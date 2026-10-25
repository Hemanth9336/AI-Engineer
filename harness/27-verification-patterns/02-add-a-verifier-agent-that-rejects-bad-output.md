---
type: task
title: "Add a verifier agent that rejects bad output"
minutes: 9
---

## Set up

```bash
mkdir -p /root/harness-lab/27-verify/workspace/services
cd /root/harness-lab/27-verify
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

Add a verifier to `/root/harness-lab/27-verify/agent.py`:

1. Collect **evidence** during the run: for each tool call, `"<name>(<arguments>): <result>"`.
2. When the generator gives a final answer, call `verify(client, question, evidence, answer)`: a separate `lab-fast` call, **no tools**, with a verifier system prompt starting `You are a verifier` and one user message containing the question, the evidence and the answer. It returns `(verdict, reason)` from the model's JSON reply `{"verdict": "pass"|"fail", "reason": "..."}`. Anything unparseable counts as `fail`.
3. On `pass`, return the answer. On `fail`, append the answer as an assistant message and a user message `A reviewer rejected your answer: <reason> ...`, and continue the loop.
4. After 2 rejected retries (3 failed answers), return `unverified: <last answer>` and exit with code **3**.

```bash
cd /root/harness-lab/27-verify
python agent.py "Which port does the billing service use?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Store assistant messages as plain dicts - you'll be appending text-only assistant messages too.
- Treat a reply like 'Looks good!' (not JSON) as fail, not pass.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/27-verify
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


def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    try:
        return IMPL[name](**args)
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"


VERIFIER = "You are a verifier. You check the answer of another agent against the evidence it collected. Reply with JSON only, like {\"verdict\": \"pass\", \"reason\": \"...\"} or {\"verdict\": \"fail\", \"reason\": \"...\"}. Fail the answer if any claim in it is not supported by the evidence."


def verify(client, question, evidence, answer):
    prompt = f"Question: {question}\n\nEvidence (tool results):\n{evidence}\n\nAnswer to check:\n{answer}"
    r = client.chat.completions.create(model="lab-fast", messages=[{"role": "system", "content": VERIFIER}, {"role": "user", "content": prompt}])
    try:
        v = json.loads(r.choices[0].message.content)
        if v.get("verdict") in ("pass", "fail"):
            return v["verdict"], str(v.get("reason", ""))
    except (ValueError, TypeError, AttributeError):
        pass
    return "fail", "the verifier's reply was not valid JSON"


def run(question, max_steps=8, max_retries=2):
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    evidence, rejections = [], 0
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            verdict, reason = verify(client, question, "\n---\n".join(evidence) or "(no tool results)", msg.content)
            if verdict == "pass":
                return msg.content
            rejections += 1
            if rejections > max_retries:
                return f"unverified: {msg.content}"
            messages.append({"role": "assistant", "content": msg.content})
            messages.append({"role": "user", "content": f"A reviewer rejected your answer: {reason} Check the evidence and answer again."})
            continue
        messages.append({"role": "assistant", "content": msg.content,
                         "tool_calls": [{"id": c.id, "type": "function", "function": {"name": c.function.name, "arguments": c.function.arguments}}
                                        for c in msg.tool_calls]})
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            evidence.append(f"{call.function.name}({call.function.arguments}): {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(3 if answer.startswith("unverified: ") else 2 if answer.startswith("stopped: reached max steps") else 0)

EOF
python agent.py "Which port does the billing service use?"
```

</details>

## Check your work

```bash
D=/root/harness-lab/27-verify; cd $D 2>/dev/null || echo "❌ create $D"
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
ver = {"match": "^You are a verifier", "on": "system", "by": "calls", "steps": ['{"verdict": "fail", "reason": "billing.yaml says port 8081, not 8080"}', '{"verdict": "pass", "reason": "matches billing.yaml"}']}
gen = {"match": "", "steps": [{"tool": "read_file", "args": {"path": "services/billing.yaml"}}, "Billing uses port 8080.", "Billing uses port 8081."]}
with MockModel(rules=[ver, gen]) as m:
    rc, out, err = m.run(["python", "agent.py", "Which port does billing use?"], timeout=30)
vs = [r for r in m.requests if r["messages"][0].get("content", "").startswith("You are a verifier")]
gs = [r for r in m.requests if r not in vs]
ok(rc == 0 and out.endswith("Billing uses port 8081.") and len(vs) == 2, "the verifier rejects the wrong port and passes the corrected answer", f"output {out[-60:]!r}, {len(vs)} verifier calls; rc {rc}; {err[-200:]}")
if vs:
    v0 = vs[0]
    txt = json.dumps(v0["messages"])
    ok(not v0.get("tools") and len(v0["messages"]) == 2 and "port: 8081" in txt and "8080" in txt and "Which port does billing use?" in txt, "the verifier gets its own context: no tools, the question, the evidence and the answer", f"verifier request: {len(v0['messages'])} messages, tools {bool(v0.get('tools'))}")
ok(gs and "billing.yaml says port 8081, not 8080" in json.dumps(gs[-1]["messages"]), "the rejection reason goes back to the generator", "the generator's retry should see the verifier's reason")
with MockModel(rules=[{"match": "^You are a verifier", "on": "system", "steps": ["Looks good to me!"]}, {"match": "", "steps": [{"tool": "read_file", "args": {"path": "services/billing.yaml"}}, "Billing uses port 8080."]}]) as m:
    rc, out, err = m.run(["python", "agent.py", "Which port does billing use?"], timeout=30)
vs = [r for r in m.requests if r["messages"][0].get("content", "").startswith("You are a verifier")]
ok(rc == 3 and out.startswith("unverified: ") and len(vs) == 3, "a verifier reply that isn't JSON counts as fail; after 2 retries the answer is returned as unverified (exit 3)", f"exit {rc}, output {out[:60]!r}, {len(vs)} verifier calls")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and (.tools | length) == 0 and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ your verifier checked a real answer" || echo "❌ run the billing question - no tool-less verifier call in the gateway log"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A verifier in a fresh context checks the answer against the evidence, not against the generator's reasoning.
- Return a structured verdict; anything unparseable counts as fail.
- Cap retries and label answers that never passed as unverified.
