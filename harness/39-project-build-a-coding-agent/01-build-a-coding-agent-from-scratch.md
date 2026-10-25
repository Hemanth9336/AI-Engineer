---
type: task
title: "Build a coding agent from scratch"
minutes: 75
---

## Scenario

Your team keeps a small Python library, and the backlog is full of tiny, well-specified changes: fix this bug, add that helper with tests. You'll build a **coding agent harness** from scratch to take them on - not a chat bot that suggests code, but a loop that reads files, edits them, runs the tests, and doesn't call itself done until they pass.

Everything you need is in this course: the loop and stop conditions (topics 7-8), errors as results (9), tool design and result shaping (12-14), dangerous tools and allowlists (15, 21), a workdir sandbox (22), verification (27) and trajectory logs (31).

## Set up

Set up creates `/root/harness-lab/39-coding-agent/repo` - a tiny `calc` package with a unittest suite (one test fails: `add` subtracts) - and `tasks.json` with the two seeded tasks. Re-running Set up resets the repo.

```bash
mkdir -p /root/harness-lab/39-coding-agent/runs
cd /root/harness-lab/39-coding-agent
rm -rf repo && mkdir -p repo/calc repo/tests
: > repo/calc/__init__.py
cat > repo/calc/ops.py <<'EOF'
def add(a, b):
    return a - b


def mean(values):
    if not values:
        return 0
    return sum(values) / len(values)
EOF
: > repo/tests/__init__.py
cat > repo/tests/test_ops.py <<'EOF'
import unittest

from calc.ops import add, mean


class OpsTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_mean(self):
        self.assertEqual(mean([2, 4, 6]), 4)

    def test_mean_empty(self):
        self.assertEqual(mean([]), 0)
EOF
cat > tasks.json <<'EOF'
[
  {
    "id": "fix-add",
    "task": "Fix the bug in add in calc/ops.py so the tests pass."
  },
  {
    "id": "add-percent",
    "task": "Add percent(part, whole) to calc/ops.py: part as a percentage of whole, rounded to 1 decimal, and 0.0 when whole is 0. Add tests for it in tests/test_percent.py."
  }
]
EOF
(cd repo && python -m unittest discover -s tests -q 2>&1 | tail -3) || true
```

## What to build

Write `/root/harness-lab/39-coding-agent/coder.py`, used as `python coder.py --repo DIR [--max-steps N] [--log FILE] "TASK"`, on `lab-fast`.

**Tools** - all paths are relative to the repo and must resolve **inside** it (absolute paths, `..` and symlinks out are refused with `error: path outside the repo: <path>`):

| Tool | Behavior | Result |
|---|---|---|
| `list_files(path)` | Files under a folder, recursively, relative paths, sorted, no `__pycache__` or dot-folders, at most 200 | one path per line |
| `read_file(path)` | The file's text | the text, or `error: no such file <path>` |
| `edit_file(path, old, new)` | Replace `old` with `new` - only if `old` appears **exactly once** | `edited <path>`, or an `error:` saying how many times it was found |
| `write_file(path, content)` | Create or overwrite a file, making folders | `wrote <path>` |
| `run_shell(command)` | Run in the repo root: only commands starting with `python -m unittest`, `python -m py_compile`, `ls`, `cat` or `grep`; no `; & \| < > $` backtick or newline. 30 s timeout, output capped at 4,000 characters | `exit <code>\n<stdout+stderr>`, or `error: not allowed: <command>` |

Tool errors are returned as results, never raised (topic 9).

**Stop conditions**

- When the model replies without a tool call, the **harness** runs `python -m unittest discover -s tests -q` itself. Pass: status `done`. Fail: add the model's reply and a user message starting `The tests still fail` with the end of the output, and continue - at most **2** times, then status `tests_failing`.
- `--max-steps` (default 20) model calls, then status `max_steps`.
- Print the final answer, then `status: <status>`, and exit 0 / 2 / 3 for done / max_steps / tests_failing.

**Trajectory log** - `--log FILE` (default `runs/<timestamp>.jsonl` next to `coder.py`), one JSON object per line, rewritten each run:

| `event` | Fields |
|---|---|
| `run_start` | `task`, `repo` |
| `model_call` | `step`, `tool_calls` (names), `text` |
| `tool_call` | `step`, `name`, `args`, `result` (first 500 characters) |
| `verify` | `step`, `passed` |
| `run_end` | `status`, `steps` (model calls made) |

