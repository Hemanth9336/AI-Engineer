---
type: task
title: "Trigger a failure you will later harness against"
minutes: 8
---

## Set up

```bash
mkdir -p /root/harness-lab/02-llms
```

## What to build

Prove the model is stateless, then fix it by sending history.

Write `/root/harness-lab/02-llms/forget.py`. It makes **three** calls to `lab-fast`, with no system message:

1. Call 1 - one user message: `Remember this: the deploy target for the billing service is rack-4471.`
2. Call 2 - a **fresh** request with only one user message: `Which rack is the deploy target for the billing service?`
3. Call 3 - the same question, but this time send the whole history: the call 1 user message, the assistant's reply to call 1, then the question.

Print exactly two lines:

```text
without history: <reply to call 2>
with history: <reply to call 3>
```

Replace any newlines inside a reply with spaces so each stays on one line.

```bash
cd /root/harness-lab/02-llms
python forget.py
```

Expect the first answer to miss `rack-4471` and the second to include it. The model didn't change between the calls - only what your code sent.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Keep the reply to call 1: `first = resp.choices[0].message.content`.
- Call 3's messages: `[{"role": "user", "content": FACT}, {"role": "assistant", "content": first}, {"role": "user", "content": QUESTION}]`.
- `reply.replace("\n", " ")` keeps it on one line.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/02-llms
cat > forget.py <<'EOF'
from openai import OpenAI

FACT = "Remember this: the deploy target for the billing service is rack-4471."
QUESTION = "Which rack is the deploy target for the billing service?"

client = OpenAI()


def ask(messages):
    reply = client.chat.completions.create(model="lab-fast", messages=messages).choices[0].message.content or ""
    return reply.replace("\n", " ")


first = ask([{"role": "user", "content": FACT}])
print("without history:", ask([{"role": "user", "content": QUESTION}]))
print("with history:", ask([{"role": "user", "content": FACT},
                            {"role": "assistant", "content": first},
                            {"role": "user", "content": QUESTION}]))
EOF
python forget.py
```

</details>

## Check your work

```bash
D=/root/harness-lab/02-llms; cd $D 2>/dev/null || echo "❌ create $D"
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
sys.path.insert(0, '/opt/harness')
from labmock import MockModel
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("forget.py")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
calls = [r for r in rows if r.get("api") == "chat.completions" and r.get("model") == "lab-fast"]
lines = out.splitlines()
ok(rc == 0 and len(lines) == 2 and lines[0].startswith("without history: ") and lines[1].startswith("with history: "),
   "forget.py prints the two labelled lines", f"python forget.py should print exactly 'without history: ...' and 'with history: ...' - got {out[-300:]!r} {err[-200:]}")
ok(len(calls) == 3, "forget.py made three lab-fast calls", f"forget.py should make exactly 3 lab-fast calls - the gateway saw {len(calls)}")
roles = [c.get("roles") for c in calls]
ok(roles[:2] == [["user"], ["user"]], "calls 1 and 2 each sent a single user message", f"calls 1 and 2 should each send only one user message - roles were {roles[:2]}")
ok(len(roles) == 3 and roles[2] == ["user", "assistant", "user"], "call 3 re-sent the history: user, assistant, user", f"call 3 should send user, assistant, user - roles were {roles[2:] }")
ok(len(lines) == 2 and "rack-4471" not in lines[0] and "rack-4471" in lines[1], "only the call with history knew rack-4471", f"the reply without history shouldn't know rack-4471 and the one with history should - got {lines}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Each API call is stateless - the model knows only what this request contains.
- Memory in a chat or agent is the harness re-sending history, in the right order of roles.
- Forgetting, drift and hallucination are contained by harness parts, not by better wording.
