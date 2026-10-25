---
type: task
title: "Build the parameterized flow"
minutes: 30
---

## Set up

Set up creates `/root/mastery/062-blurb` with one change list, `changes/2.4.0.txt`.

```bash
rm -rf /root/mastery/062-blurb && mkdir -p /root/mastery/062-blurb/changes && cd /root/mastery/062-blurb
cat > changes/2.4.0.txt <<'EOF'
- Export invoices as PDF
- Fix: totals rounded wrongly for JPY
- Faster dashboard load (about 40%)
EOF
jq --version
```

## What to build

1. Write `blurb.sh CHANGES_FILE`. It turns a change list into a release announcement of at most 280 characters.
   - **Input.** A missing or empty file exits 2 without calling `claude`. The output name is the file's base name without `.txt`.
   - **Agent step.** Run `claude -p` with `--tools ""`, `--max-turns 1`, `--output-format json`, and the file on stdin. Save the raw envelope to `work/<name>.envelope.json`.
   - **Reading the answer.**
     - Exit 3 unless the envelope parses and has `is_error: false` and `subtype: "success"`.
     - Exit 3 if `.result` is empty or longer than 280 characters.
   - **Outputs.** Write `out/<name>.md` (the announcement) and `out/<name>.meta.json` (`version`, `session_id`, `total_cost_usd`, `duration_ms`, `num_turns`).
2. Run `./blurb.sh changes/2.4.0.txt`.

The checker runs a copy of your script on a new input file, and against fake `claude` binaries that return error envelopes, plain text, and an over-long answer.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq -e` sets its exit status from the result. `jq -e '.is_error == false and .subtype == "success"' f > /dev/null 2>&1` fails on unparsable files too.
- `${#var}` is the length of a shell variable in characters.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/062-blurb
cat > blurb.sh <<'EOF'
#!/usr/bin/env bash
# blurb.sh CHANGES_FILE - write a short release announcement to out/<name>.md plus out/<name>.meta.json.
# Exit 0 ok, 2 bad input, 3 the agent step failed or returned something unusable.
set -uo pipefail
cd "$(dirname "$0")"
file=${1:?usage: blurb.sh CHANGES_FILE}
[ -s "$file" ] || { echo "not found or empty: $file" >&2; exit 2; }
name=$(basename "$file" .txt)
mkdir -p work out
env_file="work/$name.envelope.json"

prompt="Write a release announcement for version $name from the change list on stdin. \
One paragraph, at most 280 characters, plain text, no headings. Output only the announcement."
rc=0
claude -p "$prompt" --tools "" --max-turns 1 --output-format json < "$file" > "$env_file" 2> "work/$name.err" || rc=$?

if ! jq -e '.is_error == false and .subtype == "success"' "$env_file" > /dev/null 2>&1; then
  echo "agent step failed (exit $rc): $(jq -r '(.errors // []) | join("; ")' "$env_file" 2> /dev/null || echo unreadable envelope)" >&2
  exit 3
fi
blurb=$(jq -r '.result // ""' "$env_file")
if [ -z "$blurb" ] || [ "${#blurb}" -gt 280 ]; then
  echo "unusable blurb (${#blurb} characters)" >&2
  exit 3
fi

printf '%s\n' "$blurb" > "out/$name.md"
jq --arg v "$name" '{version: $v, session_id, total_cost_usd, duration_ms, num_turns}' "$env_file" > "out/$name.meta.json"
echo "out/$name.md"
EOF
chmod +x blurb.sh
./blurb.sh changes/2.4.0.txt
cat out/2.4.0.md out/2.4.0.meta.json
```

</details>

## Check your work

```bash
D=/root/mastery/062-blurb; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
HIDDEN = '- Dark mode for the whole app\n- Fix: login loop on Safari\n'

import shutil
b = text("out/2.4.0.md").strip()
ok("PDF" in b and len(b) <= 280, "out/2.4.0.md holds the announcement from the envelope's .result", f"run ./blurb.sh changes/2.4.0.txt - out/2.4.0.md: {b[:80]!r}")
meta = load("out/2.4.0.meta.json") or {}
envl = load("work/2.4.0.envelope.json") or {}
ok(meta.get("version") == "2.4.0" and meta.get("session_id") == envl.get("session_id") and envl.get("session_id")
   and meta.get("total_cost_usd") == envl.get("total_cost_usd") and isinstance(meta.get("duration_ms"), int) and isinstance(meta.get("num_turns"), int),
   "out/2.4.0.meta.json copies version, session_id, cost, duration, and turns from work/2.4.0.envelope.json",
   f"keep the raw envelope in work/ and write {{version, session_id, total_cost_usd, duration_ms, num_turns}} - got {meta}")
def copy(t):
    shutil.copy("blurb.sh", t)
    Path(t, "changes").mkdir()
    Path(t, "changes/2.5.0.txt").write_text(HIDDEN)
with tempfile.TemporaryDirectory() as t:
    copy(t)
    rc, so_, se = sh(["./blurb.sh", "changes/2.5.0.txt"], cwd=t, timeout=180)
    ok(rc == 0 and "dark mode" in text(Path(t, "out/2.5.0.md")) and (load(Path(t, "out/2.5.0.meta.json")) or {}).get("version") == "2.5.0",
       "a new input file gets its own out/2.5.0.md and meta file", f"name outputs after the input file - rc {rc}: {se.strip()[-150:]}")
    env = stub(t, f"touch {t}/CALLED; exit 0")
    rc2, _, _ = sh(["./blurb.sh", "changes/missing.txt"], cwd=t, env=env)
    Path(t, "changes/empty.txt").write_text("")
    rc3, _, _ = sh(["./blurb.sh", "changes/empty.txt"], cwd=t, env=env)
    ok(rc2 == 2 and rc3 == 2 and not Path(t, "CALLED").exists(), "missing and empty inputs exit 2 without calling claude", f"validate the input first - rc {rc2}, {rc3}")
    cases = {
        "is_error true with exit 0": 'echo \'{"type":"result","subtype":"error_during_execution","is_error":true,"result":"","errors":["boom"],"session_id":"s"}\'; exit 0',
        "max turns": 'echo \'{"type":"result","subtype":"error_max_turns","is_error":true,"errors":["Reached maximum number of turns (1)"],"session_id":"s"}\'; exit 1',
        "plain text instead of JSON": "echo 'Version 2.5.0 is great'; exit 0",
        "an over-long result": 'python3 -c \'import json; print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"x" * 400,"session_id":"s"}))\'',
    }
    bad = {}
    for name, body in cases.items():
        shutil.rmtree(Path(t, "out"), ignore_errors=True)
        rc, _, _ = sh(["./blurb.sh", "changes/2.5.0.txt"], cwd=t, env=stub(t, body))
        if rc != 3 or Path(t, "out/2.5.0.md").exists():
            bad[name] = rc
    ok(not bad, "every unusable envelope exits 3 and writes no output (is_error, max turns, plain text, too long)", f"read .is_error and .subtype, and check the result's length - failed cases {bad}")
PYEOF
```

## What you learned

- Validate input before spending a model call, and give bad input its own exit code (2).
- The JSON envelope says whether the run worked (is_error, subtype); plain text can't.
- Name outputs after the input and keep the raw envelope, so every artefact traces back to a session and a cost.
