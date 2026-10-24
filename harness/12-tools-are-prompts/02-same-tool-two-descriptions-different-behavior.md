---
type: task
title: "Same tool, two descriptions, different behavior"
minutes: 9
---

## Set up

`tools.py` holds the vague `SEARCH_V1`. `questions.txt` has five on-call questions that should all be answered from logs.

```bash
mkdir -p /root/harness-lab/12-tool-prompts
cd /root/harness-lab/12-tool-prompts
cat > tools.py <<'EOF'
SEARCH_V1 = {
    "type": "function",
    "function": {
        "name": "search_logs",
        "description": "Searches logs.",
        "parameters": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string"
                }
            },
            "required": [
                "q"
            ]
        }
    }
}
EOF
cat > questions.txt <<'EOF'
Were there any timeouts in the search service in the last hour?
Why did billing return 500 errors this morning?
How many ERROR lines did search log in the last 24 hours?
Did the billing deploy at 09:00 cause errors?
Is search slower than usual in the last 6 hours?
EOF
```

## What to build

1. In `/root/harness-lab/12-tool-prompts/tools.py`, add `SEARCH_V2`: the **same tool name** `search_logs`, with
   - a description of at least 80 characters that says what it searches and **when to use it**;
   - properties `service` (an `enum` of `billing` and `search`), `query` (string) and `since_hours` (integer), **each with a description**;
   - `required` containing `service` and `query`.
2. Write `compare.py`, used as `python compare.py QUESTIONS_FILE OUT_FILE`. For every question, and for each version (`v1` then `v2`), make **one** `lab-fast` call with the system message `You are Stackline's on-call assistant.`, the question, and `tools=[that version]`. Record:

   `{"question": ..., "version": "v1" or "v2", "called": true/false, "args": {...} or null}`

   Write the list to OUT_FILE and print two lines: `v1: called X/5` and `v2: called Y/5`.

```bash
cd /root/harness-lab/12-tool-prompts
python compare.py questions.txt results.json
```

Look at the args too, not just the counts: which version gets a usable `service`?

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `for version, tool in (("v1", SEARCH_V1), ("v2", SEARCH_V2)):` inside the loop over questions.
- `called = bool(msg.tool_calls)`; `args = json.loads(msg.tool_calls[0].function.arguments) if called else None`.
- The checker runs compare.py against labmock with a model that only calls tools whose definition is clear.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/12-tool-prompts
cat >> tools.py <<'EOF'

SEARCH_V2 = {
    "type": "function",
    "function": {
        "name": "search_logs",
        "description": "Search one Stackline service's application logs for lines matching a query. Use it for any question about errors, timeouts, crashes or slow requests in billing or search. Returns at most 20 matching lines, newest first.",
        "parameters": {
            "type": "object",
            "properties": {
                "service": {"type": "string", "enum": ["billing", "search"], "description": "Which service's logs to search"},
                "query": {"type": "string", "description": "Text to look for, for example timeout or HTTP 500"},
                "since_hours": {"type": "integer", "description": "How far back to look, in hours. Default 24."},
            },
            "required": ["service", "query"],
        },
    },
}
EOF
cat > compare.py <<'EOF'
import json
import sys

from openai import OpenAI

from tools import SEARCH_V1, SEARCH_V2

client = OpenAI()
questions = [l.strip() for l in open(sys.argv[1]) if l.strip()]
rows = []
for q in questions:
    for version, tool in (("v1", SEARCH_V1), ("v2", SEARCH_V2)):
        msg = client.chat.completions.create(model="lab-fast", tools=[tool], messages=[
            {"role": "system", "content": "You are Stackline's on-call assistant."},
            {"role": "user", "content": q}]).choices[0].message
        called = bool(msg.tool_calls)
        args = json.loads(msg.tool_calls[0].function.arguments) if called else None
        rows.append({"question": q, "version": version, "called": called, "args": args})
json.dump(rows, open(sys.argv[2], "w"), indent=2)
for version in ("v1", "v2"):
    n = sum(r["called"] for r in rows if r["version"] == version)
    print(f"{version}: called {n}/{len(questions)}")
EOF
python compare.py questions.txt results.json
```

</details>

## Check your work

```bash
D=/root/harness-lab/12-tool-prompts; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/compare.py 2>/dev/null && [ -s $D/compare.py ] && echo "✅ compare.py reads the key from the environment" || echo "❌ compare.py must not contain a key - let the SDK read it from the environment"
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
try:
    from tools import SEARCH_V2
    f = SEARCH_V2["function"]
    props = f["parameters"]["properties"]
    good = (f.get("name") == "search_logs" and len(f.get("description", "")) >= 80 and "use" in f["description"].lower()
            and sorted(props.get("service", {}).get("enum", [])) == ["billing", "search"] and props.get("since_hours", {}).get("type") == "integer"
            and props.get("query", {}).get("type") == "string" and all(len(p.get("description", "")) >= 5 for p in props.values())
            and {"service", "query"} <= set(f["parameters"].get("required", [])))
except Exception as e:
    good, f = False, {"error": str(e)}
ok(good, "SEARCH_V2 says when to use it, constrains service with an enum and describes every parameter", f"SEARCH_V2 needs name search_logs, an 80+ character description saying when to use it, service enum [billing, search], query string, since_hours integer, a description on every property, required service and query - got {str(f)[:300]}")
rules = [{"match": "Searches logs\\.\"", "on": "tools", "steps": ["I don't have enough information to check that."]},
         {"match": "search_logs", "on": "tools", "steps": [{"tool": "search_logs", "args": {"service": "search", "query": "timeout", "since_hours": 1}}]}]
with MockModel(rules=rules) as m:
    rc, out, err = m.run(["python", "compare.py", "questions.txt", "/tmp/h12.json"], timeout=60)
rows = load("/tmp/h12.json") or []
qs = [l.strip() for l in open("questions.txt") if l.strip()]
ok(len(m.requests) == 10 and all(len(r.get("tools") or []) == 1 for r in m.requests), "compare.py makes one call per question per version, each offering one tool", f"expected 10 calls each with exactly one tool - labmock saw {len(m.requests)}")
ok(all((r.get("messages") or [{}])[0].get("content") == "You are Stackline's on-call assistant." for r in m.requests), "every call uses the on-call system message", "each call should start with the system message 'You are Stackline's on-call assistant.'")
want = [{"question": q, "version": v, "called": v == "v2", "args": {"service": "search", "query": "timeout", "since_hours": 1} if v == "v2" else None} for q in qs for v in ("v1", "v2")]
ok(rows == want, "OUT_FILE records called and parsed args for each question and version, in order", f"with a model that ignores v1 and calls v2, the rows should be {want[:2]}... - got {rows[:2]}")
ok(out.splitlines()[-2:] == ["v1: called 0/5", "v2: called 5/5"], "the summary lines count tool calls per version", f"expected 'v1: called 0/5' and 'v2: called 5/5' - got {out[-120:]!r} {err[-200:]}")
real = load("results.json")
ok(isinstance(real, list) and len(real) == 10 and all(set(r) == {"question", "version", "called", "args"} for r in real), "results.json from your real run has 10 rows", "run compare.py against the lab gateway to produce results.json (10 rows)")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- The model chooses tools from the name, description and schema alone - they are prompts.
- Say what the tool does, when to use it and what it returns; constrain parameters with enums and types.
- Compare tool definitions with a small experiment, not by reading them.
