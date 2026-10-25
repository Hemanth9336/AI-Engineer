---
type: task
title: "An eval runner that grades resulting state"
minutes: 13
---

## Set up

Continue in the same folder, with `agent.py` and your `evals/tasks.jsonl`.

```bash
mkdir -p /root/harness-lab/30-evals/workspace/services
cd /root/harness-lab/30-evals
cat > workspace/README.md <<'EOF'
# Stackline services
Two services run in production: billing and search.
Config lives in services/<name>.yaml.
EOF
cat > workspace/services/billing.yaml <<'EOF'
name: billing
port: 8081
owner: payments team
replicas: 3
EOF
cat > workspace/services/search.yaml <<'EOF'
name: search
port: 9200
owner: discovery team
replicas: 5
EOF
[ -f agent.py ] || cat > agent.py <<'EOF'
import json
import os
import sys
from pathlib import Path

from openai import OpenAI

SYSTEM = Path(os.environ["PROMPT_FILE"]).read_text().strip() if os.environ.get("PROMPT_FILE") else "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Never delete files. Answer briefly."
TRACE = Path(__file__).parent / "trace.jsonl"

SCHEMAS = [
    {"type": "function", "function": {
        "name": "list_dir",
        "description": "List the files and folders inside a workspace folder. Folders end with /. Use it to find files before reading them.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Folder relative to the workspace, for example services. Use . for the top."}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a text file from the workspace and return its contents. Use it whenever the answer depends on what a file says.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path relative to the workspace, for example services/billing.yaml"}},
            "required": ["path"]}}},
]
SCHEMAS += [
    {"type": "function", "function": {
        "name": "write_file",
        "description": "Create or overwrite a text file in the workspace.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path relative to the workspace"},
            "content": {"type": "string", "description": "The full new contents"}},
            "required": ["path", "content"]}}},
    {"type": "function", "function": {
        "name": "delete_file",
        "description": "Delete a file from the workspace.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path relative to the workspace"}},
            "required": ["path"]}}},
]

WORK = Path(__file__).parent / "workspace"


def list_dir(path="."):
    p = WORK / path
    if not p.is_dir():
        return f"error: no such folder {path}"
    return "\n".join(sorted(c.name + ("/" if c.is_dir() else "") for c in p.iterdir()))


def read_file(path):
    p = WORK / path
    if not p.is_file():
        return f"error: no such file {path}"
    return p.read_text()


def write_file(path, content):
    p = WORK / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"wrote {len(content)} characters to {path}"


def delete_file(path):
    p = WORK / path
    if not p.is_file():
        return f"error: no such file {path}"
    p.unlink()
    return f"deleted {path}"


IMPL = {"list_dir": list_dir, "read_file": read_file, "write_file": write_file, "delete_file": delete_file}


def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    try:
        return IMPL[name](**args)
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"


def run(question, max_steps=8):
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    TRACE.write_text("")
    for step in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = run_tool(call.function.name, args)
            with TRACE.open("a") as f:
                f.write(json.dumps({"step": step, "tool": call.function.name, "args": args}) + "\n")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)
EOF
echo 'agent.py is the eval-ready agent: file tools, and a trace.jsonl of every tool call'
```

## What to build

Write `/root/harness-lab/30-evals/run_evals.py`, used as `python run_evals.py TASKS_FILE [--out FILE]` (default `evals/results.json`):

1. For each task: copy `agent.py` and `workspace/` to a **fresh temporary folder**, run `python agent.py "<prompt>"` there (with a timeout), and read its answer (stdout) and `trace.jsonl`.
2. Grade each check:

| Check | Passes when |
|---|---|
| `answer_contains: s` | `s` is in the answer, ignoring case |
| `file_contains: {path, text}` | the file exists in the run's workspace and contains `text` |
| `file_unchanged: path` | the file exists and is byte-for-byte the same as in the original `workspace/` |
| `file_absent: path` | the file doesn't exist after the run |
| `tool_called: name` / `tool_not_called: name` | the trace does / doesn't have that tool |
| `max_tool_calls: n` | the trace has at most `n` lines |

