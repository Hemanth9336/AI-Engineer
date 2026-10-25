---
type: task
title: "Find the wrong turn in a bad transcript"
minutes: 10
---

## Set up

`bad_run.jsonl` is the transcript of a run that answered the billing port question wrong: the real port is 8081.

```bash
mkdir -p /root/harness-lab/31-transcripts
cd /root/harness-lab/31-transcripts
cat > bad_run.jsonl <<'EOF'
{"type": "run_start", "run_id": "20260314-091502-a41f0c", "ts": 1773479702.0, "task": "Which port does the billing service use?", "model": "lab-fast", "system": "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Never delete files. Answer briefly."}
{"type": "model_call", "run_id": "20260314-091502-a41f0c", "ts": 1773479702.4, "step": 0, "model": "lab-fast", "messages": 2, "prompt_tokens": 412, "completion_tokens": 18, "latency_ms": 640, "finish_reason": "tool_calls", "content": null, "tool_calls": [{"name": "list_dir", "arguments": "{\"path\": \"services\"}"}]}
{"type": "tool_call", "run_id": "20260314-091502-a41f0c", "ts": 1773479702.8, "step": 0, "name": "list_dir", "args": {"path": "services"}, "result": "billing.yaml\nsearch.yaml", "error": false}
{"type": "model_call", "run_id": "20260314-091502-a41f0c", "ts": 1773479703.2, "step": 1, "model": "lab-fast", "messages": 4, "prompt_tokens": 455, "completion_tokens": 21, "latency_ms": 702, "finish_reason": "tool_calls", "content": null, "tool_calls": [{"name": "read_file", "arguments": "{\"path\": \"services/billing.yaml\"}"}]}
{"type": "tool_call", "run_id": "20260314-091502-a41f0c", "ts": 1773479703.6, "step": 1, "name": "read_file", "args": {"path": "services/billing.yaml"}, "result": "name: billing\nowner: payments team\n[truncated: 30 more characters]", "error": false}
{"type": "model_call", "run_id": "20260314-091502-a41f0c", "ts": 1773479704.0, "step": 2, "model": "lab-fast", "messages": 6, "prompt_tokens": 503, "completion_tokens": 17, "latency_ms": 655, "finish_reason": "tool_calls", "content": null, "tool_calls": [{"name": "read_file", "arguments": "{\"path\": \"README.md\"}"}]}
{"type": "tool_call", "run_id": "20260314-091502-a41f0c", "ts": 1773479704.4, "step": 2, "name": "read_file", "args": {"path": "README.md"}, "result": "# Stackline services\nTwo services run in production: billing and search.\nConfig lives in services/<name>.yaml.\n", "error": false}
{"type": "model_call", "run_id": "20260314-091502-a41f0c", "ts": 1773479704.8, "step": 3, "model": "lab-fast", "messages": 8, "prompt_tokens": 571, "completion_tokens": 24, "latency_ms": 810, "finish_reason": "stop", "content": "Billing most likely uses port 8080, the usual default for HTTP services.", "tool_calls": []}
{"type": "run_end", "run_id": "20260314-091502-a41f0c", "ts": 1773479705.2, "status": "done", "answer": "Billing most likely uses port 8080, the usual default for HTTP services.", "steps": 4, "total_tokens": 2021}
EOF
```

## What to build

Read `bad_run.jsonl` and find the **first** step where the run went wrong. Write `/root/harness-lab/31-transcripts/diagnosis.json`:

```json
{"wrong_step": 0, "category": "...", "evidence": "...", "fix": "..."}
```

- `wrong_step` - the step number of the first wrong turn.
- `category` - one of `prompt`, `tool_description`, `tool_result`, `model_reasoning`, `harness_loop`.
- `evidence` - what in the transcript shows it (quote what you see).
- `fix` - what you'd change, in a sentence or two.

```bash
cd /root/harness-lab/31-transcripts
python -c "
import json
for l in open('bad_run.jsonl'):
    e = json.loads(l)
    print(e['type'], e.get('step', ''), e.get('name', ''), json.dumps(e.get('result') or e.get('content') or e.get('answer') or '')[:120])"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The final answer is where the problem shows, not where it starts.
- Compare each tool result to the real file: `services/billing.yaml` has four lines.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/31-transcripts
cat > diagnosis.json <<'EOF'
{"wrong_step": 1, "category": "tool_result", "evidence": "At step 1 read_file returned billing.yaml truncated after 'owner: payments team' - the port line was cut off by the harness, so the model never saw port 8081 and guessed 8080.", "fix": "Raise the read_file truncation limit (40 characters is far too small) and keep small config files whole; then add an eval task for the billing port."}
EOF
```

</details>

## Check your work

```bash
D=/root/harness-lab/31-transcripts; cd $D 2>/dev/null || echo "❌ create $D"
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
d = load("diagnosis.json") or {}
cats = ["prompt", "tool_description", "tool_result", "model_reasoning", "harness_loop"]
ok(d.get("category") in cats, "the category is one of the five", f"category must be one of {cats} - got {d.get('category')!r}")
ok(d.get("wrong_step") == 1, "you found the first wrong turn: step 1, not the final answer", f"wrong_step {d.get('wrong_step')} - which step first gave the model incomplete information?")
ok(d.get("category") == "tool_result", "the cause is the tool result the model saw", f"category {d.get('category')!r} - did the model have the information it needed at that step?")
ok("truncat" in str(d.get("evidence", "")).lower() and "8081" not in json.dumps([json.loads(l).get("result") for l in open("bad_run.jsonl")]), "the evidence points at the truncated read_file result", "quote what the transcript shows at that step")
ok(len(str(d.get("fix", ""))) >= 20, "you proposed a fix", "add a sentence about what to change")
PYEOF
```

## What you learned

- Find the first wrong turn, not the final wrong answer - that's where the fix goes.
- Check what the model saw at each step; a starved model looks like a reasoning failure.
- Classify the cause to know where the fix lives, then add a golden task for it.
