---
type: task
title: "Hit the context limit on purpose"
minutes: 7
---

## Set up

```bash
ailab status
ailab models | grep -q lab-tiny && echo "lab-tiny is configured" || echo "lab-tiny missing - run the FDE install script from setup/README.md"
mkdir -p /root/fde-lab/04-tokens
```

## What to build

Write `/root/fde-lab/04-tokens/limit.py` that probes `lab-tiny` with growing prompts:

1. For each size in `[20, 100, 400]`, build a prompt of that many copies of the sentence `The quick brown fox jumps over the lazy dog. ` followed by `How many times does the word fox appear above?`
2. Send it to `lab-tiny` with `max_tokens=20`.
3. On success, record `{"sentences": N, "ok": true, "prompt_tokens": <usage.prompt_tokens>}`.
4. If the API rejects it, catch the error (`openai.BadRequestError`) and record `{"sentences": N, "ok": false, "error": "<first 200 characters of the error message>"}`.
5. Write the list to `limit.json` and print one line per size.

```bash
cd /root/fde-lab/04-tokens
python limit.py
```

Your script must keep running after the error - that's the point.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `import openai` then `except openai.BadRequestError as e: str(e)[:200]`.
- The sentence is about 10 tokens, so 400 copies is about 4,000 tokens - twice the window.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/04-tokens
cat > limit.py <<'EOF'
import json

import openai
from openai import OpenAI

client = OpenAI()
SENTENCE = "The quick brown fox jumps over the lazy dog. "
results = []
for n in [20, 100, 400]:
    prompt = SENTENCE * n + "How many times does the word fox appear above?"
    try:
        resp = client.chat.completions.create(model="lab-tiny", max_tokens=20, messages=[{"role": "user", "content": prompt}])
        results.append({"sentences": n, "ok": True, "prompt_tokens": resp.usage.prompt_tokens})
    except openai.BadRequestError as e:
        results.append({"sentences": n, "ok": False, "error": str(e)[:200]})
    print(results[-1])
json.dump(results, open("limit.json", "w"), indent=2)
EOF
python limit.py
```

</details>

## Check your work

```bash
D=/root/fde-lab/04-tokens; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/limit.py 2>/dev/null && [ -s $D/limit.py ] && echo "✅ limit.py reads the key from the environment" || echo "❌ limit.py must not contain a key - let the SDK read it from the environment"
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
r = load("limit.json") or []
by = {x.get("sentences"): x for x in r if isinstance(x, dict)}
ok(sorted(by) == [20, 100, 400], "limit.json has results for 20, 100 and 400 sentences", "limit.json should hold one result each for 20, 100 and 400 sentences")
ok(by.get(20, {}).get("ok") is True and by.get(100, {}).get("ok") is True and by[100].get("prompt_tokens", 0) > by[20].get("prompt_tokens", 10**9), "20 and 100 sentences fit, with growing prompt_tokens", "20 and 100 sentences should succeed with prompt_tokens from the response")
ok(by.get(400, {}).get("ok") is False and "context" in by[400].get("error", "").lower(), "400 sentences is rejected with a context-window error", "400 sentences should be caught as an error whose message mentions the context window")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
ok(any(x.get("model") == "lab-tiny" and not x.get("ok") and x.get("client", "").startswith("OpenAI/Python") for x in rows), "the gateway logged the rejected lab-tiny request", "the gateway has no rejected lab-tiny request from your script")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- The context window caps prompt plus answer tokens in one request.
- Hitting it raises an error you must catch - or, in some systems, silently truncates.
- Big prompts cost more and run slower even under the limit; send only what's needed.