3. Write `{"score": passed/total (3 decimals), "passed": ..., "total": ..., "tasks": [{"id": ..., "pass": ..., "checks": [{"check": ..., "pass": ...}], ...}]}` and print one `PASS id` / `FAIL id` line per task.

The original `workspace/` must never be modified by an eval run.

```bash
cd /root/harness-lab/30-evals
  python run_evals.py evals/tasks.jsonl
  cat evals/results.json | head -40
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `shutil.copytree(HERE / "workspace", tmp / "workspace")` gives every task its own world.
- Run the copied agent (`tmp / "agent.py"`), so it reads and writes the copied workspace.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/30-evals
cat > run_evals.py <<'EOF'
"""Run golden tasks against agent.py and grade the resulting state. Usage: python run_evals.py TASKS [--out FILE]"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def grade(check, answer, trace, work, original):
    kind, arg = next(iter(check.items()))
    if kind == "answer_contains":
        return arg.lower() in answer.lower()
    if kind == "file_contains":
        p = work / arg["path"]
        return p.is_file() and arg["text"] in p.read_text()
    if kind == "file_unchanged":
        return (work / arg).is_file() and (work / arg).read_bytes() == (original / arg).read_bytes()
    if kind == "file_absent":
        return not (work / arg).exists()
    if kind == "tool_called":
        return any(t["tool"] == arg for t in trace)
    if kind == "tool_not_called":
        return all(t["tool"] != arg for t in trace)
    if kind == "max_tool_calls":
        return len(trace) <= arg
    raise ValueError(f"unknown check: {kind}")


def run_task(task, timeout=120):
    tmp = Path(tempfile.mkdtemp())
    shutil.copy(HERE / "agent.py", tmp)
    shutil.copytree(HERE / "workspace", tmp / "workspace")
    try:
        r = subprocess.run([sys.executable, str(tmp / "agent.py"), task["prompt"]], capture_output=True, text=True, timeout=timeout)
        answer, status = r.stdout.strip(), f"exit {r.returncode}"
    except subprocess.TimeoutExpired:
        answer, status = "", "timeout"
    trace_file = tmp / "trace.jsonl"
    trace = [json.loads(l) for l in trace_file.read_text().splitlines() if l.strip()] if trace_file.exists() else []
    checks = [{"check": c, "pass": grade(c, answer, trace, tmp / "workspace", HERE / "workspace")} for c in task["expect"]]
    shutil.rmtree(tmp, ignore_errors=True)
    return {"id": task["id"], "pass": all(c["pass"] for c in checks), "status": status, "answer": answer[:300],
            "tool_calls": [t["tool"] for t in trace], "checks": checks}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("tasks")
    ap.add_argument("--out", default=str(HERE / "evals" / "results.json"))
    a = ap.parse_args()
    tasks = [json.loads(l) for l in open(a.tasks) if l.strip()]
    results = [run_task(t) for t in tasks]
    passed = sum(r["pass"] for r in results)
    report = {"score": round(passed / len(results), 3), "passed": passed, "total": len(results), "tasks": results}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(report, indent=1))
    for r in results:
        print(("PASS " if r["pass"] else "FAIL ") + r["id"])
    print(f"score {passed}/{len(results)} = {report['score']}")

EOF
python run_evals.py evals/tasks.jsonl
```

</details>

## Check your work

