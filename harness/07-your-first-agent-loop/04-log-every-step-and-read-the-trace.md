---
type: task
title: "Log every step and read the trace"
minutes: 11
---

## Set up

`sample_trace.jsonl` is a trace from a teammate's run of the same agent.

```bash
mkdir -p /root/harness-lab/07-loop/workspace/services
cd /root/harness-lab/07-loop
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
cat > sample_trace.jsonl <<'EOF'
{"step": 1, "prompt_tokens": 410, "completion_tokens": 17, "tool_calls": [{"name": "list_dir", "args": {"path": "."}}], "results": ["README.md\nservices/"], "answer": null}
{"step": 2, "prompt_tokens": 690, "completion_tokens": 19, "tool_calls": [{"name": "read_file", "args": {"path": "README.md"}}], "results": ["# Stackline services\nTwo services run in production: billing and search."], "answer": null}
{"step": 3, "prompt_tokens": 980, "completion_tokens": 18, "tool_calls": [{"name": "list_dir", "args": {"path": "services"}}], "results": ["billing.yaml\nsearch.yaml"], "answer": null}
{"step": 4, "prompt_tokens": 1240, "completion_tokens": 22, "tool_calls": [{"name": "read_file", "args": {"path": "services/search.yaml"}}], "results": ["name: search\nport: 9200\nowner: discovery team\nreplicas: 5"], "answer": null}
{"step": 5, "prompt_tokens": 1510, "completion_tokens": 14, "tool_calls": [], "results": [], "answer": "The search service is owned by the discovery team."}
EOF
[ -f agent.py ] && echo 'agent.py found' || echo 'write agent.py first (previous task)'
```

## What to build

**Part 1 - log.** Change `/root/harness-lab/07-loop/agent.py` so that every model call appends one line to `trace.jsonl` (next to `agent.py`), in the format from the lesson:

`{"step", "prompt_tokens", "completion_tokens", "tool_calls": [{"name", "args"}], "results": [...], "answer"}`

- `step` counts model calls from 1.
- `prompt_tokens` and `completion_tokens` come from the response's `usage`.
- `results` holds each tool result cut to its first **200** characters, in call order; `answer` is the final text on the last step and `null` before it.
- Start a fresh `trace.jsonl` on every run.

**Part 2 - read.** Without running anything, read `sample_trace.jsonl` and write `trace_answers.json`:

```json
{"steps": 0, "files_read": ["..."], "total_prompt_tokens": 0, "wasted_steps": [0]}
```

- `files_read`: every `read_file` path, in order.
- `wasted_steps`: the step numbers whose result the final answer didn't need. The question was "Who owns the search service?"

```bash
cd /root/harness-lab/07-loop
python agent.py "Which port does the billing service use?"
cat trace.jsonl
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Open the trace with `"w"` once at the start of `run`, then append with `"a"` per step.
- `resp.usage.prompt_tokens` - keep `resp` around, not just the message.
- The answer came from `search.yaml`. Which steps' results weren't needed to find and read it?

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/07-loop
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


TRACE = Path(__file__).parent / "trace.jsonl"


def log(row):
    with open(TRACE, "a") as f:
        f.write(json.dumps(row) + "\n")


def run(question):
    client = OpenAI()
    TRACE.write_text("")
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    step = 0
    while True:
        step += 1
        resp = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages)
        msg = resp.choices[0].message
        row = {"step": step, "prompt_tokens": resp.usage.prompt_tokens, "completion_tokens": resp.usage.completion_tokens,
               "tool_calls": [], "results": [], "answer": None}
        if not msg.tool_calls:
            row["answer"] = msg.content
            log(row)
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = run_tool(call.function.name, args)
            row["tool_calls"].append({"name": call.function.name, "args": args})
            row["results"].append(result[:200])
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
        log(row)


if __name__ == "__main__":
    print(run(sys.argv[1]))

EOF
python agent.py "Which port does the billing service use?"
cat trace.jsonl
cat > trace_answers.json <<'EOF'
{"steps": 5, "files_read": ["README.md", "services/search.yaml"], "total_prompt_tokens": 4830, "wasted_steps": [2]}
EOF
```

