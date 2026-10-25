---
type: task
title: "Reproduce a lost-context bug, fix the handoff"
minutes: 12
---

## Set up

`agent.py` is an orchestrator: the parent can `delegate(task)` to a subagent, and subagents have a `restart_service(service, cluster)` tool that writes to `restarts.log`.

`lossy.json` is a labmock script for a realistic parent model: it delegates with the short task `Restart the search service.` - dropping the user's constraint. The scripted subagent restarts **staging** only if it can see the word "staging" in its context; otherwise it picks production.

```bash
mkdir -p /root/harness-lab/28-handoff/workspace/services
cd /root/harness-lab/28-handoff
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
cat > lossy.json <<'EOF'
{
 "rules": [
  {
   "match": "^You are a subagent.*staging",
   "on": "all",
   "steps": [
    {
     "tool": "restart_service",
     "args": {
      "service": "search",
      "cluster": "staging"
     }
    },
    "Restarted search on staging."
   ]
  },
  {
   "match": "^You are a subagent",
   "on": "system",
   "steps": [
    {
     "tool": "restart_service",
     "args": {
      "service": "search",
      "cluster": "production"
     }
    },
    "Restarted search on production."
   ]
  },
  {
   "match": "",
   "steps": [
    {
     "tool": "delegate",
     "args": {
      "task": "Restart the search service."
     }
    },
    "Done - the subagent restarted search."
   ]
  }
 ]
}
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


def run_tool(name, args, impl=None):
    impl = impl or IMPL
    if name not in impl:
        return f"error: unknown tool {name}"
    try:
        return impl[name](**args)
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"


RESTART_SCHEMA = {"type": "function", "function": {
    "name": "restart_service",
    "description": "Restart a service on a cluster.",
    "parameters": {"type": "object", "properties": {
        "service": {"type": "string"}, "cluster": {"type": "string", "enum": ["staging", "production"]}},
        "required": ["service", "cluster"]}}}
RESTARTS = Path(__file__).parent / "restarts.log"


def restart_service(service, cluster):
    with RESTARTS.open("a") as f:
        f.write(f"{service} {cluster}\n")
    return f"ok: {service} restart requested on {cluster}"


SUB_SCHEMAS = SCHEMAS + [RESTART_SCHEMA]
SUB_IMPL = dict(IMPL, restart_service=restart_service)


SUB_SYSTEM = "You are a subagent. Do only the task you are given, using the tools, then reply with a short final report: the answer and the files you used. You cannot ask questions."


def subagent(task, max_steps=6):
    client = OpenAI()
    messages = [{"role": "system", "content": SUB_SYSTEM}, {"role": "user", "content": task}]
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SUB_SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return (msg.content or "")[:1500]
        messages.append(msg)
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"), SUB_IMPL)
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
echo 'agent.py delegates to subagents that can restart services'
```

## What to build

1. **Reproduce.** Run the orchestrator with the user's request and look at `restarts.log`:

```bash
cd /root/harness-lab/28-handoff
rm -f restarts.log
python /opt/harness/labmock.py lossy.json --port 4597 > /dev/null &
MOCK=$!
for i in $(seq 30); do curl -s http://127.0.0.1:4597/v1/models > /dev/null && break; sleep 0.2; done
OPENAI_BASE_URL=http://127.0.0.1:4597/v1 OPENAI_API_KEY=mock python agent.py "Search is failing. Restart it on the staging cluster only - production is in a change freeze."
kill $MOCK
cat restarts.log
```

Production was restarted during a change freeze, even though the user said staging only.

2. **Fix the handoff in the harness.** Change `agent.py` so that every `delegate(task)` sends the subagent a brief made of the task **plus the user's original request, verbatim**:
   `<task>\n\nOriginal user request (follow its constraints):\n<the user's request>`.

3. Run the same command again: `restarts.log` must now show staging only. Then try the real lab model:

