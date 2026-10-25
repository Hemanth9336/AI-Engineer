---
type: task
title: "Output formats and piping"
minutes: 7
---

## Scenario

`-p` has three output formats. **text** (the default) is just the answer. **json** is one object with the answer in `.result` plus `num_turns`, `total_cost_usd`, `is_error`, `session_id` and `permission_denials` - ideal for scripts. **stream-json** (needs `--verbose`) prints one JSON event per line as the run happens: the `system` init event (model, tools), each `assistant` and `user` message, and a final `result`.

Claude also reads **standard input**: whatever you pipe in is added to the prompt.

## Set up

Same folder: `/root/cc-lab/04-headless`, with `server.log`.

```bash
mkdir -p /root/cc-lab/04-headless && cd /root/cc-lab/04-headless
cat > server.log <<'EOF'
2026-10-20T09:00:01 INFO  api started on :8080
2026-10-20T09:00:07 INFO  GET /health 200
2026-10-20T09:01:13 ERROR E101 payment gateway timeout
2026-10-20T09:01:15 WARN  retrying payment request
2026-10-20T09:02:40 ERROR E204 invalid card number
2026-10-20T09:03:02 INFO  GET /orders 200
2026-10-20T09:04:55 ERROR E101 payment gateway timeout
2026-10-20T09:05:10 WARN  slow query on orders (2300 ms)
2026-10-20T09:06:31 ERROR E330 inventory service unreachable
2026-10-20T09:07:00 INFO  GET /health 200
EOF
claude --version
```

## What to build

Run these in `/root/cc-lab/04-headless` and look at each output:

```bash
cd /root/cc-lab/04-headless
claude -p "In one sentence, what went wrong in server.log?" --output-format json > run.json
jq -r '.result' run.json > summary.txt
jq '{num_turns, total_cost_usd, is_error}' run.json
grep ERROR server.log | claude -p "List each distinct error code (like E101) in these log lines, sorted, one per line, nothing else." > codes.txt
claude -p "Say hello to the lab" --output-format stream-json --verbose > stream.jsonl
jq -r 'select(.type == "system") | .model' stream.jsonl
```

Afterwards you should have `run.json`, `summary.txt` (exactly the `.result` text), `codes.txt` (one code per line) and `stream.jsonl`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq -r '.result'` prints the answer without JSON quotes.
- In `grep ERROR server.log | claude -p "..."` Claude sees only the four ERROR lines.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/04-headless
claude -p "In one sentence, what went wrong in server.log?" --output-format json > run.json
jq -r '.result' run.json > summary.txt
jq '{num_turns, total_cost_usd, is_error}' run.json
grep ERROR server.log | claude -p "List each distinct error code (like E101) in these log lines, sorted, one per line, nothing else." > codes.txt
claude -p "Say hello to the lab" --output-format stream-json --verbose > stream.jsonl
jq -r 'select(.type == "system") | .model' stream.jsonl
```

</details>

## Check your work

```bash
D=/root/cc-lab/04-headless; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
run = load("run.json") or {}
ok(run.get("type") == "result" and run.get("is_error") is False and run.get("result"), "run.json is a successful JSON result", "run.json should hold the output of claude -p ... --output-format json")
ok(run.get("result") and text("summary.txt").strip() == run["result"].strip(), "summary.txt is exactly .result from run.json", "summary.txt should be jq -r '.result' run.json")
codes = [l.strip() for l in text("codes.txt").splitlines() if l.strip()]
ok(codes == ["E101", "E204", "E330"], "codes.txt lists E101, E204, E330 - one per line", f"codes.txt should be the distinct codes from the ERROR lines, sorted, one per line - got {codes}")
ok(ran(r"E204 invalid card number"), "the piped ERROR lines reached Claude (stdin became part of the prompt)", "no session here received the ERROR lines on stdin - pipe grep ERROR server.log into claude -p")
ev = events("stream.jsonl")
ok(init(ev).get("model") and result(ev).get("type") == "result", "stream.jsonl has the init event (with the model) and the final result event", "stream.jsonl should hold claude -p ... --output-format stream-json --verbose")
PYEOF
```

## What you learned

- `--output-format json` gives scripts the answer plus turns, cost, errors and denials.
- `stream-json --verbose` is a live, line-by-line transcript of the run.
- Piped stdin becomes part of the prompt, so Claude slots into a shell pipeline.
