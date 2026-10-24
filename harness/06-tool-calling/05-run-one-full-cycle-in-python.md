---
type: task
title: "Run one full cycle in Python"
minutes: 9
---

## Set up

`files/` is the project folder your tool may read from.

```bash
mkdir -p /root/harness-lab/06-tools/files
cd /root/harness-lab/06-tools
cat > files/release.txt <<'EOF'
version: 2.3.0
code freeze: Friday 17:00
owner: platform team
EOF
```

## What to build

Write `/root/harness-lab/06-tools/cycle.py`, used as `python cycle.py QUESTION`:

1. Implement `read_file(path)`: return the text of `files/<path>` (the folder next to `cycle.py`), or the string `error: no such file <path>` if it doesn't exist.
2. Call `lab-fast` with `tools=[READ_FILE_TOOL]` (from your `tools.py`).
3. If the reply has tool calls: append the assistant message, run each call through a dispatch table, append one `tool` message per call with its `tool_call_id`, and call the model **once more**.
4. Print the final reply text.

Make exactly one cycle - no loop yet.

```bash
cd /root/harness-lab/06-tools
python cycle.py "What version is in release.txt?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `HERE = Path(__file__).parent` then `(HERE / "files" / path)`.
- `TOOLS = {"read_file": read_file}`; check the name is in it before calling.
- Append `msg` itself (the SDK object) before the tool messages.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/06-tools
[ -f tools.py ] || cat > tools.py <<'EOF'
READ_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a text file from the project and return its contents. Use it whenever the answer depends on what a file says.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path relative to the project folder, for example notes/todo.txt"},
            },
            "required": ["path"],
        },
    },
}
EOF
cat > cycle.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

from tools import READ_FILE_TOOL

FILES = Path(__file__).parent / "files"


def read_file(path):
    p = FILES / path
    return p.read_text() if p.is_file() else f"error: no such file {path}"


TOOLS = {"read_file": read_file}


def run_tool(name, args):
    if name not in TOOLS:
        return f"error: unknown tool {name}"
    return TOOLS[name](**args)


client = OpenAI()
messages = [{"role": "user", "content": sys.argv[1]}]
msg = client.chat.completions.create(model="lab-fast", tools=[READ_FILE_TOOL], messages=messages).choices[0].message
if msg.tool_calls:
    messages.append(msg)
    for call in msg.tool_calls:
        result = run_tool(call.function.name, json.loads(call.function.arguments))
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    msg = client.chat.completions.create(model="lab-fast", tools=[READ_FILE_TOOL], messages=messages).choices[0].message
print(msg.content)
EOF
python cycle.py "What version is in release.txt?"
```

</details>

## Check your work

```bash
D=/root/harness-lab/06-tools; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/cycle.py 2>/dev/null && [ -s $D/cycle.py ] && echo "✅ cycle.py reads the key from the environment" || echo "❌ cycle.py must not contain a key - let the SDK read it from the environment"
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
with MockModel([{"tool": "read_file", "args": {"path": "release.txt"}}, "We are releasing 2.3.0."]) as m:
    rc, out, err = m.run(["python", "cycle.py", "Which version ships?"])
ok(rc == 0 and out == "We are releasing 2.3.0.", "cycle.py prints the model's final answer", f"cycle.py should print the reply after the tool result - got {out[-200:]!r} {err[-200:]}")
ok(len(m.requests) == 2, "exactly two model calls: the request and the follow-up", f"one cycle is two model calls - labmock saw {len(m.requests)}")
msgs = m.requests[1]["messages"] if len(m.requests) > 1 else []
roles = [x.get("role") for x in msgs]
tool = next((x for x in msgs if x.get("role") == "tool"), {})
asst = next((x for x in msgs if x.get("role") == "assistant"), {})
ok(roles == ["user", "assistant", "tool"], "the follow-up history is user, assistant, tool", f"the second call should send user, assistant (with tool_calls), tool - got {roles}")
ok(bool(asst.get("tool_calls")) and tool.get("tool_call_id") == "call_0_0", "the tool message answers the assistant's tool call id", f"the tool message's tool_call_id should match the call id call_0_0 - got {tool.get('tool_call_id')!r}")
ok("version: 2.3.0" in str(tool.get("content")), "the tool result is the real contents of files/release.txt", f"the tool message should carry the text of files/release.txt - got {str(tool.get('content'))[:120]!r}")
with MockModel([{"tool": "read_file", "args": {"path": "missing.txt"}}, "That file does not exist."]) as m:
    rc, out, err = m.run(["python", "cycle.py", "What is in missing.txt?"])
tool = next((x for x in (m.requests[1]["messages"] if len(m.requests) > 1 else []) if x.get("role") == "tool"), {})
ok(rc == 0 and "error" in str(tool.get("content")).lower() and out == "That file does not exist.", "a missing file goes back to the model as an error result, not a crash", f"read_file on a missing file should return an error string to the model - rc {rc}, tool content {str(tool.get('content'))[:120]!r} {err[-200:]}")
with MockModel(["Hello! How can I help?"]) as m:
    rc, out, err = m.run(["python", "cycle.py", "Hi"])
ok(rc == 0 and out == "Hello! How can I help?" and len(m.requests) == 1, "with no tool call, cycle.py answers after one call", f"a direct reply should be printed after a single call - got {out!r}, {len(m.requests)} calls")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- One cycle: call, append the assistant tool-call message, run the tool, append a tool message with the call id, call again.
- Tool results are strings - errors included - so the model can read and react to them.
- Dispatch tool names through a fixed table; never run arbitrary names from the model.
