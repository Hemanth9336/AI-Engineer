---
type: task
title: "Run three subagents concurrently and merge results"
minutes: 11
---

## Set up

`subagent.py` has `subagent(task)` from topic 25 and the workspace tools.

```bash
mkdir -p /root/harness-lab/26-parallel
cd /root/harness-lab/26-parallel
mkdir -p /root/harness-lab/26-parallel/workspace/services
cd /root/harness-lab/26-parallel
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
cat > subagent.py <<'EOF'
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


SUB_SYSTEM = "You are a subagent. Do only the task you are given, using the tools, then reply with a short final report: the answer and the files you used. You cannot ask questions."


def subagent(task, max_steps=6):
    client = OpenAI()
    messages = [{"role": "system", "content": SUB_SYSTEM}, {"role": "user", "content": task}]
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return (msg.content or "")[:1500]
        messages.append(msg)
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"subagent stopped: reached max steps ({max_steps})"
EOF
echo 'subagent.py is the subagent from topic 25'
```

## What to build

Write `/root/harness-lab/26-parallel/fanout.py`:

1. `TASKS` - these three, in this order:
   - `Read services/billing.yaml and report the service's port and owner.`
   - `Read services/search.yaml and report the service's port and owner.`
   - `Read README.md and list the services it mentions.`
2. `run_all(tasks, workers=3)` runs `subagent(task)` for each task **concurrently** and returns the reports **in task order**. If a subagent raises, its report is `error: <ExceptionType>: <message>` and the others still complete.
3. Running `python fanout.py` writes `report.json`: `{"results": [{"task": ..., "answer": ...}, ...], "seconds": <wall-clock time>}` and prints it.

```bash
cd /root/harness-lab/26-parallel
python fanout.py
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `ThreadPoolExecutor.map` keeps the input order.
- Catch exceptions inside the function you submit, not around `map`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/26-parallel
cat > fanout.py <<'EOF'
"""Run independent subagents at the same time and merge their reports. Usage: python fanout.py"""
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from subagent import subagent

TASKS = [
    "Read services/billing.yaml and report the service's port and owner.",
    "Read services/search.yaml and report the service's port and owner.",
    "Read README.md and list the services it mentions.",
]


def safe(task):
    try:
        return subagent(task)
    except Exception as e:
        return f"error: {type(e).__name__}: {e}"


def run_all(tasks, workers=3):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(safe, tasks))


if __name__ == "__main__":
    start = time.time()
    answers = run_all(TASKS)
    report = {"results": [{"task": t, "answer": a} for t, a in zip(TASKS, answers)], "seconds": round(time.time() - start, 2)}
    (Path(__file__).parent / "report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))

EOF
python fanout.py
```

</details>

## Check your work

```bash
D=/root/harness-lab/26-parallel; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/fanout.py 2>/dev/null && [ -s $D/fanout.py ] && echo "✅ fanout.py reads the key from the environment" || echo "❌ fanout.py must not contain a key - let the SDK read it from the environment"
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
import os, time
sys.path.insert(0, ".")
def slow(match, path, answer):
    return {"match": match, "steps": [{"tool": "read_file", "args": {"path": path}, "delay": 1.0}, {"text": answer, "delay": 1.0}]}
rules_ = [slow("billing.yaml and report", "services/billing.yaml", "billing: port 8081, payments team"),
          slow("search.yaml and report", "services/search.yaml", "search: port 9200, discovery team"),
          slow("README.md and list", "README.md", "README mentions billing and search"),
          {"match": "broken", "steps": [{"tool": "read_file", "raw_args": "{not json"}, "never"]}]
with MockModel(rules=rules_) as m:
    Path("report.json").unlink(missing_ok=True)
    t = time.time()
    rc, out, err = m.run(["python", "fanout.py"], timeout=40)
    took = time.time() - t
    conc = m.max_concurrency()
rep = load("report.json") or {}
res = rep.get("results") or []
want = [("billing.yaml and report", "billing: port 8081"), ("search.yaml and report", "search: port 9200"), ("README.md and list", "README mentions")]
ok(rc == 0 and len(res) == 3 and all(w[0] in r.get("task", "") and r.get("answer", "").startswith(w[1]) for w, r in zip(want, res)), "report.json has the three reports, in task order", f"results: {res}; rc {rc}; {err[-150:]}")
ok(conc >= 3 and took < 4.5, f"the three subagents ran concurrently ({took:.1f}s for three 2-second subagents)", f"took {took:.1f}s with at most {conc} requests at once - they should overlap")
ok(isinstance(rep.get("seconds"), (int, float)) and 1.5 < rep["seconds"] < 4.5, "report.json records the wall-clock time", f"seconds = {rep.get('seconds')}")
try:
    with MockModel(rules=rules_) as m:
        os.environ.update(OPENAI_BASE_URL=m.url, OPENAI_API_KEY="mock")
        from fanout import run_all
        got = run_all(["Read services/billing.yaml and report the service's port and owner.", "broken task", "Read README.md and list the services it mentions."])
    ok(len(got) == 3 and got[0].startswith("billing: port 8081") and got[1].startswith("error: ") and got[2].startswith("README mentions"), "one failing subagent becomes an error report; the others still finish", f"got {[str(g)[:60] for g in got]}")
except Exception as e:
    ok(False, "", f"run_all should catch each subagent's exception - {type(e).__name__}: {e}")
PYEOF
jq -se '[.[] | select(.ok and .model == "lab-fast" and .system)] | length >= 3' /var/log/ailab/requests.jsonl | grep -q true && echo "✅ the gateway logged your subagents' calls" || echo "❌ run fanout.py against the gateway - fewer than 3 subagent calls logged"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Independent subtasks can run concurrently; model calls mostly wait on the network.
- A thread pool with map keeps results in task order, so merging stays deterministic.
- Catch failures per subagent so one error doesn't lose every other result.
