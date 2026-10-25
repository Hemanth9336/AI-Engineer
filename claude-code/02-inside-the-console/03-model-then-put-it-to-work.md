---
type: task
title: "/model, then put it to work"
minutes: 10
---

## Set up

Same project as the previous task, in `/root/cc-lab/02-console`.

```bash
mkdir -p /root/cc-lab/02-console && cd /root/cc-lab/02-console
cat > tasks.py <<'EOF'
"""tasklog - a tiny to-do list kept in tasks.json.

Usage: python3 tasks.py add TEXT | list | done N
"""
import json
import os
import sys

FILE = os.environ.get("TASKS_FILE", "tasks.json")


def load():
    try:
        with open(FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save(tasks):
    with open(FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd, args = argv[0], argv[1:]
    tasks = load()
    if cmd == "add":
        tasks.append({"text": " ".join(args), "done": False})
        save(tasks)
        print(f"added #{len(tasks)}")
    elif cmd == "list":
        for i, t in enumerate(tasks, 1):
            print(f"{i}. [{'x' if t['done'] else ' '}] {t['text']}")
    elif cmd == "done":
        tasks[int(args[0]) - 1]["done"] = True
        save(tasks)
        print(f"done #{args[0]}")
    else:
        print(f"unknown command: {cmd}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
EOF
cat > test_tasks.py <<'EOF'
import os
import subprocess
import sys
import tempfile
import unittest


def run(*args, file):
    env = dict(os.environ, TASKS_FILE=file)
    return subprocess.run([sys.executable, "tasks.py", *args], capture_output=True, text=True, env=env).stdout


class TasksTest(unittest.TestCase):
    def test_add_then_list(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "t.json")
            self.assertEqual(run("add", "buy", "milk", file=f).strip(), "added #1")
            self.assertEqual(run("list", file=f).strip(), "1. [ ] buy milk")

    def test_done(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "t.json")
            run("add", "a", file=f)
            run("done", "1", file=f)
            self.assertEqual(run("list", file=f).strip(), "1. [x] a")


if __name__ == "__main__":
    unittest.main()
EOF
cat > README.md <<'EOF'
# tasklog

A tiny command-line to-do list. Tasks live in `tasks.json` (set `TASKS_FILE` to use another file).

    python3 tasks.py add "write the report"
    python3 tasks.py list
    python3 tasks.py done 1

Run the tests with `python3 -m unittest -q`.
EOF
[ -f tasks.json ] || printf '[{"text": "water the plants", "done": false}]\n' > tasks.json
claude --version
```

## What to build

1. Start the console in `/root/cc-lab/02-console` and switch to the small, fast model:

```
/model haiku
```

(Or type `/model` and pick it from the list.)

2. Give it a real job:

> Add a `count` command to tasks.py that prints how many tasks are still open, like `3 open`. Keep the other commands working.

3. Approve the edit, then try it: `python3 tasks.py count` and `python3 -m unittest -q`.

Headless equivalent: `claude -p "..." --model haiku --permission-mode acceptEdits`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `/model` changes the model for the rest of the session; `--model` does the same for one `-p` run.
- A task is open when its `done` is false.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/02-console
claude -p "Add a count command to tasks.py that prints how many tasks are still open, like '3 open'. Keep the other commands working." \
  --model haiku --permission-mode acceptEdits --max-turns 8
python3 tasks.py count
python3 -m unittest -q
```

</details>

## Check your work

```bash
D=/root/cc-lab/02-console; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
hits = [rows for rows in sessions(os.getcwd()) if any("count" in p.lower() for p in prompts(rows)) and any(is_haiku(m) for m in models(rows))]
ok(hits, "a session in this folder used haiku and asked for the count command", "no session here where haiku answered a request about a count command - use /model haiku first")
with tempfile.TemporaryDirectory() as t:
    f = os.path.join(t, "t.json")
    Path(f).write_text(json.dumps([{"text": "a", "done": True}, {"text": "b", "done": False}, {"text": "c", "done": False}, {"text": "d", "done": True}, {"text": "e", "done": False}]))
    rc, out, err = sh([sys.executable, "tasks.py", "count"], env={"TASKS_FILE": f})
    ok(rc == 0 and out.strip() == "3 open", "tasks.py count prints '3 open' for a list with 3 open tasks", f"python3 tasks.py count on 5 tasks (3 open) should print '3 open' - got {(out + err).strip()[:200]!r}")
    rc, out, err = sh([sys.executable, "tasks.py", "list"], env={"TASKS_FILE": f})
    ok(out.splitlines()[:2] == ["1. [x] a", "2. [ ] b"], "list still works", f"python3 tasks.py list broke - got {out[:200]!r}")
rc, out, err = sh([sys.executable, "-m", "unittest", "-q"])
ok(rc == 0, "the existing tests still pass", "python3 -m unittest -q fails: " + err[-300:])
PYEOF
```

## What you learned

- `/model` (or `--model`) picks who answers: haiku for quick jobs, sonnet for everyday work, opus for hard problems.
- The session transcript records which model answered every turn.
- Always run the code and the tests after an agent edit.
