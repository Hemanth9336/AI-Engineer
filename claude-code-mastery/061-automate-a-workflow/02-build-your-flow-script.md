---
type: task
title: "Build your flow script"
minutes: 30
---

## Set up

Set up creates `/root/mastery/061-flow` with a day of application logs in `logs/` (INFO, WARN, and ERROR lines from three services).

```bash
rm -rf /root/mastery/061-flow && mkdir -p /root/mastery/061-flow/logs && cd /root/mastery/061-flow
cat > logs/app-1.log <<'EOF'
2026-10-24T07:58:00Z INFO payments started
2026-10-24T08:01:12Z ERROR payments TimeoutError: upstream timed out after 30s
2026-10-24T08:02:40Z ERROR auth TokenExpired: refresh token expired for client web
2026-10-24T08:05:03Z WARN search slow query 2.1s
2026-10-24T08:06:44Z ERROR payments TimeoutError: upstream timed out after 30s
2026-10-24T08:09:10Z ERROR search IndexMissing: index products-v7 not found
2026-10-24T08:11:52Z ERROR payments TimeoutError: upstream timed out after 30s
EOF
cat > logs/app-2.log <<'EOF'
2026-10-24T12:00:00Z INFO auth started
2026-10-24T12:03:21Z ERROR auth TokenExpired: refresh token expired for client ios
2026-10-24T12:04:05Z ERROR payments TimeoutError: upstream timed out after 30s
2026-10-24T12:08:30Z ERROR auth TokenExpired: refresh token expired for client web
2026-10-24T12:10:12Z ERROR search IndexMissing: index products-v7 not found
2026-10-24T12:15:47Z ERROR payments TimeoutError: upstream timed out after 30s
2026-10-24T12:20:00Z INFO payments healthy
EOF
claude --version
```

## What to build

1. Write `flow.sh [LOGDIR] [DATE]` (defaults: `logs`, today). Use `set -euo pipefail`, and work relative to the script's folder.
   - **Gather.** Count the `ERROR` lines by service and error class into `work/digest.txt`, one `count service error` line each, most frequent first. For example, `5 payments TimeoutError`.
   - **Skip.** If there are no errors, write `reports/DATE.md` with `No errors logged.` yourself and exit 0, without calling `claude`.
   - **Agent step.** Run `claude -p` with `--tools ""` and `--max-turns 1`, feeding the digest on stdin. Ask for `# Error report DATE`, then one bullet per signature: `- <count> x <service> <error>: <cause>`. Write the output to `work/draft.md`.
   - **Exit codes.** Exit non-zero if `claude` fails, and exit 2 if `LOGDIR` doesn't exist.
   - **Verify.** Check the first line, and that every top-3 digest line appears as `<count> x <service> <error>`. On failure, exit non-zero and keep the draft in `work/`.
   - **Publish.** `mv` the draft to `reports/DATE.md`.
2. Run `./flow.sh logs 2026-10-24`.

The checker runs copies of your script on a quiet day, on a day where the model writes nonsense, and with a `claude` that crashes.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `grep` exits 1 when nothing matches, and `pipefail` turns that into a failure. Wrap it: `{ grep ... || true; } | awk ...`.
- `while read -r count service error; do ...; done < <(head -3 work/digest.txt)` walks the top three lines.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/061-flow
cat > flow.sh <<'EOF'
#!/usr/bin/env bash
# flow.sh [LOGDIR] [DATE] - turn a day of error logs into reports/DATE.md, or exit non-zero and leave reports/ alone.
set -euo pipefail
cd "$(dirname "$0")"
logdir=${1:-logs}
day=${2:-$(date +%F)}
[ -d "$logdir" ] || { echo "no log dir: $logdir" >&2; exit 2; }
mkdir -p work reports

