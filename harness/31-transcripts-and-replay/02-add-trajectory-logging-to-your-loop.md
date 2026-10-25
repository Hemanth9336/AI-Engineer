---
type: task
title: "Add trajectory logging to your loop"
minutes: 9
---

## Set up

```bash
mkdir -p /root/harness-lab/31-transcripts/workspace/services
cd /root/harness-lab/31-transcripts
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
echo 'agent.py is the eval-ready agent from topic 30'
```

## What to build

Make `/root/harness-lab/31-transcripts/agent.py` write a transcript for every run to `transcripts/<run_id>.jsonl` (a new file per run). Every line has `type`, `run_id` and `ts`, plus:

| type | fields |
|---|---|
| `run_start` | `task`, `model`, `system` |
| `model_call` | `step`, `model`, `messages` (how many were sent), `prompt_tokens`, `completion_tokens`, `latency_ms`, `finish_reason`, `content`, `tool_calls` (list of `{name, arguments}`) |
| `tool_call` | `step`, `name`, `args` (a dict), `result` (the full text), `error` (true if the result starts with `error`) |
| `run_end` | `status` (`done` or `max_steps`), `answer`, `steps`, `total_tokens` |

Steps are numbered from 0, one per model call. Keep `trace.jsonl` working as before.

```bash
cd /root/harness-lab/31-transcripts
python agent.py "Which port does the billing service use?"
ls transcripts/
cat transcripts/*.jsonl | python -c "import sys, json; [print(json.loads(l)['type']) for l in sys.stdin]"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `resp.usage.prompt_tokens` and `resp.choices[0].finish_reason` come from the response object, not the message.
- Write `run_end` in both exits: the final answer and the step limit.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/31-transcripts
cat > agent.py <<'EOF'
import json
import os
import time
import uuid
import sys
from pathlib import Path

from openai import OpenAI

SYSTEM = Path(os.environ["PROMPT_FILE"]).read_text().strip() if os.environ.get("PROMPT_FILE") else "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Never delete files. Answer briefly."
TRACE = Path(__file__).parent / "trace.jsonl"
TRANSCRIPTS = Path(__file__).parent / "transcripts"
MODEL = "lab-fast"

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


class Transcript:
    def __init__(self, task):
        TRANSCRIPTS.mkdir(exist_ok=True)
        self.run_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        self.path = TRANSCRIPTS / f"{self.run_id}.jsonl"
        self.write("run_start", task=task, model=MODEL, system=SYSTEM)

    def write(self, type_, **data):
        with self.path.open("a") as f:
            f.write(json.dumps({"type": type_, "run_id": self.run_id, "ts": round(time.time(), 3), **data}) + "\n")


def run(question, max_steps=8):
    client = OpenAI()
    tr = Transcript(question)
    total = 0
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    TRACE.write_text("")
    for step in range(max_steps):
        start = time.time()
        resp = client.chat.completions.create(model=MODEL, tools=SCHEMAS, messages=messages)
        msg, u = resp.choices[0].message, resp.usage
        total += u.prompt_tokens + u.completion_tokens
        tr.write("model_call", step=step, model=MODEL, messages=len(messages), prompt_tokens=u.prompt_tokens, completion_tokens=u.completion_tokens,
                 latency_ms=round((time.time() - start) * 1000), finish_reason=resp.choices[0].finish_reason,
                 content=msg.content, tool_calls=[{"name": c.function.name, "arguments": c.function.arguments} for c in msg.tool_calls or []])
        if not msg.tool_calls:
            tr.write("run_end", status="done", answer=msg.content, steps=step + 1, total_tokens=total)
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = run_tool(call.function.name, args)
            tr.write("tool_call", step=step, name=call.function.name, args=args, result=result, error=str(result).startswith("error"))
            with TRACE.open("a") as f:
                f.write(json.dumps({"step": step, "tool": call.function.name, "args": args}) + "\n")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    tr.write("run_end", status="max_steps", answer=None, steps=max_steps, total_tokens=total)
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)

EOF
python agent.py "Which port does the billing service use?"
ls transcripts/
```

</details>

## Check your work