</details>

## Check your work

```bash
D=/root/harness-lab/07-loop; cd $D 2>/dev/null || echo "❌ create $D"
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
script = [{"tool": "list_dir", "args": {"path": "services"}, "usage": [300, 11]},
          {"calls": [{"tool": "read_file", "args": {"path": "services/billing.yaml"}}, {"tool": "read_file", "args": {"path": "services/search.yaml"}}], "usage": [420, 23]},
          {"text": "Billing 8081, search 9200.", "usage": [610, 9]}]
Path("trace.jsonl").write_text("stale line from an old run\n") if Path("trace.jsonl").exists() else None
with MockModel(script) as m:
    rc, out, err = m.run(["python", "agent.py", "Ports of both services?"])
try:
    rows = [json.loads(l) for l in Path("trace.jsonl").read_text().splitlines() if l.strip()]
except Exception as e:
    rows = None
ok(rc == 0 and rows is not None and len(rows) == 3, "trace.jsonl holds one fresh JSON line per model call", f"after a 3-call run trace.jsonl should hold exactly 3 JSON lines (start fresh each run) - got {None if rows is None else len(rows)} {err[-200:]}")
if rows and len(rows) == 3:
    ok([r.get("step") for r in rows] == [1, 2, 3] and [(r.get("prompt_tokens"), r.get("completion_tokens")) for r in rows] == [(300, 11), (420, 23), (610, 9)], "steps count from 1 and token counts come from usage", f"step/prompt_tokens/completion_tokens should be 1/300/11, 2/420/23, 3/610/9 - got {[(r.get('step'), r.get('prompt_tokens'), r.get('completion_tokens')) for r in rows]}")
    ok(rows[1].get("tool_calls") == [{"name": "read_file", "args": {"path": "services/billing.yaml"}}, {"name": "read_file", "args": {"path": "services/search.yaml"}}], "a step with two calls logs both, with parsed args", f"step 2 tool_calls should list both read_file calls with args dicts - got {rows[1].get('tool_calls')}")
    res = rows[1].get("results") or []
    ok(len(res) == 2 and res[0].startswith("name: billing") and res[1].startswith("name: search") and all(len(x) <= 200 for x in res), "results are logged in call order, cut to 200 characters", f"step 2 results should be the two file texts (max 200 chars) - got {res}")
    ok(rows[0].get("answer") is None and rows[2].get("answer") == "Billing 8081, search 9200." and rows[2].get("tool_calls") == [], "answer is null until the final step", f"answer should be null on tool steps and the text on the last - got {[r.get('answer') for r in rows]}")
with MockModel([{"tool": "read_file", "args": {"path": "README.md"}}, "ok"]) as m:
    m.run(["python", "agent.py", "x"])
big = [json.loads(l) for l in Path("trace.jsonl").read_text().splitlines() if l.strip()] if Path("trace.jsonl").exists() else []
ok(len(big) == 2, "each run starts a fresh trace", f"a second 2-call run should leave 2 lines - found {len(big)}")
a = load("trace_answers.json") or {}
ok(a.get("steps") == 5 and a.get("files_read") == ["README.md", "services/search.yaml"], "trace_answers.json: 5 steps, files read in order", f"steps and files_read are wrong - got {a.get('steps')}, {a.get('files_read')}")
ok(a.get("total_prompt_tokens") == 4830, "trace_answers.json: total prompt tokens summed correctly", f"total_prompt_tokens should be the sum over all 5 steps - got {a.get('total_prompt_tokens')}")
ok(a.get("wasted_steps") == [2], "trace_answers.json: reading README.md was the wasted step", f"wasted_steps - the listings found search.yaml; one step's result added nothing to the answer - got {a.get('wasted_steps')}")
PYEOF
```

## What you learned

- Log one JSONL line per model call: tokens, tool calls with parsed args, short results, and the answer.
- A trace shows whether the agent looked before answering, read the right thing, and where it wasted steps.
- prompt_tokens grows every step because the whole history is re-sent.
