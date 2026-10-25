---
type: task
title: "Add a done flag across the task app"
minutes: 30
---

## Set up

Set up creates `/root/mastery/055-taskapp` with:
- A small task CLI: `tasks/model.py`, `tasks/store.py` (JSON persistence), `tasks/cli.py`, and one test.
- `FEATURE.md`, the spec for a done flag that touches all three modules.

```bash
rm -rf /root/mastery/055-taskapp && mkdir -p /root/mastery/055-taskapp/tasks /root/mastery/055-taskapp/tests && cd /root/mastery/055-taskapp
cat > tasks/__init__.py <<'EOF'

EOF
cat > tasks/model.py <<'EOF'
from dataclasses import asdict, dataclass


@dataclass
class Task:
    id: int
    title: str

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return Task(id=d["id"], title=d["title"])
EOF
cat > tasks/store.py <<'EOF'
import json
from pathlib import Path

from tasks.model import Task


class Store:
    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return []
        return [Task.from_dict(d) for d in json.loads(self.path.read_text())]

    def save(self, tasks):
        self.path.write_text(json.dumps([t.to_dict() for t in tasks], indent=2))

    def add(self, title):
        tasks = self.load()
        task = Task(id=max((t.id for t in tasks), default=0) + 1, title=title)
        tasks.append(task)
        self.save(tasks)
        return task
EOF
cat > tasks/cli.py <<'EOF'
import argparse
import sys

from tasks.store import Store


def main(argv=None, out=sys.stdout, err=sys.stderr):
    p = argparse.ArgumentParser(prog="tasks")
    p.add_argument("--file", default="tasks.json")
    sub = p.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("add")
    add.add_argument("title")
    sub.add_parser("list")
    args = p.parse_args(argv)
    store = Store(args.file)
    if args.cmd == "add":
        task = store.add(args.title)
        print(f"added {task.id}: {task.title}", file=out)
    elif args.cmd == "list":
        for task in store.load():
            print(f"{task.id}. {task.title}", file=out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_tasks.py <<'EOF'
import io
import tempfile
import unittest
from pathlib import Path

from tasks.cli import main


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        out = io.StringIO()
        code = main(["--file", self.file, *args], out=out)
        return code, out.getvalue()

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.file = str(Path(self.dir.name, "tasks.json"))

    def tearDown(self):
        self.dir.cleanup()

    def test_add_and_list(self):
        self.run_cli("add", "Buy milk")
        self.run_cli("add", "Call Bo")
        self.assertEqual(self.run_cli("list")[1], "1. Buy milk\n2. Call Bo\n")
EOF
cat > FEATURE.md <<'EOF'
# Feature: mark tasks done

- A task has a `done` flag, false for new tasks.
- Existing tasks.json files, which have no `done` field, keep loading; their tasks count as not done.
- `tasks done <id>` marks a task done and prints `done <id>: <title>`. An unknown id prints `no task <id>` to stderr and exits 1.
- `tasks list` shows the state: `1. [ ] Buy milk`, `2. [x] Call Bo`.
- `tasks list --pending` shows only tasks that aren't done.
- Tests cover each of these.
EOF
python3 -m unittest -q
```

## What to build

1. **Plan** in plan mode, saving the envelope as `plan.json` and the result as `PLAN.md`:
   > Plan the feature in FEATURE.md for this task app: list every file to change, how old tasks.json files stay loadable, and the tests to add. Do not edit anything.

   Read `PLAN.md`. It should name all four files and say how old `tasks.json` files keep loading.
2. **Execute** with edits accepted and the test command allowed, saving `exec.json`:
   > Implement PLAN.md for the feature in FEATURE.md. Run python3 -m unittest after your edits and fix failures until the whole suite passes.
3. **Verify** with your own `verify.sh`. It exits 1 with a message on the first failure.
   - Run the suite.
   - Smoke-test `python3 -m tasks.cli` in a temp dir:
     - add two tasks, then `done 2`;
     - `list` and `list --pending`;
     - `done 9` must exit 1 with `no task 9`.
   - Load an old-format file with no `done` field.
   Run it until it prints `verify: all checks passed`.