Then let it work through the seeded tasks:

```bash
cd /root/harness-lab/39-coding-agent
python coder.py --repo repo --log runs/fix-add.jsonl "Fix the bug in add in calc/ops.py so the tests pass."
python coder.py --repo repo --log runs/add-percent.jsonl "Add percent(part, whole) to calc/ops.py: part as a percentage of whole, rounded to 1 decimal, and 0.0 when whole is 0. Add tests for it in tests/test_percent.py."
(cd repo && python -m unittest discover -s tests -q)
grep -c '"event": "tool_call"' runs/fix-add.jsonl runs/add-percent.jsonl
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `p = (root / rel).resolve()` then require `p == root or root in p.parents` - resolving first is what catches symlinks.
- Check the command for operator characters before splitting it with `shlex.split`, and compare the first tokens against the allowlist.
- Map `python` to `sys.executable` so the tests run with the same interpreter as the agent.
- Verification by the harness is what makes 'done' trustworthy: the model saying it's finished is not evidence.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/39-coding-agent
cat > coder.py <<'EOF'
"""A minimal coding agent. Usage: python coder.py --repo DIR [--max-steps N] [--log FILE] "TASK"
Exit codes: 0 done (tests pass), 2 step limit, 3 finished but tests still fail."""
import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path

from openai import OpenAI

SYSTEM = ("You are a careful coding agent working in a Python repository. Read the relevant files before you change them. "
          "Make the smallest change that does the task. Use edit_file for changes to existing files and write_file only for "
          "new files. Run the tests with run_shell(\"python -m unittest discover -s tests -q\") before you finish. "
          "When the task is done, reply with a one-line summary and no tool call.")

TEST_CMD = "python -m unittest discover -s tests -q"
ALLOWED = [["python", "-m", "unittest"], ["python", "-m", "py_compile"], ["ls"], ["cat"], ["grep"]]
OPERATORS = set(";&|<>`$\n")
MAX_OUTPUT = 4000
TIMEOUT = 30
MAX_RETRIES = 2

SCHEMAS = [
    {"type": "function", "function": {
        "name": "list_files",
        "description": "List the files under a folder of the repository, recursively, as relative paths. Use it to find files.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Folder relative to the repo root; . for everything"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a text file from the repository. Always read a file before editing it.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path relative to the repo root, like calc/ops.py"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "edit_file",
        "description": "Replace one exact piece of text in an existing file. old must appear exactly once in the file; include enough surrounding lines to make it unique.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "old": {"type": "string", "description": "Exact text to replace"},
            "new": {"type": "string", "description": "Replacement text"}}, "required": ["path", "old", "new"]}}},
    {"type": "function", "function": {
        "name": "write_file",
        "description": "Create a new file (or overwrite one completely) with the given content. Prefer edit_file for existing files.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {
        "name": "run_shell",
        "description": "Run one command in the repo root. Allowed: python -m unittest ..., python -m py_compile ..., ls, cat, grep. No pipes, redirects or chaining.",
        "parameters": {"type": "object", "properties": {
            "command": {"type": "string", "description": "For example: python -m unittest discover -s tests -q"}}, "required": ["command"]}}},
]


