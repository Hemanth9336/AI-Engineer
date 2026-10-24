---
type: task
title: "Add an ask_user tool"
minutes: 10
---

## Set up

```bash
mkdir -p /root/harness-lab/11-ask/workspace/services
cd /root/harness-lab/11-ask
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
```

## What to build

Add an `ask_user(question)` tool to `/root/harness-lab/11-ask/agent.py`:

1. Its description must say **when** to ask (ambiguity, a decision only the user can make) and when **not** to (things the other tools can find out). At least 60 characters.
2. The harness prints `QUESTION: <question>` on its own line (flush it), reads one line from stdin with `input()`, and returns the stripped answer as the tool result.
3. If stdin is closed (`EOFError`), return a result starting `error: the user is not available` - don't crash or hang.

```bash
cd /root/harness-lab/11-ask
python agent.py "Restart the service."
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `print(f"QUESTION: {question}", flush=True)` then `input("> ")`.
- `except EOFError:` catches a closed stdin - for example `python agent.py ... < /dev/null`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/11-ask
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
SCHEMAS.append({"type": "function", "function": {
    "name": "ask_user",
    "description": "Ask the user one short question when the request is ambiguous or you need a decision only they can make. "
                   "Don't ask about things you can find out with the other tools.",
    "parameters": {"type": "object", "properties": {"question": {"type": "string", "description": "One clear question for the user"}},
                   "required": ["question"]}}})

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


def ask_user(question):
    print(f"QUESTION: {question}", flush=True)
    try:
        return input("> ").strip()
    except EOFError:
        return "error: the user is not available. Stop and explain what you need from them."


IMPL = {"list_dir": list_dir, "read_file": read_file, "ask_user": ask_user}


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
echo search | python agent.py "Restart the service."
```

</details>

## Check your work

```bash
D=/root/harness-lab/11-ask; cd $D 2>/dev/null || echo "❌ create $D"
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
sys.path.insert(0, ".")
try:
    from agent import SCHEMAS
    t = next(s["function"] for s in SCHEMAS if s["function"]["name"] == "ask_user")
    good = len(t.get("description", "")) >= 60 and t["parameters"].get("required") == ["question"]
except Exception:
    good, t = False, {}
ok(good, "ask_user is offered with a real description and a required question", f"SCHEMAS should include ask_user with a description of 60+ characters and required [question] - got {t}")
script = [{"tool": "ask_user", "args": {"question": "Which service do you mean: billing or search?"}},
          {"tool": "read_file", "args": {"path": "services/search.yaml"}}, "Search runs on port 9200 with 5 replicas."]
with MockModel(script) as m:
    rc, out, err = m.run(["python", "agent.py", "What port does the service use?"], input="search\n", timeout=30)
lines = out.splitlines()
ok(rc == 0 and "QUESTION: Which service do you mean: billing or search?" in lines and lines[-1].endswith("Search runs on port 9200 with 5 replicas."), "the question is shown, the run continues and answers", f"stdout should include the QUESTION line and end with the answer - got {out[-300:]!r} {err[-300:]}")
res = [x.get("content", "") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
ok(len(res) == 2 and res[0] == "search", "the user's typed answer is the tool result", f"the ask_user result should be exactly 'search' - got {res[:1]}")
with MockModel([{"tool": "ask_user", "args": {"question": "Delete or archive?"}}, "I need to know whether to delete or archive the old configs."]) as m:
    rc, out, err = m.run(["python", "agent.py", "Clean up old configs."], input="", timeout=30)
res = [x.get("content", "") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
ok(rc == 0 and res and res[0].startswith("error: the user is not available"), "with no user attached, ask_user returns an error and the run ends cleanly", f"with stdin closed the result should start 'error: the user is not available' - got rc {rc}, {res[:1]} {err[-200:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Asking is a tool: the model calls ask_user, the harness gets the answer from wherever the user is.
- The description steers when to ask - and when to look it up instead.
- Unattended runs need an honest 'user not available' result, not a hang.
