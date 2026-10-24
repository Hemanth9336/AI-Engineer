---
type: task
title: "The agent resumes after restart using its notes"
minutes: 10
---

## Set up

`workspace/logs/` has four small logs. Keep `save_note` and `NOTES.md` from the previous task - you're adding a second file, `state.json`, for progress.

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
python - <<'EOF'
from pathlib import Path
Path('workspace/logs').mkdir(parents=True, exist_ok=True)
for n in range(1, 5):
    Path(f'workspace/logs/part{n}.log').write_text(''.join(f'line {n}.{i} INFO search request ok {i * 7 % 300}ms\n' for i in range(30)))
EOF
```

## What to build

Make `/root/harness-lab/19-memory/agent.py` resumable:

1. Arguments: `python agent.py "question" [--max-steps N]` or `python agent.py --resume [--max-steps N]` (default 8 steps).
2. Store assistant messages as plain dicts. After every complete step (assistant message + all its tool results), write `state.json` next to agent.py: `{"question": ..., "messages": [...]}`.
3. When the model gives a final answer, delete `state.json`.
4. On the step limit, print `stopped: reached max steps (N) - run with --resume to continue` and exit 2, leaving `state.json` in place.
5. `--resume` loads `state.json` and continues the loop from the saved messages (with a fresh step limit). With no `state.json`, it prints an error to stderr and exits 1.

```bash
cd /root/harness-lab/19-memory
python agent.py "Read logs/part1.log and logs/part2.log, then tell me how many lines each has." --max-steps 1 || echo "stopped with exit $?"
python -c "import json; s = json.load(open('state.json')); print(len(s['messages']), 'messages saved')"
python agent.py --resume
ls state.json 2>/dev/null || echo "state.json removed"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `argparse` with `nargs="?"` lets the question be optional when `--resume` is given.
- Pass the loaded messages into `run()` and keep appending to them - the model sees the whole history it had before.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/19-memory
cat > agent.py <<'EOF'
import argparse
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
STATE = Path(__file__).parent / "state.json"


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


def save_state(question, messages):
    STATE.write_text(json.dumps({"question": question, "messages": messages}, indent=1))


def run(question, max_steps=8, messages=None):
    client = OpenAI()
    messages = messages or [{"role": "system", "content": system_prompt()}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            STATE.unlink(missing_ok=True)
            return msg.content
        messages.append({"role": "assistant", "content": msg.content,
                         "tool_calls": [{"id": c.id, "type": "function", "function": {"name": c.function.name, "arguments": c.function.arguments}}
                                        for c in msg.tool_calls]})
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
        save_state(question, messages)
    return f"stopped: reached max steps ({max_steps}) - run with --resume to continue"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--max-steps", type=int, default=8)
    a = ap.parse_args()
    if a.resume:
        if not STATE.exists():
            print("error: nothing to resume - there is no state.json", file=sys.stderr)
            sys.exit(1)
        saved = json.loads(STATE.read_text())
        answer = run(saved["question"], a.max_steps, saved["messages"])
    elif a.question:
        answer = run(a.question, a.max_steps)
    else:
        ap.error("give a question, or --resume")
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)

EOF
rm -f state.json
python agent.py "Read logs/part1.log and logs/part2.log, then tell me how many lines each has." --max-steps 1 || echo "stopped with exit $?"
python -c "import json; s = json.load(open('state.json')); print(len(s['messages']), 'messages saved')"
python agent.py --resume
ls state.json 2>/dev/null || echo "state.json removed"
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

state = Path("state.json")
state.unlink(missing_ok=True)
script = [{"tool": "read_file", "args": {"path": f"logs/part{n}.log"}} for n in range(1, 5)] + ["All four logs have 30 lines."]
Q = "Count the lines in logs/part1.log to logs/part4.log."
with MockModel(script) as m:
    rc, out, err = m.run(["python", "agent.py", Q, "--max-steps", "2"], timeout=20)
    saved = json.loads(state.read_text()) if state.exists() else {}
    msgs = saved.get("messages") or []
    ok(rc == 2 and "--resume" in out and saved.get("question") == Q and valid(msgs) and sum(1 for x in msgs if x.get("role") == "assistant") == 2 and "line 2.0 " in json.dumps(msgs),
       "a run stopped at the step limit exits 2 and leaves state.json with the question and both steps", f"exit {rc}, output {out[-100:]!r}, state.json has {len(msgs)} messages; {err[-150:]}")
    n = len(m.requests)
    rc, out, err = m.run(["python", "agent.py", "--resume"], timeout=20)
    after = m.requests[n:]
    called = [c["function"]["name"] + ":" + c["function"]["arguments"] for x in (after[-1]["messages"][len(msgs):] if after else []) for c in (x.get("tool_calls") or [])]
    ok(rc == 0 and out.endswith("All four logs have 30 lines.") and after and after[0]["messages"] == msgs,
       "--resume sends the saved history and finishes the task", f"exit {rc}, output {out[-80:]!r}, first resumed request had {len(after[0]['messages']) if after else 0} messages (saved: {len(msgs)}); {err[-150:]}")
    ok(called == [f'read_file:{{"path": "logs/part{n}.log"}}' for n in (3, 4)], "the resumed run continues with part3 and part4 instead of starting over", f"tool calls after resuming: {called}")
    ok(not state.exists(), "state.json is deleted once the task is done", "a finished task should remove state.json")
    rc, out, err = m.run(["python", "agent.py", "--resume"], timeout=20)
    ok(rc == 1 and err, "--resume with nothing to resume exits 1 with an error", f"exit {rc}, stderr {err[-120:]!r}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and (.roles | map(select(. == "assistant")) | length) >= 1)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the real model continued a resumed history" || echo "❌ run the --max-steps 1 then --resume commands - no resumed request in the gateway log"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Persist decisions, progress and expensive stable results; recompute anything that can change.
- Checkpoint the message list after every complete step, and delete it when the task is done.
- Resuming is loading the history and continuing the loop - side effects must not run twice.
