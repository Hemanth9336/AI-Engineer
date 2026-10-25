---
type: task
title: "Define a subagent"
minutes: 10
---

## Set up

Set up creates `/root/cc-lab/13-subagents`: a small `calc` module and three tests. One of them fails.

```bash
mkdir -p /root/cc-lab/13-subagents/tests /root/cc-lab/13-subagents/runs && cd /root/cc-lab/13-subagents
cat > calc.py <<'EOF'
def add(a, b):
    return a + b


def percent(part, whole):
    """part as a percentage of whole, rounded to 1 decimal place."""
    return round(part / whole * 100)
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_calc.py <<'EOF'
import unittest

from calc import add, percent


class CalcTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_percent(self):
        self.assertEqual(percent(1, 8), 12.5)

    def test_percent_whole(self):
        self.assertEqual(percent(5, 5), 100.0)


if __name__ == "__main__":
    unittest.main()
EOF
claude --version
```

## What to build

1. Create `/root/cc-lab/13-subagents/.claude/agents/test-runner.md`:
   - front matter: `name: test-runner`, a `description` that says when to use it, `tools: Bash, Read` (no editing tools), `model: haiku`;
   - a body telling it to run `python3 -m unittest discover -s tests -v` and report the number run, the number failed, and each failure's test name and assertion message - and never to edit files.
2. Ask the main session to delegate, and save the event stream and the report:

```bash
cd /root/cc-lab/13-subagents
claude -p "Use the test-runner subagent to run the tests and tell me which test fails and why. Don't fix anything." \
  --allowedTools "Bash(python3 -m unittest:*)" --max-turns 6 --output-format stream-json --verbose > runs/delegate.jsonl
jq -r 'select(.type == "result") | .result' runs/delegate.jsonl > report.txt
cat report.txt
```

3. In `runs/delegate.jsonl`, find the `Agent` (or `Task`) tool call with `"subagent_type": "test-runner"` - that's the hand-off.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The `init` event in the stream lists every agent Claude can use - check that `test-runner` is there.
- `--allowedTools` applies to subagents too, so the test command is allowed.

</details>

<details><summary>Solution</summary>

```bash
mkdir -p /root/cc-lab/13-subagents/.claude/agents && cd /root/cc-lab/13-subagents
cat > .claude/agents/test-runner.md <<'EOF'
---
name: test-runner
description: Runs the project's unit tests and reports which tests fail and why. Use when asked to run or check the tests.
tools: Bash, Read
model: haiku
---
You run tests and report back. You never edit files.

1. Run `python3 -m unittest discover -s tests -v`.
2. Report: how many tests ran, how many failed, and for each failure the test name and the assertion message.

Keep the report short - the main conversation only needs the result, not the full output.
EOF
cd /root/cc-lab/13-subagents
claude -p "Use the test-runner subagent to run the tests and tell me which test fails and why. Don't fix anything." \
  --allowedTools "Bash(python3 -m unittest:*)" --max-turns 6 --output-format stream-json --verbose > runs/delegate.jsonl
jq -r 'select(.type == "result") | .result' runs/delegate.jsonl > report.txt
cat report.txt
```

</details>

## Check your work

```bash
D=/root/cc-lab/13-subagents; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
src = text(".claude/agents/test-runner.md")
m = re.match(r"^---\n(.*?)\n---\n(.*)$", src, re.S)
fm = dict((k.strip(), v.strip()) for k, v in (l.split(":", 1) for l in (m.group(1).splitlines() if m else []) if ":" in l))
ok(m, ".claude/agents/test-runner.md exists with front matter", "create .claude/agents/test-runner.md with a --- front matter block")
ok(fm.get("name") == "test-runner" and len(fm.get("description", "")) > 15, "name is test-runner and the description says when to use it", f"set name: test-runner and a real description - got {fm}")
tools = [t.strip() for t in fm.get("tools", "").split(",") if t.strip()]
ok("Bash" in tools and not set(tools) & {"Write", "Edit", "MultiEdit", "NotebookEdit"}, f"tools are limited to {tools} - it can run tests but not edit", "tools: should include Bash and no editing tools (Write, Edit)")
ok(fm.get("model") == "haiku", "it runs on haiku", "set model: haiku")
ok(m and "unittest" in m.group(2), "the instructions say how to run the tests", "tell the subagent to run python3 -m unittest discover -s tests -v")
ev = events("runs/delegate.jsonl")
ok("test-runner" in (init(ev).get("agents") or []), "Claude Code loaded the test-runner agent", "runs/delegate.jsonl should list test-runner in the init event's agents - is the file in .claude/agents/?")
hand = [u for u in ev_uses(ev) if u.get("name") in ("Agent", "Task") and u["input"].get("subagent_type") == "test-runner"]
ok(hand, "the main session handed the job to the test-runner subagent", "no Agent/Task call with subagent_type test-runner in runs/delegate.jsonl")
ok("test_percent" in text("report.txt"), "report.txt names the failing test (test_percent)", "report.txt should be the run's result and name test_percent")
ok(text("calc.py") == 'def add(a, b):\n    return a + b\n\n\ndef percent(part, whole):\n    """part as a percentage of whole, rounded to 1 decimal place."""\n    return round(part / whole * 100)\n', "calc.py is untouched - nobody fixed anything", "calc.py changed - the subagent must only report")
PYEOF
```

## What you learned

- A subagent works in its own context and returns only its report.
- `tools` limits what it can do; `description` tells Claude when to use it.
- The hand-off is an `Agent` tool call with `subagent_type` - visible in the stream.
