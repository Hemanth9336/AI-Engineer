---
type: task
title: "Spawn a subagent for a subtask"
minutes: 11
---

## Set up

`workspace/logs/` has three logs of about 3,000 characters each.

```bash
mkdir -p /root/harness-lab/25-subagents/workspace/services
cd /root/harness-lab/25-subagents
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
import sys
from pathlib import Path

from openai import OpenAI

SYSTEM = "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly."

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


IMPL = {"list_dir": list_dir, "read_file": read_file}


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
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)
EOF
echo 'agent.py is your loop with a step limit (topic 08)'
python - <<'EOF'
from pathlib import Path
Path('workspace/logs').mkdir(parents=True, exist_ok=True)
for n in range(1, 4):
    Path(f'workspace/logs/part{n}.log').write_text(''.join(f'line {n}.{i} INFO search request ok {(i * 7 + n * 13) % 300}ms\n' for i in range(80)))
EOF
```

## What to build

Extend `/root/harness-lab/25-subagents/agent.py`:

1. Write `subagent(task, max_steps=6)`: a **fresh** message list (a system prompt starting with `You are a subagent` + the task as the only user message), the same `list_dir`/`read_file` tools, its own loop. It returns only its final text, capped at 1,500 characters (or a "stopped" message at the step limit).
2. Give the **parent** a `delegate(task)` tool that runs `subagent(task)` and returns its report as the tool result. The parent's tools are the file tools plus `delegate`; the subagent does **not** get `delegate`.

```bash
cd /root/harness-lab/25-subagents
python agent.py "Use a subagent to find which service runs on port 9200."
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Keep two tool sets: `SCHEMAS` for the subagent, `SCHEMAS + [delegate]` for the parent.
- Pass the right implementation map to `run_tool` so the parent can run `delegate`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/25-subagents
cat > agent.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

SYSTEM = "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly."

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


IMPL = {"list_dir": list_dir, "read_file": read_file}


def run_tool(name, args, impl=None):
    impl = impl or IMPL
    if name not in impl:
        return f"error: unknown tool {name}"
    try:
        return impl[name](**args)
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"


SUB_SYSTEM = "You are a subagent. Do only the task you are given, using the tools, then reply with a short final report: the answer and the files you used. You cannot ask questions."


def subagent(task, max_steps=6):
    client = OpenAI()
    messages = [{"role": "system", "content": SUB_SYSTEM}, {"role": "user", "content": task}]
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return (msg.content or "")[:1500]
        messages.append(msg)
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"subagent stopped: reached max steps ({max_steps})"


DELEGATE_SCHEMA = {"type": "function", "function": {
    "name": "delegate",
    "description": "Hand a self-contained subtask to a subagent with its own fresh context. It can read the workspace. You get back only its short final report. Write the task so it makes sense without this conversation.",
    "parameters": {"type": "object", "properties": {
        "task": {"type": "string", "description": "The full subtask, including any file names and constraints it needs"}},
        "required": ["task"]}}}
PARENT_SCHEMAS = SCHEMAS + [DELEGATE_SCHEMA]
PARENT_IMPL = dict(IMPL, delegate=lambda task: subagent(task))


def run(question, max_steps=8):
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=PARENT_SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"), PARENT_IMPL)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)

EOF
python agent.py "Use a subagent to find which service runs on port 9200."
```

</details>

## Check your work

```bash
D=/root/harness-lab/25-subagents; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/agent.py 2>/dev/null && [ -s $D/agent.py ] && echo "✅ agent.py reads the key from the environment" || echo "❌ agent.py must not contain a key - let the SDK read it from the environment"
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
rules_ = [{"match": "^You are a subagent", "on": "system", "steps": [{"tool": "read_file", "args": {"path": "logs/part1.log"}}, {"tool": "read_file", "args": {"path": "logs/part2.log"}}, {"tool": "read_file", "args": {"path": "logs/part3.log"}}, "part2.log has the slowest request (299ms). Files: logs/part1-3.log"]},
          {"match": "", "steps": [{"tool": "delegate", "args": {"task": "Find which of logs/part1.log, part2.log and part3.log has the slowest request."}}, "part2.log has the slowest request."]}]
with MockModel(rules=rules_) as m:
    rc, out, err = m.run(["python", "agent.py", "Which log has the slowest request? Use a subagent."], timeout=40)
subs = [r for r in m.requests if r["messages"][0].get("content", "").startswith("You are a subagent")]
parents = [r for r in m.requests if r not in subs]
ok(rc == 0 and len(subs) == 4 and len(parents) == 2 and out.endswith("part2.log has the slowest request."), "the parent delegated, the subagent ran its own 4-step loop, and the parent answered", f"{len(parents)} parent and {len(subs)} subagent calls; rc {rc}; {err[-200:]}")
if subs:
    first = subs[0]["messages"]
    ok(len(first) == 2 and first[1] == {"role": "user", "content": "Find which of logs/part1.log, part2.log and part3.log has the slowest request."}, "the subagent starts fresh: its system prompt and the task, nothing from the parent", f"the subagent's first request had {len(first)} messages")
    names = sorted((t.get("function") or {}).get("name") for t in subs[0].get("tools") or [])
    ok("delegate" not in names and "read_file" in names, "the subagent has the file tools but can't delegate again", f"subagent tools: {names}")
if parents:
    pnames = sorted((t.get("function") or {}).get("name") for t in parents[0].get("tools") or [])
    ptxt = json.dumps(parents[-1]["messages"])
    res = [x.get("content") for x in parents[-1]["messages"] if x.get("role") == "tool"]
    ok("delegate" in pnames, "the parent has a delegate tool", f"parent tools: {pnames}")
    ok(res == ["part2.log has the slowest request (299ms). Files: logs/part1-3.log"] and "INFO search request" not in ptxt, "the parent gets only the subagent's report - none of the 9,000 characters of logs", f"parent tool results: {[str(r)[:80] for r in res]}; parent context {len(ptxt)} chars")
with MockModel(rules=[{"match": "^You are a subagent", "on": "system", "steps": ["x" * 5000]}, {"match": "", "steps": [{"tool": "delegate", "args": {"task": "t"}}, "ok"]}]) as m:
    m.run(["python", "agent.py", "go"], timeout=30)
res = [x.get("content") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
ok(res and len(res[0]) <= 1500, "a long subagent report is capped at 1,500 characters", f"report length {len(res[0]) if res else None}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and (.tool_calls | index("delegate") != null))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the real model delegated to your subagent" || echo "❌ run the 'Use a subagent' question - no delegate call in the gateway log"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A subagent is a fresh context with its own loop for one focused subtask.
- The parent gets back only a short report, so its context stays small.
- The harness controls what the subagent gets (prompt, tools, step limit) and what comes back.
