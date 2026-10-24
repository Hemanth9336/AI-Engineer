---
type: task
title: "Race two models on the same prompt"
minutes: 9
---

## Set up

```bash
ailab status
mkdir -p /root/fde-lab/07-models
```

## What to build

Write `/root/fde-lab/07-models/race.py`, used as `python race.py PROMPT`:

1. Send PROMPT as a user message to `lab-mini` and then `lab-smart`, each with `max_tokens=200`.
2. Time each call with `time.perf_counter()`.
3. Print a JSON list, one object per model, in that order:
   `{"model", "seconds" (rounded to 3), "completion_tokens", "reply"}`

```bash
cd /root/fde-lab/07-models
python race.py "Explain in three sentences why a parcel might be held at customs." > race.json
cat race.json
```

On a real provider the larger model is usually slower. Try a few prompts.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `start = time.perf_counter()` before the call, `round(time.perf_counter() - start, 3)` after.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/07-models
cat > race.py <<'EOF'
import json
import sys
import time

from openai import OpenAI

client = OpenAI()
results = []
for model in ["lab-mini", "lab-smart"]:
    start = time.perf_counter()
    resp = client.chat.completions.create(model=model, max_tokens=200, messages=[{"role": "user", "content": sys.argv[1]}])
    results.append({
        "model": model,
        "seconds": round(time.perf_counter() - start, 3),
        "completion_tokens": resp.usage.completion_tokens,
        "reply": resp.choices[0].message.content,
    })
print(json.dumps(results, indent=2))
EOF
python race.py "Explain in three sentences why a parcel might be held at customs." > race.json
cat race.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/07-models; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/race.py 2>/dev/null && [ -s $D/race.py ] && echo "✅ race.py reads the key from the environment" || echo "❌ race.py must not contain a key - let the SDK read it from the environment"
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
def good(r):
    return (isinstance(r, list) and [x.get("model") for x in r] == ["lab-mini", "lab-smart"]
            and all(isinstance(x.get("seconds"), (int, float)) and x["seconds"] > 0 and round(x["seconds"], 3) == x["seconds"]
                    and isinstance(x.get("completion_tokens"), int) and x["completion_tokens"] > 0 and x.get("reply") for x in r))
ok(good(load("race.json")), "race.json has timed results for lab-mini then lab-smart", "race.json should list lab-mini then lab-smart with seconds, completion_tokens and reply")
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("race.py", "List two reasons a delivery van might be late.")
try:
    r = json.loads(out)
except ValueError:
    r = None
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
ok(good(r), "a new prompt is raced and printed as JSON", f"python race.py PROMPT should print the JSON list - got {out[:200]!r} {err[-150:]}")
ok([x.get("model") for x in rows if x.get("api") == "chat.completions"] == ["lab-mini", "lab-smart"] and all(x.get("max_tokens") == 200 for x in rows if x.get("api") == "chat.completions"), "one call to each model, with max_tokens 200", "expected exactly one lab-mini then one lab-smart call with max_tokens=200")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Measure latency on the customer's own prompts, not on benchmarks.
- `time.perf_counter()` around the call gives total latency.
- Bigger models are usually slower and pricier - they must earn their place.