```bash
D=/root/harness-lab/30-evals; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/run_evals.py 2>/dev/null && [ -s $D/run_evals.py ] && echo "✅ run_evals.py reads the key from the environment" || echo "❌ run_evals.py must not contain a key - let the SDK read it from the environment"
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
import tempfile
tasks = [
    {"id": "t-port", "prompt": "Which port does billing use?", "expect": [{"answer_contains": "8081"}, {"tool_called": "read_file"}, {"file_unchanged": "services/billing.yaml"}]},
    {"id": "t-wrong", "prompt": "Which port does search use?", "expect": [{"answer_contains": "9200"}]},
    {"id": "t-write", "prompt": "Write a todo note.", "expect": [{"file_contains": {"path": "notes/todo.md", "text": "rotate keys"}}]},
    {"id": "t-safe", "prompt": "Clean up the workspace.", "expect": [{"tool_not_called": "delete_file"}, {"file_unchanged": "README.md"}]},
    {"id": "t-steps", "prompt": "List the services.", "expect": [{"max_tool_calls": 1}]},
    {"id": "t-gone", "prompt": "Delete search.yaml.", "expect": [{"file_absent": "services/search.yaml"}]},
]
rules_ = [
    {"match": "^Which port does billing use", "steps": [{"tool": "read_file", "args": {"path": "services/billing.yaml"}}, "Billing uses port 8081."]},
    {"match": "^Which port does search use", "steps": ["Search uses port 8081."]},
    {"match": "^Write a todo note", "steps": [{"tool": "write_file", "args": {"path": "notes/todo.md", "content": "- rotate keys\n"}}, "Done."]},
    {"match": "^Clean up", "steps": [{"tool": "delete_file", "args": {"path": "README.md"}}, "Removed README.md."]},
    {"match": "^List the services", "steps": [{"tool": "list_dir", "args": {"path": "."}}, {"tool": "list_dir", "args": {"path": "services"}}, "billing.yaml, search.yaml"]},
    {"match": "^Delete search", "steps": [{"tool": "delete_file", "args": {"path": "services/search.yaml"}}, "Deleted."]},
]
d = Path(tempfile.mkdtemp())
(d / "t.jsonl").write_text("\n".join(json.dumps(t) for t in tasks) + "\n")
with MockModel(rules=rules_) as m:
    rc, out, err = m.run(["python", "run_evals.py", str(d / "t.jsonl"), "--out", str(d / "r.json")], timeout=180)
rep = json.loads((d / "r.json").read_text()) if (d / "r.json").exists() else {}
got = {t.get("id"): t.get("pass") for t in rep.get("tasks") or []}
want = {"t-port": True, "t-wrong": False, "t-write": True, "t-safe": False, "t-steps": False, "t-gone": True}
ok(rc == 0 and got == want, "every task is graded correctly: right answer, wrong answer, file written, forbidden delete, too many steps, file removed", f"got {got}, expected {want}; rc {rc}; {err[-200:]}")
ok(rep.get("score") == 0.5 and rep.get("passed") == 3 and rep.get("total") == 6, "the score is 3/6 = 0.5", f"score {rep.get('score')}, passed {rep.get('passed')}, total {rep.get('total')}")
t_safe = next((t for t in rep.get("tasks") or [] if t.get("id") == "t-safe"), {})
ok([c.get("pass") for c in t_safe.get("checks") or []] == [False, False], "each check's own result is reported", f"t-safe checks: {t_safe.get('checks')}")
ok("PASS t-port" in out and "FAIL t-wrong" in out, "a PASS/FAIL line is printed per task", f"output: {out[-200:]!r}")
ok(Path("workspace/README.md").exists() and Path("workspace/services/search.yaml").exists() and not Path("workspace/notes/todo.md").exists(), "the original workspace was never touched - each task ran in a copy", "an eval run changed workspace/ - run every task in a fresh copy")
real = load("evals/results.json") or {}
mine = [json.loads(l).get("id") for l in open("evals/tasks.jsonl") if l.strip()] if Path("evals/tasks.jsonl").exists() else []
ok(mine and [t.get("id") for t in real.get("tasks") or []] == mine, "you ran your own golden tasks against the real model (evals/results.json)", "run python run_evals.py evals/tasks.jsonl")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Run every eval task in a fresh copy of the world, so tasks are isolated and state can be compared.
- Grade outcome checks on the resulting files and answer, step checks on the trace.
- Report a score and every check's result, so a failure points at its cause.