```bash
python agent.py "Search is failing. Restart it on the staging cluster only - production is in a change freeze."
cat restarts.log
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Remember the question when `run()` starts, so `delegate` can read it.
- Change what the harness sends, not the parent's prompt - the model will drop constraints again some day.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/28-handoff
rm -f restarts.log
python /opt/harness/labmock.py lossy.json --port 4597 > /dev/null &
MOCK=$!
for i in $(seq 30); do curl -s http://127.0.0.1:4597/v1/models > /dev/null && break; sleep 0.2; done
OPENAI_BASE_URL=http://127.0.0.1:4597/v1 OPENAI_API_KEY=mock python agent.py "Search is failing. Restart it on the staging cluster only - production is in a change freeze."
kill $MOCK
cat restarts.log
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


RESTART_SCHEMA = {"type": "function", "function": {
    "name": "restart_service",
    "description": "Restart a service on a cluster.",
    "parameters": {"type": "object", "properties": {
        "service": {"type": "string"}, "cluster": {"type": "string", "enum": ["staging", "production"]}},
        "required": ["service", "cluster"]}}}
RESTARTS = Path(__file__).parent / "restarts.log"


def restart_service(service, cluster):
    with RESTARTS.open("a") as f:
        f.write(f"{service} {cluster}\n")
    return f"ok: {service} restart requested on {cluster}"


SUB_SCHEMAS = SCHEMAS + [RESTART_SCHEMA]
SUB_IMPL = dict(IMPL, restart_service=restart_service)


SUB_SYSTEM = "You are a subagent. Do only the task you are given, using the tools, then reply with a short final report: the answer and the files you used. You cannot ask questions."


def subagent(task, max_steps=6):
    client = OpenAI()
    messages = [{"role": "system", "content": SUB_SYSTEM}, {"role": "user", "content": task}]
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SUB_SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return (msg.content or "")[:1500]
        messages.append(msg)
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"), SUB_IMPL)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"subagent stopped: reached max steps ({max_steps})"


DELEGATE_SCHEMA = {"type": "function", "function": {
    "name": "delegate",
    "description": "Hand a self-contained subtask to a subagent with its own fresh context. It can read the workspace. You get back only its short final report. Write the task so it makes sense without this conversation.",
    "parameters": {"type": "object", "properties": {
        "task": {"type": "string", "description": "The full subtask, including any file names and constraints it needs"}},
        "required": ["task"]}}}
PARENT_SCHEMAS = SCHEMAS + [DELEGATE_SCHEMA]
USER_REQUEST = {"text": ""}


def brief(task):
    return f"{task}\n\nOriginal user request (follow its constraints):\n{USER_REQUEST['text']}"


PARENT_IMPL = dict(IMPL, delegate=lambda task: subagent(brief(task)))


def run(question, max_steps=8):
    client = OpenAI()
    USER_REQUEST["text"] = question
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
rm -f restarts.log
python /opt/harness/labmock.py lossy.json --port 4597 > /dev/null &
MOCK=$!
for i in $(seq 30); do curl -s http://127.0.0.1:4597/v1/models > /dev/null && break; sleep 0.2; done
OPENAI_BASE_URL=http://127.0.0.1:4597/v1 OPENAI_API_KEY=mock python agent.py "Search is failing. Restart it on the staging cluster only - production is in a change freeze."
kill $MOCK
cat restarts.log
python agent.py "Search is failing. Restart it on the staging cluster only - production is in a change freeze."
cat restarts.log
```

</details>

## Check your work

```bash
D=/root/harness-lab/28-handoff; cd $D 2>/dev/null || echo "❌ create $D"
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
Path("restarts.log").unlink(missing_ok=True)
spec = json.load(open("lossy.json"))
req = "Search is failing. Restart it on the staging cluster only - production is in a change freeze."
with MockModel(rules=spec["rules"]) as m:
    rc, out, err = m.run(["python", "agent.py", req], timeout=30)
log = Path("restarts.log").read_text().split() if Path("restarts.log").exists() else []
ok(rc == 0 and log == ["search", "staging"], "with the same lossy parent, only staging is restarted", f"restarts.log: {log}; rc {rc}; {err[-200:]}")
subs = [r for r in m.requests if r["messages"][0].get("content", "").startswith("You are a subagent")]
first = subs[0]["messages"][1]["content"] if subs else ""
ok(first.startswith("Restart the search service.") and req in first, "the subagent's brief has the parent's task plus the user's original request, verbatim", f"the subagent was given: {first[:200]!r}")
req2 = "Billing looks stuck. Restart billing on staging; do not touch production."
with MockModel(rules=[{"match": "^You are a subagent", "on": "system", "steps": ["ok"]}, {"match": "", "steps": [{"tool": "delegate", "args": {"task": "Restart billing."}}, "done"]}]) as m:
    m.run(["python", "agent.py", req2], timeout=30)
subs = [r for r in m.requests if r["messages"][0].get("content", "").startswith("You are a subagent")]
ok(subs and req2 in subs[0]["messages"][1]["content"], "the brief always carries the current request, not a hard-coded one", "a different question should appear in the subagent's brief")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and (.tool_calls | index("restart_service") != null))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the real model's subagent restarted a service through your handoff" || echo "❌ run the request against the gateway too - no restart_service call logged"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Lost context happens at the handoff: the parent's short task drops constraints it knew.
- The harness, not the model, should carry the original request and pinned constraints into every brief.
- Enforce critical constraints in the tools as well, so no brief can override them.
