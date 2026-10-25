---
type: task
title: "Build a streaming gate that fails closed"
minutes: 20
---

## Set up

Set up creates `/root/mastery/035-gate`: a small `app/price.py` with a passing `unittest` suite.

```bash
rm -rf /root/mastery/035-gate && mkdir -p /root/mastery/035-gate/app /root/mastery/035-gate/tests && cd /root/mastery/035-gate
cat > app/__init__.py <<'EOF'

EOF
cat > app/price.py <<'EOF'
def with_vat(cents):
    return round(cents * 1.25)
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_price.py <<'EOF'
import unittest
from app.price import with_vat


class T(unittest.TestCase):
    def test_vat(self):
        self.assertEqual(with_vat(400), 500)

    def test_zero(self):
        self.assertEqual(with_vat(0), 0)
EOF
```

## What to build

Build the gate a merge pipeline will call: it may say **go** only when it is sure.

1. `/root/mastery/035-gate/verdict.schema.json`: an object with `verdict` (`pass` or `fail`), `failures` (integer, minimum 0), and `summary` (string), all required, no extra properties.
2. `/root/mastery/035-gate/gate.py <stream.jsonl>`: exit `0` and print `GATE PASS: <summary>` only for a stream whose last `result` event is a success with a `structured_output` that matches the schema, is consistent (`pass` exactly when `failures` is 0), and says `pass`. Every other case - including a missing file, a non-JSON line, or no `result` event - exits `1` with `GATE FAIL: <reason>`. Either way, write `gate.json` with `ok`, `reason`, and `session_id`.
3. `/root/mastery/035-gate/gate.sh`: run this headless, allowing only `Bash(python3 -m unittest *)`, at most 6 turns, with `stream-json`, `--verbose`, and your schema; save the stream with `tee stream.jsonl`, print each tool call (`-> Bash`) to stderr as it happens, then call `gate.py`:
   > Run the test suite with python3 -m unittest -q and report a verdict: pass or fail, the number of failing tests, and a one-line summary.

The checker feeds `gate.py` nine crafted streams, then runs `gate.sh` for real.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `--json-schema "$(cat verdict.schema.json)"` passes the file's contents.
- In Python, `True` is an `int` - reject booleans for `failures` explicitly.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/035-gate
cat > verdict.schema.json <<'EOF'
{
  "type": "object",
  "properties": {
    "verdict": { "type": "string", "enum": ["pass", "fail"] },
    "failures": { "type": "integer", "minimum": 0 },
    "summary": { "type": "string" }
  },
  "required": ["verdict", "failures", "summary"],
  "additionalProperties": false
}
EOF
cat > gate.py <<'EOF'
#!/usr/bin/env python3
"""gate.py <stream.jsonl> - exit 0 only for a complete run whose verdict is a clean pass. Anything else fails closed."""
import json, sys


def stop(reason, sid=None):
    json.dump({"ok": False, "reason": reason, "session_id": sid}, open("gate.json", "w"))
    print(f"GATE FAIL: {reason}", file=sys.stderr)
    sys.exit(1)


events = []
try:
    for line in open(sys.argv[1]):
        if line.strip():
            events.append(json.loads(line))
except (OSError, IndexError, ValueError) as e:
    stop(f"unreadable stream ({e})")
res = [e for e in events if e.get("type") == "result"]
if not res:
    stop("no result event - the run did not finish")
r = res[-1]
sid = r.get("session_id")
if r.get("is_error") or r.get("subtype") != "success":
    stop(f"run failed: {r.get('subtype')}", sid)
out = r.get("structured_output")
if not isinstance(out, dict):
    stop("no structured_output", sid)
if set(out) != {"verdict", "failures", "summary"} or out["verdict"] not in ("pass", "fail") \
        or not isinstance(out["failures"], int) or isinstance(out["failures"], bool) or out["failures"] < 0 \
        or not isinstance(out["summary"], str):
    stop(f"structured_output does not match the schema: {out}", sid)
if (out["verdict"] == "pass") != (out["failures"] == 0):
    stop(f"inconsistent verdict: {out['verdict']} with {out['failures']} failures", sid)
if out["verdict"] != "pass":
    stop(f"tests failed: {out['summary']}", sid)
json.dump({"ok": True, "reason": out["summary"], "session_id": sid}, open("gate.json", "w"))
print(f"GATE PASS: {out['summary']}")
EOF
cat > gate.sh <<'EOF'
#!/usr/bin/env bash
# gate.sh - run the agent, stream its events to stream.jsonl, and let gate.py decide.
set -uo pipefail
cd "$(dirname "$0")"
claude -p "Run the test suite with python3 -m unittest -q and report a verdict: pass or fail, the number of failing tests, and a one-line summary." \
  --allowedTools "Bash(python3 -m unittest *)" --max-turns 6 \
  --output-format stream-json --verbose --json-schema "$(cat verdict.schema.json)" < /dev/null \
  | tee stream.jsonl \
  | jq --unbuffered -r 'select(.type == "assistant") | .message.content[]? | select(.type == "tool_use") | "-> \(.name)"' >&2
