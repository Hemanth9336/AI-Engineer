---
type: task
title: "Set and enforce a per-part budget"
minutes: 10
---

## Set up

`workspace/logs/` has six log files of about 4,000 characters each - enough to blow a small budget in a few steps.

```bash
mkdir -p /root/harness-lab/17-budget/workspace/services
cd /root/harness-lab/17-budget
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
for n in range(1, 7):
    Path(f'workspace/logs/part{n}.log').write_text(''.join(f'line {n}.{i} INFO search request ok {i * 7 % 300}ms\n' for i in range(120)))
EOF
```

## What to build

1. Write `/root/harness-lab/17-budget/budget.py` with `BUDGET = {"tool_result_chars": 2000, "history_chars": 6000}` and `enforce(messages, budget=BUDGET)` that returns a **new** list:
   - `messages[0]` (system) and `messages[1]` (the task) are always kept, unchanged.
   - Any tool message whose content is longer than `tool_result_chars` is cut to that many characters plus `\n[truncated: <N> more characters]`.
   - The rest is grouped into turns (an assistant message plus the tool messages after it). While the total `len(json.dumps(m))` of those messages is over `history_chars`, drop the **oldest** turn - but never the last one.
   - If any turns were dropped, insert one user message right after the task: `[note: <N> earlier steps were dropped to fit the context budget]`. Drop any old note first, so there is only ever one.
2. In `agent.py`, store assistant messages as plain dicts (topic 10), and call `messages = enforce(messages)` before every model call.

