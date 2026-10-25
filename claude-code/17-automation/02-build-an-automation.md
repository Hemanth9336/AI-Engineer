---
type: task
title: "Build an automation"
minutes: 12
---

## Set up

Set up creates `/root/cc-lab/17-automation` with a git repository, `repo/`, that has three fresh commits.

```bash
mkdir -p /root/cc-lab/17-automation/repo && cd /root/cc-lab/17-automation
if [ ! -d repo/.git ]; then
git -C repo init -q && git -C repo symbolic-ref HEAD refs/heads/main
git -C repo config user.name "Priya Shah" && git -C repo config user.email "priya@example.com"
echo "limit = 100/min" > repo/limits.txt && git -C repo add . && git -C repo commit -qm "feat: add rate limiter to the public API"
echo "retries = 5" > repo/webhooks.txt && git -C repo add . && git -C repo commit -qm "fix: retry failed webhook deliveries"
echo "1. run tests 2. tag 3. deploy" > repo/DEPLOY.md && git -C repo add . && git -C repo commit -qm "docs: explain the deploy checklist"
fi
git -C repo log --oneline
claude --version
```

## What to build

1. Write `/root/cc-lab/17-automation/digest.sh` (executable), used as `./digest.sh REPO_DIR`:
   - `set -euo pipefail`; without an argument it must fail;
   - collect the last 24 hours of commits: `git -C "$REPO" log --since='24 hours ago' --pretty='- %s (%an)'`;
   - **no commits:** append `<timestamp> skipped` to `reports/run.log` (next to the script), exit 0, and don't call Claude;
   - otherwise pipe the commits into `claude -p "Summarize these commits for a team update: at most 3 bullets, plain text." --max-turns 2 --output-format json`;
   - if `claude` exits non-zero **or** `.is_error` isn't `false`: append `<timestamp> failed`, exit 1, and leave any existing digest alone;
   - on success: write `.result` to `reports/digest-YYYY-MM-DD.md` (today's date) and append `<timestamp> ok`.
2. Write `/root/cc-lab/17-automation/cron.txt`: one crontab line that runs it at 08:00 on weekdays, with absolute paths, appending output to `reports/cron.log`.
3. Run it for real:

```bash
cd /root/cc-lab/17-automation
chmod +x digest.sh
./digest.sh repo
cat reports/digest-$(date +%F).md
tail -n 3 reports/run.log
cat cron.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `here="$(cd "$(dirname "$0")" && pwd)"` gives the script's own folder, so reports land next to it wherever cron starts it.
- `if ! out="$(... | claude -p ...)"; then` catches a failing claude even under `set -e`.
- The checker runs your script against fake `claude` commands that succeed, fail, and report errors.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/17-automation
cat > digest.sh <<'EOF'
#!/usr/bin/env bash
# Usage: ./digest.sh REPO_DIR
# Summarize the last 24 hours of commits in REPO_DIR into reports/digest-YYYY-MM-DD.md (next to this script).
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
repo="${1:?usage: digest.sh REPO_DIR}"
mkdir -p "$here/reports"
log() { echo "$(date +%FT%T) $1" >> "$here/reports/run.log"; }

commits="$(git -C "$repo" log --since='24 hours ago' --pretty='- %s (%an)')"
if [ -z "$commits" ]; then
  log skipped
  exit 0
fi

if ! out="$(printf '%s\n' "$commits" | claude -p "Summarize these commits for a team update: at most 3 bullets, plain text." \
      --max-turns 2 --output-format json)"; then
  log failed
  exit 1
fi
if [ "$(jq -r '.is_error' <<<"$out")" != "false" ]; then
  log failed
  exit 1
fi

jq -r '.result' <<<"$out" > "$here/reports/digest-$(date +%F).md"
log ok
EOF
cat > cron.txt <<'EOF'
0 8 * * 1-5 /root/cc-lab/17-automation/digest.sh /root/cc-lab/17-automation/repo >> /root/cc-lab/17-automation/reports/cron.log 2>&1
EOF
cd /root/cc-lab/17-automation
chmod +x digest.sh
./digest.sh repo
cat reports/digest-$(date +%F).md
tail -n 3 reports/run.log
cat cron.txt
```

</details>

## Check your work

```bash
D=/root/cc-lab/17-automation; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
import datetime, shutil, stat
src = text("digest.sh")
ok(src and os.access("digest.sh", os.X_OK), "digest.sh exists and is executable", "create digest.sh and chmod +x it")
ok("--max-turns" in src and "claude -p" in src and "set -euo pipefail" in src, "digest.sh uses set -euo pipefail, claude -p and --max-turns", "digest.sh needs set -euo pipefail and a claude -p call with --max-turns")
today = datetime.date.today().isoformat()
repo = os.path.abspath("repo")
with tempfile.TemporaryDirectory() as t:
    work, stubs = os.path.join(t, "work"), os.path.join(t, "bin")
    os.makedirs(work); os.makedirs(stubs)
    shutil.copy("digest.sh", work)
    script = os.path.join(work, "digest.sh")
    os.chmod(script, 0o755)
    def stub(body):
        p = os.path.join(stubs, "claude")
        Path(p).write_text("#!/usr/bin/env bash\ntouch " + t + "/called\ncat > " + t + "/stdin.txt\necho \"$@\" > " + t + "/args.txt\n" + body + "\n")
        os.chmod(p, 0o755)
        Path(t, "called").unlink(missing_ok=True)
    def go(*args):
        return sh([script, *args], env={"PATH": stubs + ":" + os.environ["PATH"]})
    def last():
        lines = text(os.path.join(work, "reports", "run.log")).splitlines()
        return lines[-1] if lines else ""
    digest = os.path.join(work, "reports", f"digest-{today}.md")
    stub("echo '{\"type\":\"result\",\"is_error\":false,\"result\":\"STUB SUMMARY\"}'")
    rc, out, err = go(repo)
    ok(rc == 0 and text(digest).strip() == "STUB SUMMARY" and last().endswith(" ok"), "success: digest-<today>.md holds .result and run.log gets 'ok'", f"with a succeeding claude: exit {rc}, digest {text(digest)[:60]!r}, last log {last()!r} {err[-200:]}")
    ok("rate limiter" in text(os.path.join(t, "stdin.txt")) and "--output-format json" in text(os.path.join(t, "args.txt")).replace("--output-format=json", "--output-format json"), "the commits are piped in on stdin and JSON output is requested", "pipe the commit list into claude -p on stdin and pass --output-format json")
    stub("exit 1")
    rc, out, err = go(repo)
    ok(rc != 0 and last().endswith(" failed") and text(digest).strip() == "STUB SUMMARY", "claude failing: exit non-zero, 'failed' logged, old digest kept", f"with claude exiting 1: exit {rc}, last log {last()!r}, digest {text(digest)[:40]!r}")
    stub("echo '{\"type\":\"result\",\"is_error\":true,\"result\":\"boom\"}'")
    rc, out, err = go(repo)
    ok(rc != 0 and last().endswith(" failed") and "boom" not in text(digest), "claude reporting is_error: treated as a failure", f"with is_error true: exit {rc}, last log {last()!r}")
    old = os.path.join(t, "old")
    os.makedirs(old)
    env = {"GIT_AUTHOR_DATE": "2020-01-01T10:00:00", "GIT_COMMITTER_DATE": "2020-01-01T10:00:00"}
    sh("git init -q && git -c user.name=x -c user.email=x@example.com commit -q --allow-empty -m 'ancient'", cwd=old, env=env)
    stub("echo '{\"type\":\"result\",\"is_error\":false,\"result\":\"x\"}'")
    rc, out, err = go(old)
    ok(rc == 0 and last().endswith(" skipped") and not Path(t, "called").exists(), "no recent commits: 'skipped', exit 0, Claude not called", f"for a repo with only old commits: exit {rc}, last log {last()!r}, claude called: {Path(t, 'called').exists()}")
    rc, out, err = go()
    ok(rc != 0, "no argument: the script fails", "./digest.sh with no argument should exit non-zero")
reports = sorted(Path("reports").glob("digest-*.md"))
ok(reports and reports[-1].read_text().strip() and " ok" in text("reports/run.log"), f"the real run wrote {reports[-1] if reports else 'a digest'} and logged ok", "run ./digest.sh repo for real - reports/digest-<date>.md and an 'ok' line in reports/run.log are missing")
cron = [l for l in text("cron.txt").splitlines() if l.strip() and not l.startswith("#")]
f = cron[0].split() if cron else []
ok(len(cron) == 1 and len(f) >= 7 and all(re.fullmatch(r"[\d*/,-]+", x) for x in f[:5]) and os.path.realpath(f[5]) == os.path.realpath("digest.sh") and os.path.realpath(f[6]) == os.path.realpath(repo), "cron.txt is one crontab line running digest.sh with absolute paths", f"cron.txt should be one line like '0 8 * * 1-5 /root/cc-lab/17-automation/digest.sh /root/cc-lab/17-automation/repo >> ...' - got {cron}")
ok(f[:5] == ["0", "8", "*", "*", "1-5"] if len(f) >= 5 else False, "it runs at 08:00 on weekdays", f"the schedule should be 0 8 * * 1-5 - got {f[:5]}")
PYEOF
```

## What you learned

- A Claude script is ordinary automation: `set -euo pipefail`, checked exit codes, a log line per run.
- Check both the exit code and `.is_error`; skip the model when there's nothing to do.
- Cron needs absolute paths - and every run should be bounded with `--max-turns`.
