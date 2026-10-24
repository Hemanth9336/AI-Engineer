---
type: task
title: "Prove it: two calls, the model forgets"
minutes: 7
---

## Set up

```bash
mkdir -p /root/fde-lab/12-state
```

## What to build

Write `/root/fde-lab/12-state/forget.py` that uses `lab-mini` at `temperature=0`:

1. Call 1: user message `My name is Priya and my order is MER-55120.` Keep the reply.
2. Call 2, a **new request**: only the user message `What is my order number?`
3. Call 3: the same question, but send the history - call 1's user message, call 1's reply as an `assistant` message, then the question.

Save `{"separate": <reply 2>, "with_history": <reply 3>}` to `forget.json`.

```bash
cd /root/fde-lab/12-state
python forget.py
cat forget.json
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Keep the first reply as a dict: `{"role": "assistant", "content": reply1}`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/12-state
cat > forget.py <<'EOF'
import json

from openai import OpenAI

client = OpenAI()


def ask(messages):
    return client.chat.completions.create(model="lab-mini", temperature=0, messages=messages).choices[0].message.content


intro = {"role": "user", "content": "My name is Priya and my order is MER-55120."}
question = {"role": "user", "content": "What is my order number?"}
reply1 = ask([intro])
result = {
    "separate": ask([question]),
    "with_history": ask([intro, {"role": "assistant", "content": reply1}, question]),
}
json.dump(result, open("forget.json", "w"), indent=2)
print(result)
EOF
python forget.py
```

</details>

## Check your work

```bash
D=/root/fde-lab/12-state; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/forget.py 2>/dev/null && [ -s $D/forget.py ] && echo "✅ forget.py reads the key from the environment" || echo "❌ forget.py must not contain a key - let the SDK read it from the environment"
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
r = load("forget.json") or {}
ok("MER-55120" in str(r.get("with_history")), "with the history, the model knows the order number", f"with_history should contain MER-55120 - got {r.get('with_history')!r}")
ok(isinstance(r.get("separate"), str) and "MER-55120" not in r["separate"], "in a separate request, the model doesn't know it", f"separate should not contain the order number - got {r.get('separate')!r}")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
mine = [x.get("roles") for x in rows if x.get("model") == "lab-mini" and x.get("temperature") == 0 and x.get("client", "").startswith("OpenAI/Python")]
ok(["user"] in mine and ["user", "assistant", "user"] in mine, "the gateway logged a single-message call and a call with the history", "make one call with only the question and one with user, assistant, user")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Every API request is independent - the model only sees what you send.
- Conversation memory is your code re-sending the history.
- That means cost grows with conversation length.
