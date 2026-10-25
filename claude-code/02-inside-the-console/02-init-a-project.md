---
type: task
title: "/init a project"
minutes: 10
---

## Set up

Set up creates `tasklog`, a tiny to-do CLI with tests, in `/root/cc-lab/02-console`.

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

1. Open the console in the project folder and ask Claude to write its memory file:

```bash
cd /root/cc-lab/02-console
claude
```

2. At the prompt, type `/init` and press Enter. Claude reads the project and proposes a `CLAUDE.md`. Approve the write when it asks.
3. Read what it wrote - it should name the test command and describe how `tasks.py` is laid out - then type `/exit`.

Prefer one line? `claude -p "/init" --permission-mode acceptEdits` does the same thing headless.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `/init` is typed inside the console, not in bash.
- If Claude asks whether to create `CLAUDE.md`, choose Yes.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/02-console
claude -p "/init" --permission-mode acceptEdits --max-turns 10
cat CLAUDE.md
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
md = text("CLAUDE.md")
lines = [l for l in md.splitlines() if l.strip()]
ok(len(lines) >= 5, f"CLAUDE.md exists with {len(lines)} lines", "no CLAUDE.md with at least 5 lines in /root/cc-lab/02-console - run /init and approve the write")
ok("unittest" in md, "CLAUDE.md records how to run the tests", "CLAUDE.md should say how to run the tests (python3 -m unittest)")
ok("tasks.py" in md or "tasks.json" in md, "CLAUDE.md describes the code layout (tasks.py / tasks.json)", "CLAUDE.md should mention tasks.py or tasks.json")
ok(ran(r"<command-name>/init</command-name>"), "a Claude Code session in this folder ran /init", "no session in this folder ran /init - open claude here and type /init")
PYEOF
```

## What you learned

- `/init` bootstraps a project memory file from what Claude finds in the repo.
- Slash commands talk to the console; everything else is a message to the model.
- Every session is saved per folder under `~/.claude/projects/`.
