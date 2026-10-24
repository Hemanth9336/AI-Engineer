---
type: task
title: "Give the agent a notes file it reads and writes"
minutes: 9
---

## Set up

```bash
mkdir -p /root/harness-lab/19-memory/workspace/services
cd /root/harness-lab/19-memory
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

Extend `/root/harness-lab/19-memory/agent.py`:

1. Add a `save_note(note)` tool. It collapses whitespace, rejects empty notes and notes over 200 characters with an `error: ...` string (without writing anything), and otherwise appends `- <note>` as one line to `NOTES.md` **next to agent.py**, returning `saved: <note>`.
2. At the start of every run, build the system prompt from the original `SYSTEM` plus, if `NOTES.md` has any content, `\n\n## Notes from earlier sessions\n` followed by the file's contents.

```bash
cd /root/harness-lab/19-memory
python agent.py "Remember that the billing team's on-call this week is Priya."
cat NOTES.md
python agent.py "Who is on call for billing this week?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Keep the path relative to the file: `NOTES = Path(__file__).parent / "NOTES.md"`.
- Write the tool description so the model knows what deserves a note - and that secrets don't.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/19-memory
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
    {"type": "function", "function": {
        "name": "save_note",
        "description": "Save one short fact to your notes so you remember it in future sessions: the user's preferences and decisions, things you learned about the workspace. Never save secrets.",
        "parameters": {"type": "object", "properties": {
            "note": {"type": "string", "description": "One self-contained fact, at most 200 characters"}},
            "required": ["note"]}}},
]

WORK = Path(__file__).parent / "workspace"
NOTES = Path(__file__).parent / "NOTES.md"


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


def save_note(note):
    note = " ".join(str(note).split())
    if not note or len(note) > 200:
        return "error: a note must be 1-200 characters - save one short fact per note"
    with NOTES.open("a") as f:
        f.write(f"- {note}\n")
    return f"saved: {note}"


def system_prompt():
    notes = NOTES.read_text().strip() if NOTES.exists() else ""
    return SYSTEM + (f"\n\n## Notes from earlier sessions\n{notes}" if notes else "")


IMPL = {"list_dir": list_dir, "read_file": read_file, "save_note": save_note}


def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    try:
        return IMPL[name](**args)
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"


def run(question, max_steps=8):
    client = OpenAI()
    messages = [{"role": "system", "content": system_prompt()}, {"role": "user", "content": question}]
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
rm -f NOTES.md
python agent.py "Remember that the billing team's on-call this week is Priya."
cat NOTES.md
python agent.py "Who is on call for billing this week?"
```

</details>

## Check your work

```bash
D=/root/harness-lab/19-memory; cd $D 2>/dev/null || echo "❌ create $D"
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
notes = Path("NOTES.md")
saved = notes.read_text() if notes.exists() else None
try:
    notes.unlink(missing_ok=True)
    with MockModel([{"tool": "save_note", "args": {"note": "Deploys  are frozen\non Fridays after 15:00."}}, "Noted."]) as m:
        rc, out, err = m.run(["python", "agent.py", "Remember: no deploys on Friday afternoons."], timeout=20)
    names = [(t.get("function") or {}).get("name") for t in (m.requests[0].get("tools") or [])] if m.requests else []
    text = notes.read_text() if notes.exists() else ""
    ok(rc == 0 and "save_note" in names and text == "- Deploys are frozen on Fridays after 15:00.\n", "save_note appends one clean '- note' line to NOTES.md next to agent.py", f"NOTES.md is {text!r}; tools {names}; {err[-150:]}")
    ok(m.requests and m.requests[0]["messages"][0]["content"] == "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly.", "with no notes yet, the system prompt is unchanged", "before any note exists, the system prompt should be just SYSTEM")
    with MockModel(["Fridays after 15:00 are frozen."]) as m:
        rc, out, err = m.run(["python", "agent.py", "When can't I deploy?"], timeout=20)
    sysmsg = m.requests[0]["messages"][0]["content"] if m.requests else ""
    ok(sysmsg == "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly." + "\n\n## Notes from earlier sessions\n- Deploys are frozen on Fridays after 15:00.", "a new run loads the notes into the system prompt", f"system prompt was {sysmsg[-160:]!r}")
    with MockModel([{"tool": "save_note", "args": {"note": "x" * 300}}, "ok"]) as m:
        rc, out, err = m.run(["python", "agent.py", "Remember this."], timeout=20)
    res = [x.get("content", "") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
    ok(res and res[0].startswith("error:") and notes.read_text() == text, "a 300-character note is rejected with an error and not written", f"tool result {res[:1]}")
finally:
    if saved is None:
        notes.unlink(missing_ok=True)
    else:
        notes.write_text(saved)
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and (.tool_calls | index("save_note") != null))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the real model saved a note through your tool" || echo "❌ run the 'Remember that...' question - no save_note call in the gateway log"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Files are the agent's long-term memory: loaded at the start, written through a tool.
- The model decides what to remember; the harness controls format, size and location.
- Notes are loaded into every call - keep them short, factual and free of secrets.