```bash
D=/root/harness-lab/31-transcripts; cd $D 2>/dev/null || echo "❌ create $D"
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
before = set(Path("transcripts").glob("*.jsonl")) if Path("transcripts").exists() else set()
script = [{"tool": "read_file", "args": {"path": "services/billing.yaml"}, "usage": [300, 20]}, {"tool": "read_file", "args": {"path": "nope.txt"}, "usage": [350, 15]}, {"text": "Billing uses port 8081.", "usage": [400, 10]}]
with MockModel(script) as m:
    rc, out, err = m.run(["python", "agent.py", "Which port does billing use?"], timeout=30)
new = sorted(set(Path("transcripts").glob("*.jsonl")) - before) if Path("transcripts").exists() else []
ok(rc == 0 and len(new) == 1, "one new transcript file per run in transcripts/", f"new transcript files: {[p.name for p in new]}; rc {rc}; {err[-150:]}")
ev = [json.loads(l) for l in new[0].read_text().splitlines() if l.strip()] if new else []
types = [e.get("type") for e in ev]
ok(types == ["run_start", "model_call", "tool_call", "model_call", "tool_call", "model_call", "run_end"], "events are in order: start, model, tool, model, tool, model, end", f"types: {types}")
ok(ev and len({e.get("run_id") for e in ev}) == 1 and new[0].stem == ev[0].get("run_id") and all(isinstance(e.get("ts"), (int, float)) for e in ev), "every line has the run's id and a timestamp; the file is named after the run id", f"run ids: {sorted({str(e.get('run_id')) for e in ev})}")
if len(ev) == 7:
    s, m0, t0, m1, t1, m2, end = ev
    ok(s.get("task") == "Which port does billing use?" and s.get("model") == "lab-fast" and s.get("system"), "run_start has the task, model and system prompt", f"run_start: {s}")
    ok([x.get("step") for x in (m0, m1, m2)] == [0, 1, 2] and [x.get("prompt_tokens") for x in (m0, m1, m2)] == [300, 350, 400] and [x.get("completion_tokens") for x in (m0, m1, m2)] == [20, 15, 10]
       and [x.get("finish_reason") for x in (m0, m1, m2)] == ["tool_calls", "tool_calls", "stop"] and all(isinstance(x.get("latency_ms"), (int, float)) and x["latency_ms"] >= 0 for x in (m0, m1, m2))
       and m0.get("messages") == 2 and m1.get("messages") == 4 and m0.get("tool_calls") == [{"name": "read_file", "arguments": '{"path": "services/billing.yaml"}'}] and m2.get("content") == "Billing uses port 8081.",
       "model_call events record step, message count, tokens, latency, finish reason, text and tool calls", f"model_calls: {[{k: x.get(k) for k in ('step', 'messages', 'prompt_tokens', 'finish_reason')} for x in (m0, m1, m2)]}")
    ok(t0.get("name") == "read_file" and t0.get("args") == {"path": "services/billing.yaml"} and "port: 8081" in t0.get("result", "") and t0.get("error") is False and t1.get("error") is True and t1.get("step") == 1,
       "tool_call events record the full result and flag errors", f"tool_calls: {t0}, {t1}")
    ok(end.get("status") == "done" and end.get("answer") == "Billing uses port 8081." and end.get("steps") == 3 and end.get("total_tokens") == 1095, "run_end has the status, answer, steps and total tokens (1,095)", f"run_end: {end}")
before = set(Path("transcripts").glob("*.jsonl"))
with MockModel([{"tool": "list_dir", "args": {"path": "."}}]) as m:
    m.run(["python", "agent.py", "loop forever"], timeout=40)
new = sorted(set(Path("transcripts").glob("*.jsonl")) - before)
last = json.loads(new[0].read_text().splitlines()[-1]) if new else {}
ok(last.get("type") == "run_end" and last.get("status") == "max_steps", "a run that hits the step limit ends with status max_steps", f"last event: {last}")
ok(Path("trace.jsonl").exists() and Path("trace.jsonl").read_text().strip(), "trace.jsonl still works", "keep writing trace.jsonl for the eval runner")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ you logged a real run" || echo "❌ run agent.py against the gateway"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A transcript records every model call and tool call of a run, in order, under one run ID.
- Full tool results, tokens, latency and finish reasons are what you'll need when debugging.
- Transcripts hold sensitive data: redact them and control who can read them.
