---
type: task
title: "Add an approval step before a delete tool runs"
minutes: 10
---

## Set up

```bash
mkdir -p /root/harness-lab/15-danger/workspace/services
cd /root/harness-lab/15-danger
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
mkdir -p workspace/old
echo 'stale config' > workspace/old/a.txt
echo 'keep me' > workspace/old/b.txt
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

Change `/root/harness-lab/15-danger/agent.py`:

1. Add two tools: `write_file(path, content)` and `delete_file(path)` (both inside `workspace/`).
2. Add a `RISK` dict classifying every tool as `read`, `write` or `irreversible`: `list_dir` and `read_file` are read, `write_file` is write, `delete_file` is irreversible. **Unclassified tools count as irreversible.**
3. Before running an irreversible tool, print `APPROVE? <name> <args as JSON> [y/N]` on its own line and read one line from stdin. Only `y` or `yes` (any case) approves. Anything else - including a closed stdin - denies.
4. A denied call doesn't run and returns `error: the user denied <name>. Do not retry it; ask the user what they want instead.`
5. Append every decision to `approvals.log` (next to `agent.py`): `approved <name> <args JSON>` or `denied <name> <args JSON>`.

Read and write tools run without asking.

```bash
cd /root/harness-lab/15-danger
python agent.py "Delete old/a.txt"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Gate in `run_tool`, after the unknown-tool check and before calling `IMPL[name]`.
- `RISK.get(name, "irreversible")` makes unknown tools dangerous by default.
- `except EOFError:` - treat no answer as no.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/15-danger
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
        "description": "Delete a file from the workspace. This cannot be undone and needs the user's approval.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path relative to the workspace"}},
            "required": ["path"]}}},
]

RISK = {"list_dir": "read", "read_file": "read", "write_file": "write", "delete_file": "irreversible"}

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
APPROVALS = Path(__file__).parent / "approvals.log"


def approved(name, args):
    print(f"APPROVE? {name} {json.dumps(args)} [y/N]", flush=True)
    try:
        answer = input().strip().lower()
    except EOFError:
        answer = ""
    ok = answer in ("y", "yes")
    with open(APPROVALS, "a") as f:
        f.write(f"{'approved' if ok else 'denied'} {name} {json.dumps(args)}\n")
    return ok


def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    if RISK.get(name, "irreversible") == "irreversible" and not approved(name, args):
        return f"error: the user denied {name}. Do not retry it; ask the user what they want instead."
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
echo y | python agent.py "Delete old/a.txt"
```

</details>

## Check your work

```bash
D=/root/harness-lab/15-danger; cd $D 2>/dev/null || echo "❌ create $D"
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
Path("workspace/old").mkdir(parents=True, exist_ok=True)
Path("workspace/old/a.txt").write_text("stale config\n"); Path("workspace/old/b.txt").write_text("keep me\n")
Path("workspace/notes.txt").unlink(missing_ok=True); Path("approvals.log").unlink(missing_ok=True)
script = [{"tool": "delete_file", "args": {"path": "old/a.txt"}}, {"tool": "delete_file", "args": {"path": "old/b.txt"}},
          {"tool": "write_file", "args": {"path": "notes.txt", "content": "cleaned up old/a.txt"}}, {"tool": "read_file", "args": {"path": "notes.txt"}}, "Deleted a.txt; b.txt was kept."]
with MockModel(script) as m:
    rc, out, err = m.run(["python", "agent.py", "Clean up old/"], input="Y\nno\n", timeout=30)
asks = [l for l in out.splitlines() if l.startswith("APPROVE?")]
ok(rc == 0 and asks == ['APPROVE? delete_file {"path": "old/a.txt"} [y/N]', 'APPROVE? delete_file {"path": "old/b.txt"} [y/N]'], "each delete shows the exact action and asks once", f"expected two APPROVE? lines with the JSON args - got {asks} {err[-300:]}")
ok(not Path("workspace/old/a.txt").exists() and Path("workspace/old/b.txt").exists(), "the approved delete ran and the denied one didn't", f"a.txt should be gone (answered Y) and b.txt kept (answered no) - a exists: {Path('workspace/old/a.txt').exists()}, b exists: {Path('workspace/old/b.txt').exists()}")
res = [x.get("content", "") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
ok(len(res) == 4 and res[1] == "error: the user denied delete_file. Do not retry it; ask the user what they want instead.", "the denial goes back to the model as a 'don't retry' result", f"the second result should be the denial message - got {res[1:2]}")
ok(len(res) == 4 and Path("workspace/notes.txt").exists() and "cleaned up" in res[3], "write and read tools run without asking", "write_file should run without an APPROVE? prompt")
log = Path("approvals.log").read_text().splitlines() if Path("approvals.log").exists() else []
ok(log == ['approved delete_file {"path": "old/a.txt"}', 'denied delete_file {"path": "old/b.txt"}'], "approvals.log records both decisions with their arguments", f"approvals.log should hold 'approved delete_file ...' then 'denied delete_file ...' - got {log}")
Path("workspace/old/a.txt").write_text("stale config\n")
with MockModel([{"tool": "delete_file", "args": {"path": "old/a.txt"}}, "I couldn't get approval."]) as m:
    rc, out, err = m.run(["python", "agent.py", "Delete old/a.txt"], input="", timeout=30)
ok(rc == 0 and Path("workspace/old/a.txt").exists(), "with nobody to answer, the delete is denied", "with stdin closed the delete must not run")
sys.path.insert(0, ".")
try:
    import agent
    unknown = agent.RISK.get("format_disk", "irreversible") if hasattr(agent, "RISK") else None
    ok(agent.RISK.get("read_file") == "read" and agent.RISK.get("write_file") == "write" and agent.RISK.get("delete_file") == "irreversible", "RISK classifies read, write and irreversible tools", f"RISK should be read/write/irreversible for read_file/write_file/delete_file - got {getattr(agent, 'RISK', None)}")
except Exception as e:
    ok(False, "", f"agent.py should define RISK - {type(e).__name__}: {e}")
Path("agent_unknown_test.py").write_text("import agent\nagent.IMPL['format_disk'] = lambda: 'formatted'\nagent.SCHEMAS.append({'type': 'function', 'function': {'name': 'format_disk', 'parameters': {'type': 'object', 'properties': {}}}})\nimport sys\nprint(agent.run(sys.argv[1]))\n")
with MockModel([{"tool": "format_disk", "args": {}}, "ok"]) as m:
    rc, out, err = m.run(["python", "agent_unknown_test.py", "x"], input="", timeout=30)
res = [x.get("content", "") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
Path("agent_unknown_test.py").unlink()
ok(res and "denied" in res[0] and "APPROVE? format_disk" in out, "a tool missing from RISK is gated like an irreversible one", f"an unclassified tool should ask for approval and be denied with no answer - got {res[:1]} {err[-200:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Classify every tool as read, write or irreversible - and treat unclassified tools as irreversible.
- The gate shows the exact action, defaults to no, and returns denials as 'don't retry' results.
- Log every decision; a gate nobody can audit is hard to trust.