# gather: count ERROR lines by "service error", most frequent first
{ grep -h ' ERROR ' "$logdir"/*.log 2> /dev/null || true; } | awk '{sub(/:$/, "", $4); print $3, $4}' \
  | sort | uniq -c | sort -k1,1nr -k2 > work/digest.txt

# skip: nothing to report means no model call
if [ ! -s work/digest.txt ]; then
  printf '# Error report %s\n\nNo errors logged.\n' "$day" > "reports/$day.md"
  echo "reports/$day.md (no errors)"
  exit 0
fi

# agent step: text only, input on stdin
prompt="Write the daily error report for $day from the error digest on stdin (columns: count, service, error). \
Start with the line '# Error report $day'. Then one bullet per signature, most frequent first, \
formatted '- <count> x <service> <error>: <one-line likely cause>'. Output only the report."
if ! claude -p "$prompt" --tools "" --max-turns 1 < work/digest.txt > work/draft.md 2> work/claude.err; then
  echo "claude failed; see work/claude.err" >&2
  exit 1
fi

# verify: the heading, and every top-3 signature with its count
fail=0
[ "$(head -1 work/draft.md)" = "# Error report $day" ] || { echo "draft: first line is not '# Error report $day'" >&2; fail=1; }
while read -r count service error; do
  grep -qF -- "$count x $service $error" work/draft.md || { echo "draft: missing '$count x $service $error'" >&2; fail=1; }
done < <(head -3 work/digest.txt)
[ "$fail" = 0 ] || { echo "draft failed verification; kept in work/draft.md" >&2; exit 1; }

# publish
mv work/draft.md "reports/$day.md"
echo "reports/$day.md"
EOF
chmod +x flow.sh
./flow.sh logs 2026-10-24
cat reports/2026-10-24.md
```

</details>

## Check your work

```bash
D=/root/mastery/061-flow; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
python3 - <<'PYEOF'
import glob, hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def text(p):
    try:
        return Path(p).read_text()
    except Exception:
        return ""
def sha(p):
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except Exception:
        return None
def sh(cmd, cwd=None, env=None, input=None, timeout=60):
    try:
        r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, cwd=cwd, input=input,
                           timeout=timeout, env=dict(os.environ, **(env or {})))
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"
def sessions(d):
    # Claude Code saves every session (console or -p) as ~/.claude/projects/<dir>/<id>.jsonl, one JSON row per event
    real, out = os.path.realpath(d), []
    for f in sorted(glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")), key=os.path.getmtime):
        rows = []
        for line in open(f, errors="replace"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
        if any(r.get("cwd") and os.path.realpath(r["cwd"]) == real for r in rows):
            out.append(rows)
    return out
def ran(pat, d=None):
    return [rows for rows in sessions(d or os.getcwd()) if any(re.search(pat, p, re.I | re.S) for p in prompts(rows))]
def content(r):
    c = (r.get("message") or {}).get("content")
    return c if isinstance(c, list) else ([{"type": "text", "text": c}] if isinstance(c, str) else [])
def prompts(rows):
    return [b.get("text", "") for r in rows if r.get("type") == "user" and not r.get("isMeta") for b in content(r) if b.get("type") == "text"]
def uses(rows):
    return [b for r in rows if r.get("type") == "assistant" for b in content(r) if b.get("type") == "tool_use"]
def results(rows):
    return [b for r in rows if r.get("type") == "user" for b in content(r) if b.get("type") == "tool_result"]
def models(rows):
    return {(r.get("message") or {}).get("model") for r in rows if r.get("type") == "assistant"} - {None, "<synthetic>"}
def is_haiku(m):
    return bool(m) and ("haiku" in m.lower() or m == os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL"))
def events(p):
    out = []
    for line in text(p).splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out
def init(ev):
    return next((e for e in ev if e.get("type") == "system" and e.get("subtype") == "init"), {})
def result(ev):
    return next((e for e in ev if e.get("type") == "result"), {})
def ev_uses(ev):
    return [b for e in ev if e.get("type") == "assistant" for b in content(e) if b.get("type") == "tool_use"]
def stub(t, body):
    b = Path(t, "bin"); b.mkdir(exist_ok=True)
    p = b / "claude"; p.write_text("#!/usr/bin/env bash\n" + body + "\n"); p.chmod(0o755)
    return {"PATH": f"{b}:{os.environ['PATH']}"}

import shutil
rep = text("reports/2026-10-24.md")
ok(rep.startswith("# Error report 2026-10-24") and all(s in rep for s in ["5 x payments TimeoutError", "3 x auth TokenExpired", "2 x search IndexMissing"]),
   "reports/2026-10-24.md lists the three signatures with their counts", "run ./flow.sh logs 2026-10-24 to publish reports/2026-10-24.md")
dg = text("work/digest.txt").split("\n")
ok(dg and dg[0].split() == ["5", "payments", "TimeoutError"], "work/digest.txt counts ERROR lines by service and error, most frequent first",
   f"gather into work/digest.txt as 'count service error', sorted by count - first line {dg[:1]}")
def copy(t, logs):
    shutil.copy("flow.sh", t)
    Path(t, "logs").mkdir()
    for i, body in enumerate(logs):
        Path(t, "logs", f"x-{i}.log").write_text(body)
with tempfile.TemporaryDirectory() as t:
    copy(t, ["2026-10-25T09:00:00Z INFO all quiet\n"])
    env = stub(t, f"touch {t}/CALLED; exit 0")
    rc, so_, se = sh(["./flow.sh", "logs", "2026-10-25"], cwd=t, env=env)
    r = text(Path(t, "reports/2026-10-25.md"))
    ok(rc == 0 and "No errors" in r and not Path(t, "CALLED").exists(), "a day without errors publishes 'No errors' without calling claude",
       f"skip the model when the digest is empty - rc {rc}, report {r[:60]!r}, claude called: {Path(t, 'CALLED').exists()}")
with tempfile.TemporaryDirectory() as t:
    copy(t, ["".join(f"2026-10-25T09:0{i}:00Z ERROR search DiskFullError: no space left on device\n" for i in range(4))])
    Path(t, "reports").mkdir(); Path(t, "reports/2026-10-25.md").write_text("previous good report\n")
    rc, so_, se = sh(["./flow.sh", "logs", "2026-10-25"], cwd=t, timeout=180)
    ok(rc != 0 and text(Path(t, "reports/2026-10-25.md")) == "previous good report\n" and Path(t, "work/draft.md").exists(),
       "a garbage draft fails verification: non-zero exit, the old report stays, the draft is kept", f"verify the draft against the digest before mv - rc {rc}: {se.strip()[-200:]}")
with tempfile.TemporaryDirectory() as t:
    copy(t, ['2026-10-24T07:58:00Z INFO payments started\n2026-10-24T08:01:12Z ERROR payments TimeoutError: upstream timed out after 30s\n2026-10-24T08:02:40Z ERROR auth TokenExpired: refresh token expired for client web\n2026-10-24T08:05:03Z WARN search slow query 2.1s\n2026-10-24T08:06:44Z ERROR payments TimeoutError: upstream timed out after 30s\n2026-10-24T08:09:10Z ERROR search IndexMissing: index products-v7 not found\n2026-10-24T08:11:52Z ERROR payments TimeoutError: upstream timed out after 30s\n'])
    env = stub(t, "echo 'API Error: 529 overloaded' >&2; exit 1")
    rc, so_, se = sh(["./flow.sh", "logs", "2026-10-26"], cwd=t, env=env)
    ok(rc != 0 and not Path(t, "reports/2026-10-26.md").exists(), "when claude itself fails, flow.sh exits non-zero and publishes nothing",
       f"check claude's exit status - rc {rc}, report exists: {Path(t, 'reports/2026-10-26.md').exists()}")
    rc, so_, se = sh(["./flow.sh", "no-such-dir"], cwd=t, env=env)
    ok(rc == 2, "a missing log directory exits 2", f"exit 2 when LOGDIR doesn't exist - rc {rc}")
PYEOF
```

## What you learned

- Deterministic code gathers, verifies, and publishes; the agent only does the part that needs judgment.
- Verify the agent's output against facts you computed yourself, and publish with mv only after it passes.
- Skip the model when there's nothing to do, and fail loudly (non-zero, stderr) when anything is off.