```bash
cd /root/harness-lab/17-budget
python agent.py "Read every file in logs/ and tell me which has the slowest request."
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Filter out messages starting `[note: ` before grouping, then re-add a fresh one.
- Group: start a new turn at every non-tool message; append tool messages to the current turn.
- Truncate first, then measure and drop.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/17-budget
cat > budget.py <<'EOF'
import json

BUDGET = {"tool_result_chars": 2000, "history_chars": 6000}


def size(m):
    return len(json.dumps(m))


def turns(msgs):
    """Group messages into turns: an assistant message plus the tool results that follow it."""
    out = []
    for m in msgs:
        if m.get("role") == "tool" and out:
            out[-1].append(m)
        else:
            out.append([m])
    return out


def enforce(messages, budget=BUDGET):
    head, rest = messages[:2], [m for m in messages[2:] if not str(m.get("content") or "").startswith("[note: ")]
    cap = budget["tool_result_chars"]
    trimmed = []
    for m in rest:
        c = m.get("content")
        if m.get("role") == "tool" and isinstance(c, str) and len(c) > cap:
            m = dict(m, content=c[:cap] + f"\n[truncated: {len(c) - cap} more characters]")
        trimmed.append(m)
    groups = turns(trimmed)
    dropped = 0
    while len(groups) > 1 and sum(size(m) for g in groups for m in g) > budget["history_chars"]:
        groups.pop(0)
        dropped += 1
    body = [m for g in groups for m in g]
    note = [{"role": "user", "content": f"[note: {dropped} earlier steps were dropped to fit the context budget]"}] if dropped else []
    return head + note + body

EOF
cat > agent.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

from budget import enforce

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
        messages = enforce(messages)
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append({"role": "assistant", "content": msg.content,
                         "tool_calls": [{"id": c.id, "type": "function", "function": {"name": c.function.name, "arguments": c.function.arguments}}
                                        for c in msg.tool_calls]})
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)

EOF
python agent.py "Read every file in logs/ and tell me which has the slowest request." || true
```

</details>

## Check your work

```bash
D=/root/harness-lab/17-budget; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/budget.py 2>/dev/null && [ -s $D/budget.py ] && echo "✅ budget.py reads the key from the environment" || echo "❌ budget.py must not contain a key - let the SDK read it from the environment"
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
def valid(h):
    pending = set()
    for x in h:
        if x.get("role") == "tool":
            if x.get("tool_call_id") not in pending:
                return False
            pending.discard(x["tool_call_id"])
        else:
            if pending:
                return False
            pending = {c["id"] for c in x.get("tool_calls") or []}
    return not pending
def turn(i, n):
    return [{"role": "assistant", "content": None, "tool_calls": [{"id": f"c{i}", "type": "function", "function": {"name": "read_file", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": f"c{i}", "content": "x" * n}]
head = [{"role": "system", "content": "S"}, {"role": "user", "content": "task"}]
try:
    import budget as B
    small = head + turn(1, 100)
    ok(B.enforce(small) == small, "a history under budget is returned unchanged", f"enforce on a small history should change nothing - got {B.enforce(small)}")
    big = head + turn(1, 5000)
    r = B.enforce(big)
    c = r[-1]["content"]
    ok(c == "x" * 2000 + "\n[truncated: 3000 more characters]" and big[-1]["content"] == "x" * 5000, "a 5,000-char result is cut to 2,000 with a truncation marker (input untouched)", f"got {c[-60:]!r}")
    many = head + [m for i in range(1, 8) for m in turn(i, 1500)]
    r = B.enforce(many)
    body = [m for m in r[2:] if not str(m.get("content") or "").startswith("[note: ")]
    notes = [m for m in r if str(m.get("content") or "").startswith("[note: ")]
    kept = [m["tool_call_id"] for m in body if m["role"] == "tool"]
    ok(r[:2] == head and valid(r) and sum(len(json.dumps(m)) for m in body) <= 6000 and kept == [f"c{i}" for i in range(8 - len(kept), 8)], "old turns are dropped whole, oldest first, until the history fits", f"kept {kept}; size {sum(len(json.dumps(m)) for m in body)}; valid {valid(r)}")
    ok(len(notes) == 1 and r[2] == notes[0] and notes[0]["role"] == "user" and notes[0]["content"] == f"[note: {7 - len(kept)} earlier steps were dropped to fit the context budget]", "one note right after the task says how many steps were dropped", f"expected a single note at position 2 - got {notes}")
    again = B.enforce(r + turn(8, 1500))
    ok(sum(1 for m in again if str(m.get("content") or "").startswith("[note: ")) == 1, "running enforce again keeps a single, updated note", "a second enforce pass should replace the note, not add another")
    huge = head + turn(1, 1500) + [{"role": "assistant", "content": None, "tool_calls": [{"id": f"k{i}", "type": "function", "function": {"name": "read_file", "arguments": "{}"}} for i in range(4)]}] + [{"role": "tool", "tool_call_id": f"k{i}", "content": "y" * 1900} for i in range(4)]
    r = B.enforce(huge)
    ok([m.get("tool_call_id") for m in r if m["role"] == "tool"] == ["k0", "k1", "k2", "k3"], "the most recent turn is never dropped, even if it alone is over budget", "the last turn must always be kept")
except Exception as e:
    ok(False, "", f"budget.py should define enforce(messages, budget=BUDGET) - {type(e).__name__}: {e}")
script = [{"tool": "read_file", "args": {"path": f"logs/part{n}.log"}} for n in range(1, 7)] + ["part3.log has the slowest request (299ms)."]
with MockModel(rules=[{"match": "", "by": "calls", "steps": script}]) as m:
    rc, out, err = m.run(["python", "agent.py", "Which log has the slowest request?"], timeout=40)
sizes = [sum(len(json.dumps(x)) for x in r["messages"][2:] if not str(x.get("content") or "").startswith("[note: ")) for r in m.requests]
ok(rc == 0 and len(m.requests) == 7 and max(sizes) <= 6000 and all(valid(r["messages"]) for r in m.requests), "every request the agent sent was valid and within the 6,000-character history budget", f"history sizes per request: {sizes}; rc {rc}; {err[-200:]}")
ok(any("earlier steps were dropped" in json.dumps(r["messages"]) for r in m.requests), "the agent's later requests carry the dropped-steps note", "enforce should have dropped old turns and added the note during this run")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Budget each part and enforce it in the harness before every call.
- Truncate big results with a marker; drop whole old turns, never the task, the system prompt or the latest turn.
- Leave a note when steps are dropped, so the model knows its history was shortened.