class Repo:
    def __init__(self, root):
        self.root = Path(root).resolve()

    def path(self, rel):
        p = (self.root / rel).resolve()
        if p != self.root and self.root not in p.parents:
            raise PermissionError(f"path outside the repo: {rel}")
        return p

    def list_files(self, path="."):
        base = self.path(path)
        if not base.is_dir():
            return f"error: no such folder {path}"
        files = sorted(str(f.relative_to(self.root)) for f in base.rglob("*")
                       if f.is_file() and "__pycache__" not in f.parts and not any(x.startswith(".") for x in f.relative_to(self.root).parts))
        return "\n".join(files[:200]) or "(empty)"

    def read_file(self, path):
        p = self.path(path)
        if not p.is_file():
            return f"error: no such file {path}"
        return p.read_text()

    def edit_file(self, path, old, new):
        p = self.path(path)
        if not p.is_file():
            return f"error: no such file {path}"
        text = p.read_text()
        n = text.count(old) if old else 0
        if n != 1:
            return f"error: old text found {n} times in {path} - it must appear exactly once"
        p.write_text(text.replace(old, new, 1))
        return f"edited {path}"

    def write_file(self, path, content):
        p = self.path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return f"wrote {path}"

    def run_shell(self, command):
        if any(c in OPERATORS for c in command):
            return f"error: not allowed: {command} (no pipes, redirects or chaining)"
        try:
            argv = shlex.split(command)
        except ValueError as e:
            return f"error: could not parse command: {e}"
        if not any(argv[:len(a)] == a for a in ALLOWED):
            return f"error: not allowed: {command}"
        if argv[0] == "python":
            argv[0] = sys.executable
        try:
            r = subprocess.run(argv, cwd=self.root, capture_output=True, text=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            return f"error: timed out after {TIMEOUT}s"
        out = r.stdout + r.stderr
        if len(out) > MAX_OUTPUT:
            out = out[:MAX_OUTPUT] + f"\n[truncated {len(out) - MAX_OUTPUT} characters]"
        return f"exit {r.returncode}\n{out}"


def run_tool(repo, name, args):
    fn = getattr(repo, name, None) if name in {s["function"]["name"] for s in SCHEMAS} else None
    if fn is None:
        return f"error: unknown tool {name}"
    try:
        return fn(**args)
    except PermissionError as e:
        return f"error: {e}"
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"


def run(task, repo_dir, max_steps=20, log_path=None):
    repo = Repo(repo_dir)
    log_path = Path(log_path or Path(__file__).parent / "runs" / time.strftime("%Y%m%d-%H%M%S.jsonl"))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("")

    def log(event, **data):
        with log_path.open("a") as f:
            f.write(json.dumps({"event": event, **data}) + "\n")

    def finish(status, steps, answer):
        log("run_end", status=status, steps=steps)
        return status, answer

    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": task}]
    log("run_start", task=task, repo=str(repo.root))
    retries = 0
    for step in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        log("model_call", step=step, tool_calls=[c.function.name for c in msg.tool_calls or []], text=msg.content or "")
        if not msg.tool_calls:
            out = repo.run_shell(TEST_CMD)
            passed = out.startswith("exit 0\n")
            log("verify", step=step, passed=passed)
            if passed:
                return finish("done", step + 1, msg.content or "")
            if retries == MAX_RETRIES:
                return finish("tests_failing", step + 1, msg.content or "")
            retries += 1
            messages.append({"role": "assistant", "content": msg.content or ""})
            messages.append({"role": "user", "content": "The tests still fail, so the task isn't done. Fix them before you finish.\n\n" + out[-2000:]})
            continue
        messages.append(msg)
        for call in msg.tool_calls:
            try:
                args = json.loads(call.function.arguments or "{}")
                result = run_tool(repo, call.function.name, args)
            except json.JSONDecodeError:
                args, result = {}, "error: arguments were not valid JSON"
            log("tool_call", step=step, name=call.function.name, args=args, result=result[:500])
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return finish("max_steps", max_steps, f"stopped: reached max steps ({max_steps})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--max-steps", type=int, default=20)
    ap.add_argument("--log")
    a = ap.parse_args()
    status, answer = run(a.task, a.repo, a.max_steps, a.log)
    print(answer)
    print(f"status: {status}")
    sys.exit({"done": 0, "max_steps": 2, "tests_failing": 3}[status])

EOF
cd /root/harness-lab/39-coding-agent
python coder.py --repo repo --log runs/fix-add.jsonl "Fix the bug in add in calc/ops.py so the tests pass."
python coder.py --repo repo --log runs/add-percent.jsonl "Add percent(part, whole) to calc/ops.py: part as a percentage of whole, rounded to 1 decimal, and 0.0 when whole is 0. Add tests for it in tests/test_percent.py."
(cd repo && python -m unittest discover -s tests -q)
grep -c '"event": "tool_call"' runs/fix-add.jsonl runs/add-percent.jsonl
```

</details>

## Check your work

```bash
D=/root/harness-lab/39-coding-agent; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/coder.py 2>/dev/null && [ -s $D/coder.py ] && echo "✅ coder.py reads the key from the environment" || echo "❌ coder.py must not contain a key - let the SDK read it from the environment"
python - <<'PYEOF'
import json, math, os, subprocess, sys
from pathlib import Path
from openai import OpenAI
_C = OpenAI()
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def E(xs):
    return [d.embedding for d in _C.embeddings.create(model="lab-embed", input=xs).data]
def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def run(*args, cwd=None):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()
sys.path.insert(0, '/opt/harness')
from labmock import MockModel
import shutil, tempfile
REPO = {'calc/__init__.py': '', 'calc/ops.py': 'def add(a, b):\n    return a - b\n\n\ndef mean(values):\n    if not values:\n        return 0\n    return sum(values) / len(values)\n', 'tests/__init__.py': '', 'tests/test_ops.py': 'import unittest\n\nfrom calc.ops import add, mean\n\n\nclass OpsTest(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n\n    def test_mean(self):\n        self.assertEqual(mean([2, 4, 6]), 4)\n\n    def test_mean_empty(self):\n        self.assertEqual(mean([]), 0)\n'}
def fresh(fixed=False):
    d = Path(tempfile.mkdtemp()) / "repo"
    for p, t in REPO.items():
        (d / p).parent.mkdir(parents=True, exist_ok=True)
        (d / p).write_text(t.replace("return a - b", "return a + b") if fixed else t)
    return d
def go(steps, repo, *extra, task="Do the task."):
    log = repo.parent / "log.jsonl"
    with MockModel(rules=[{"match": "", "steps": steps}]) as m:
        rc, out, err = m.run(["python", "coder.py", "--repo", str(repo), "--log", str(log), *extra, task], timeout=120)
    evs = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    return rc, out, err, m.requests, evs
def results(reqs):
    return [x.get("content") for x in (reqs[-1]["messages"] if reqs else []) if x.get("role") == "tool"]
if not Path("coder.py").exists():
    print("❌ write coder.py")
else:
    r = fresh()
    rc, out, err, reqs, evs = go([{"tool": "read_file", "args": {"path": "calc/ops.py"}}, {"tool": "edit_file", "args": {"path": "calc/ops.py", "old": "return a - b", "new": "return a + b"}}, {"tool": "run_shell", "args": {"command": "python -m unittest discover -s tests -q"}}, "Fixed add."], r)
    res = results(reqs)
    ok(rc == 0 and out.splitlines()[-1:] == ["status: done"] and "return a + b" in (r / "calc/ops.py").read_text(), "a scripted fix runs read -> edit -> test -> done, exit 0", f"rc {rc}, out {out[-150:]!r} {err[-300:]}")
    ok(len(res) == 3 and res[0] == REPO["calc/ops.py"] and res[1] == "edited calc/ops.py" and res[2].startswith("exit 0\n") and "OK" in res[2], "tool results: file text, 'edited calc/ops.py', 'exit 0' + test output", f"tool results: {[str(x)[:60] for x in res]}")
    kinds = [e.get("event") for e in evs]
    ok(kinds == ["run_start", "model_call", "tool_call", "model_call", "tool_call", "model_call", "tool_call", "model_call", "verify", "run_end"] and evs[-1] == {"event": "run_end", "status": "done", "steps": 4} and evs[-2].get("passed") is True and evs[2].get("name") == "read_file" and evs[3].get("tool_calls") == ["edit_file"], "the trajectory log has every event in order", f"log events: {kinds} last {evs[-1:] }")
    r = fresh(fixed=True)
    (r / "link").symlink_to(r.parent)
    rc, out, err, reqs, evs = go([{"calls": [{"tool": "write_file", "args": {"path": "../escape.txt", "content": "x"}}, {"tool": "read_file", "args": {"path": "/etc/hosts"}}, {"tool": "write_file", "args": {"path": "link/evil.txt", "content": "x"}}, {"tool": "list_files", "args": {"path": ".."}}]}, "done"], r)
    res = results(reqs)
    ok(len(res) == 4 and all(str(x).startswith("error: path outside the repo") for x in res) and not (r.parent / "escape.txt").exists() and not (r.parent / "evil.txt").exists(), "../, absolute paths and a symlink out of the repo are all refused", f"results {[str(x)[:60] for x in res]}")
    rc, out, err, reqs, evs = go([{"calls": [{"tool": "run_shell", "args": {"command": "rm -rf calc"}}, {"tool": "run_shell", "args": {"command": "ls; rm -rf calc"}}, {"tool": "run_shell", "args": {"command": "cat calc/ops.py | sh"}}, {"tool": "run_shell", "args": {"command": "python -c 'import shutil; shutil.rmtree(\"calc\")'"}}, {"tool": "run_shell", "args": {"command": "ls calc"}}]}, "done"], r)
    res = results(reqs)
    ok(len(res) == 5 and all(str(x).startswith("error: not allowed") for x in res[:4]) and res[4].startswith("exit 0\n") and "ops.py" in res[4] and (r / "calc/ops.py").exists(), "run_shell refuses rm, chaining, pipes and python -c, and runs ls", f"results {[str(x)[:60] for x in res]}")
    before = (r / "calc/ops.py").read_text()
    (r / "dup.txt").write_text("x = 1\nx = 1\n")
    rc, out, err, reqs, evs = go([{"calls": [{"tool": "edit_file", "args": {"path": "calc/ops.py", "old": "no such text", "new": "y"}}, {"tool": "edit_file", "args": {"path": "dup.txt", "old": "x = 1", "new": "x = 2"}}, {"tool": "read_file", "args": {"path": "nope.py"}}, {"tool": "teleport", "args": {}}]}, "done"], r)
    res = results(reqs)
    ok(len(res) == 4 and all(str(x).startswith("error:") for x in res) and "0 times" in res[0] and "2 times" in res[1] and (r / "dup.txt").read_text() == "x = 1\nx = 1\n" and (r / "calc/ops.py").read_text() == before, "edit_file needs exactly one match; missing files and unknown tools are errors, nothing changes", f"results {[str(x)[:70] for x in res]}")
    (r / "big.txt").write_text("y" * 20000)
    rc, out, err, reqs, evs = go([{"tool": "run_shell", "args": {"command": "cat big.txt"}}, "done"], r)
    res = results(reqs)
    ok(res and len(res[0]) < 4300 and res[0].startswith("exit 0"), "run_shell output is capped near 4,000 characters", f"result length {len(res[0]) if res else None}")
    r = fresh()
    rc, out, err, reqs, evs = go(["All done!"], r)
    last = reqs[-1]["messages"] if reqs else []
    ok(rc == 3 and len(reqs) == 3 and out.splitlines()[-1:] == ["status: tests_failing"], "a model that claims 'done' while tests fail is sent back twice, then stops with exit 3", f"rc {rc}, {len(reqs)} model calls, out {out[-100:]!r}")
    ok(last and last[-1]["role"] == "user" and last[-1]["content"].startswith("The tests still fail") and "test_add" in last[-1]["content"], "the harness tells the model the tests still fail, with the failing output", f"last message: {str(last[-1:])[:200]}")
    ok([e.get("passed") for e in evs if e.get("event") == "verify"] == [False, False, False] and evs[-1:] == [{"event": "run_end", "status": "tests_failing", "steps": 3}], "the log records each failed verification and the final status", f"log tail {evs[-2:]}")
    rc, out, err, reqs, evs = go([{"tool": "list_files", "args": {"path": "."}}], fresh(fixed=True), "--max-steps", "5")
    ok(rc == 2 and len(reqs) == 5 and out.splitlines()[-1:] == ["status: max_steps"] and evs[-1:] == [{"event": "run_end", "status": "max_steps", "steps": 5}], "a model that never stops is cut off by --max-steps (exit 2)", f"rc {rc}, {len(reqs)} calls, out {out[-100:]!r}")
rr = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], cwd="repo", capture_output=True, text=True)
ops = Path("repo/calc/ops.py").read_text() if Path("repo/calc/ops.py").exists() else ""
ok(rr.returncode == 0 and "return a + b" in ops and "def percent(part, whole)" in ops and Path("repo/tests/test_percent.py").exists() and "Ran 5 tests" in rr.stderr, "the seeded tasks are done in repo/: add fixed, percent added with its tests, all 5 tests pass", f"repo tests: {rr.stderr[-200:]!r}")
for t in ("fix-add", "add-percent"):
    evs = [json.loads(l) for l in open(f"runs/{t}.jsonl")] if Path(f"runs/{t}.jsonl").exists() else []
    ok(evs[-1:] and evs[-1].get("status") == "done" and any(e.get("event") == "verify" and e.get("passed") for e in evs), f"runs/{t}.jsonl: the real run finished with tests passing", f"runs/{t}.jsonl should end with status done - got {evs[-1:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and (.tool_calls | index("edit_file") != null))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your agent's edit_file calls" || echo "❌ no edit_file call from your agent in the gateway log - run the seeded tasks"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A coding agent is the same loop with file, edit and shell tools - the safety lives in the tool code.
- Confine paths after resolving them, and allowlist shell commands token by token, refusing operators.
- 'Done' means the harness ran the tests and they passed - not that the model said so.
- A trajectory log of every model call, tool call and verification makes each run reviewable.