python3 gate.py stream.jsonl
EOF
chmod +x gate.sh gate.py
./gate.sh; echo "gate exit $?"
cat gate.json
```

</details>

## Check your work

```bash
D=/root/mastery/035-gate; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
STREAMS = {'complete clean pass': ([{'type': 'system', 'subtype': 'init', 'session_id': 's-1'}, {'type': 'result', 'subtype': 'success', 'is_error': False, 'session_id': 's-1', 'structured_output': {'verdict': 'pass', 'failures': 0, 'summary': '2 tests passed'}}], 0), 'stream cut off before the result event': ([{'type': 'system', 'subtype': 'init', 'session_id': 's-1'}, {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'All tests pass!'}]}}], 1), 'success without structured_output': ([{'type': 'system', 'subtype': 'init', 'session_id': 's-1'}, {'type': 'result', 'subtype': 'success', 'is_error': False, 'session_id': 's-1', 'result': 'All good'}], 1), 'pass with 2 failures (inconsistent)': ([{'type': 'system', 'subtype': 'init', 'session_id': 's-1'}, {'type': 'result', 'subtype': 'success', 'is_error': False, 'session_id': 's-1', 'structured_output': {'verdict': 'pass', 'failures': 2, 'summary': 'x'}}], 1), 'error_max_turns': ([{'type': 'system', 'subtype': 'init', 'session_id': 's-1'}, {'type': 'result', 'subtype': 'error_max_turns', 'is_error': True, 'session_id': 's-1'}], 1), 'verdict fail': ([{'type': 'system', 'subtype': 'init', 'session_id': 's-1'}, {'type': 'result', 'subtype': 'success', 'is_error': False, 'session_id': 's-1', 'structured_output': {'verdict': 'fail', 'failures': 1, 'summary': 'test_vat failed'}}], 1), 'extra field': ([{'type': 'system', 'subtype': 'init', 'session_id': 's-1'}, {'type': 'result', 'subtype': 'success', 'is_error': False, 'session_id': 's-1', 'structured_output': {'verdict': 'pass', 'failures': 0, 'summary': '2 tests passed', 'shipit': True}}], 1)}

sc = load("verdict.schema.json") or {}
props = sc.get("properties") or {}
ok(set(sc.get("required") or []) == {"verdict", "failures", "summary"} and (props.get("verdict") or {}).get("enum") == ["pass", "fail"]
   and (props.get("failures") or {}).get("type") == "integer" and sc.get("additionalProperties") is False,
   "verdict.schema.json requires verdict (pass|fail), integer failures, and summary, with no extra fields",
   "verdict.schema.json needs required [verdict, failures, summary], verdict enum [pass, fail], failures integer, additionalProperties false")
t = tempfile.mkdtemp()
for name, (evs, want) in STREAMS.items():
    p = os.path.join(t, "s.jsonl")
    Path(p).write_text("\n".join(json.dumps(e) for e in evs) + "\n")
    rc, out, err = sh(["python3", os.path.abspath("gate.py"), p], cwd=t)
    g = load(os.path.join(t, "gate.json")) or {}
    ok(rc == want and g.get("ok") is (want == 0), f"{name} -> exit {want}", f"gate.py on a stream with {name} should exit {want} and write gate.json ok={want == 0} - got exit {rc}, gate.json {g}")
p = os.path.join(t, "bad.jsonl")
Path(p).write_text('{"type":"system"}\nnot json\n' + json.dumps(STREAMS["complete clean pass"][0][1]) + "\n")
rc, out, err = sh(["python3", os.path.abspath("gate.py"), p], cwd=t)
ok(rc == 1, "a stream with a corrupt line -> exit 1", f"any line that is not JSON must fail the gate - got exit {rc}")
rc, out, err = sh(["python3", os.path.abspath("gate.py"), os.path.join(t, "missing.jsonl")], cwd=t)
ok(rc == 1, "a missing stream file -> exit 1", f"a missing file must fail the gate - got exit {rc}")
rc, out, err = sh("./gate.sh", timeout=300)
evs = events("stream.jsonl")
r = [e for e in evs if e.get("type") == "result"]
ok(rc == 0 and r and (r[-1].get("structured_output") or {}).get("verdict") == "pass" and (load("gate.json") or {}).get("ok") is True,
   "gate.sh streamed a real run to stream.jsonl and passed it", f"./gate.sh should exit 0 after a real streamed run with a pass verdict - got exit {rc} {err.strip()[-200:]}")
ok(any(e.get("type") == "system" and e.get("subtype") == "init" for e in evs) and "-> Bash" in err, "the stream has the init event and gate.sh showed tool calls live",
   "save the full stream with tee and print each tool_use name (-> Bash) as it happens")
PYEOF
```

## What you learned

- stream-json in print mode needs --verbose; the result event is the only proof a run finished.
- --json-schema puts a validated object in structured_output, which can still be missing on a successful run.
- A gate fails closed: any missing, malformed, or contradictory piece means stop.