The checker runs the CLI on hidden data and runs your `verify.sh` against the original code, where it must fail.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `err=$(cmd 2>&1 > /dev/null)` captures only stderr; `$?` right after it is the command's exit code.
- `dict.get("done", False)` in `from_dict` is the whole backward-compatibility story - make sure the plan says so.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/055-taskapp
claude -p 'Plan the feature in FEATURE.md for this task app: list every file to change, how old tasks.json files stay loadable, and the tests to add. Do not edit anything.' --permission-mode plan --output-format json < /dev/null > plan.json
jq -r .result plan.json > PLAN.md
cat PLAN.md
claude -p 'Implement PLAN.md for the feature in FEATURE.md. Run python3 -m unittest after your edits and fix failures until the whole suite passes.' --permission-mode acceptEdits --allowedTools "Bash(python3 -m unittest *)" --output-format json < /dev/null > exec.json
jq -r .result exec.json
cat > verify.sh <<'EOF'
#!/usr/bin/env bash
# verify.sh - independent check of the done-flag feature: unit tests, a CLI smoke test, and an old-format file.
set -u
cd "$(dirname "$0")"
fail() { echo "FAIL: $1"; exit 1; }
python3 -m unittest -q > /dev/null 2>&1 || fail "unit tests"
t=$(mktemp -d)
trap 'rm -rf "$t"' EXIT
cli() { python3 -m tasks.cli --file "$t/tasks.json" "$@"; }
cli add "Buy milk" > /dev/null && cli add "Call Bo" > /dev/null || fail "add"
[ "$(cli done 2)" = "done 2: Call Bo" ] || fail "done 2"
[ "$(cli list)" = "$(printf '1. [ ] Buy milk\n2. [x] Call Bo')" ] || fail "list shows state"
[ "$(cli list --pending)" = "1. [ ] Buy milk" ] || fail "list --pending"
err=$(cli done 9 2>&1 > /dev/null); code=$?
[ "$code" -eq 1 ] && [ "$err" = "no task 9" ] || fail "unknown id exits 1 with 'no task 9'"
echo '[{"id": 1, "title": "Legacy"}]' > "$t/tasks.json"
[ "$(cli list)" = "1. [ ] Legacy" ] || fail "old tasks.json without done"
echo "verify: all checks passed"
EOF
chmod +x verify.sh
./verify.sh
```

</details>

## Check your work

```bash
D=/root/mastery/055-taskapp; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def transcript(sid):
    for f in glob.glob(os.path.expanduser(f"~/.claude/projects/*/{sid}.jsonl")):
        rows = []
        for line in open(f, errors="replace"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
        return f, rows
    return None, []
OLD = {'tasks/model.py': 'from dataclasses import asdict, dataclass\n\n\n@dataclass\nclass Task:\n    id: int\n    title: str\n\n    def to_dict(self):\n        return asdict(self)\n\n    @staticmethod\n    def from_dict(d):\n        return Task(id=d["id"], title=d["title"])', 'tasks/store.py': 'import json\nfrom pathlib import Path\n\nfrom tasks.model import Task\n\n\nclass Store:\n    def __init__(self, path):\n        self.path = Path(path)\n\n    def load(self):\n        if not self.path.exists():\n            return []\n        return [Task.from_dict(d) for d in json.loads(self.path.read_text())]\n\n    def save(self, tasks):\n        self.path.write_text(json.dumps([t.to_dict() for t in tasks], indent=2))\n\n    def add(self, title):\n        tasks = self.load()\n        task = Task(id=max((t.id for t in tasks), default=0) + 1, title=title)\n        tasks.append(task)\n        self.save(tasks)\n        return task', 'tasks/cli.py': 'import argparse\nimport sys\n\nfrom tasks.store import Store\n\n\ndef main(argv=None, out=sys.stdout, err=sys.stderr):\n    p = argparse.ArgumentParser(prog="tasks")\n    p.add_argument("--file", default="tasks.json")\n    sub = p.add_subparsers(dest="cmd", required=True)\n    add = sub.add_parser("add")\n    add.add_argument("title")\n    sub.add_parser("list")\n    args = p.parse_args(argv)\n    store = Store(args.file)\n    if args.cmd == "add":\n        task = store.add(args.title)\n        print(f"added {task.id}: {task.title}", file=out)\n    elif args.cmd == "list":\n        for task in store.load():\n            print(f"{task.id}. {task.title}", file=out)\n    return 0\n\n\nif __name__ == "__main__":\n    sys.exit(main())'}

import io, shutil
plan = text("PLAN.md")
miss = [f for f in ("model.py", "store.py", "cli.py", "test") if f not in plan]
ok(plan and not miss and re.search(r"compat|old|existing", plan, re.I), "PLAN.md names model, store, cli, and tests, and addresses old files",
   f"save the plan-mode result as PLAN.md; it should name every file to change and how old tasks.json files keep loading - missing {miss}")
penv = load("plan.json") or {}
_, prow = transcript(penv.get("session_id") or "none")
pedits = [u.get("name") for u in uses(prow) if u.get("name") in ("Edit", "Write", "MultiEdit", "NotebookEdit")]
ok(prow and not pedits, "the planning run made no edits", f"run the planning step with --permission-mode plan and save plan.json - edits seen: {pedits}")
eenv = load("exec.json") or {}
_, erow = transcript(eenv.get("session_id") or "none")
seq = [(u.get("name"), (u.get("input") or {}).get("command", "")) for u in uses(erow)]
last_edit = max((i for i, (n, _) in enumerate(seq) if n in ("Edit", "Write", "MultiEdit")), default=-1)
tests_after = [i for i, (n, c) in enumerate(seq) if n == "Bash" and "unittest" in c and i > last_edit]
ok(last_edit >= 0 and tests_after, "the execution run edited files and ran the tests after its last edit", f"let the execute run run python3 -m unittest (allow it) after editing - tool sequence {[n for n, _ in seq]}")
sys.path.insert(0, os.getcwd())
for m in [k for k in sys.modules if k == "tasks" or k.startswith("tasks.")]:
    del sys.modules[m]
from tasks.cli import main
def cli(f, *a):
    o, e = io.StringIO(), io.StringIO()
    try:
        c = main(["--file", f, *a], out=o, err=e)
    except SystemExit as x:
        c = x.code
    return c, o.getvalue(), e.getvalue()
with tempfile.TemporaryDirectory() as t:
    f = os.path.join(t, "t.json")
    Path(f).write_text(json.dumps([{"id": 4, "title": "Old one"}, {"id": 7, "title": "Older"}]))
    r1 = cli(f, "list")
    r2 = cli(f, "done", "7")
    r3 = cli(f, "add", "Fresh")
    r4 = cli(f, "list")
    r5 = cli(f, "list", "--pending")
    r6 = cli(f, "done", "5")
    saved = json.loads(Path(f).read_text())
ok(r1[1] == "4. [ ] Old one\n7. [ ] Older\n", "an old-format file (no done field) loads with every task not done", f"old files must load as not done - list printed {r1[1]!r}")
ok(r2[:2] == (0, "done 7: Older\n") and r3[1] == "added 8: Fresh\n" and r4[1] == "4. [ ] Old one\n7. [x] Older\n8. [ ] Fresh\n",
   "done marks the right task, persists, and new tasks start not done", f"done/add/list on hidden data gave {r2[:2]}, {r3[1]!r}, {r4[1]!r}")
ok(r5[1] == "4. [ ] Old one\n8. [ ] Fresh\n", "list --pending hides done tasks", f"list --pending printed {r5[1]!r}")
ok(r6 == (1, "", "no task 5\n"), "an unknown id prints 'no task 5' to stderr and exits 1", f"done 5 should give (1, '', 'no task 5\\n') - got {r6}")
ok([d.get("done") for d in saved] == [False, True, False], "tasks.json now stores the done flag for every task", f"saved data should carry done for each task - got {saved}")
rc, out, err = sh("python3 -m unittest -q")
n = len(re.findall(r"def test_", text("tests/test_tasks.py")))
ok(rc == 0 and n >= 5 and "done" in text("tests/test_tasks.py") and "--pending" in text("tests/test_tasks.py"),
   f"the suite passes with {n} tests, covering done and --pending", f"tests should pass and cover done, --pending, unknown ids, and old files - rc {rc}, {n} tests")
rc, out, err = sh("./verify.sh")
ok(rc == 0, "./verify.sh passes on the feature", f"verify.sh failed: {(out + err).strip()[-200:]}")
with tempfile.TemporaryDirectory() as t:
    shutil.copytree(".", t, dirs_exist_ok=True)
    for rel, body in OLD.items():
        Path(t, rel).write_text(body)
    rc, out, err = sh("./verify.sh", cwd=t)
ok(rc != 0, "verify.sh fails against the pre-feature code - it really checks the feature", "verify.sh should fail when model, store, and cli are reverted to the original")
PYEOF
```

## What you learned

- Split multi-file work into plan (read-only, saved as an artifact), execute (edits plus a runnable test command), and verify (your script).
- Backward compatibility with existing data is part of the plan, or it's the bug that ships.
- A verification script proves something only if it fails on the old code; test the test.
