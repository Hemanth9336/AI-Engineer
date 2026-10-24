---
type: task
title: "Build a multi-turn chat loop"
minutes: 7
---

## Set up

```bash
mkdir -p /root/fde-lab/12-state
```

## What to build

Write `/root/fde-lab/12-state/chat.py`, a terminal chat for Meridian's support assistant:

- Start the history with a system message: `You are Meridian Logistics' support assistant. Answer in at most two sentences.`
- Read user turns with `input()` until end of input (`EOFError`) or the line `quit`.
- Skip empty lines.
- For each turn: append the user message, call `lab-mini`, append the reply, and print `assistant: <reply>`. Print nothing else.

```bash
cd /root/fde-lab/12-state
printf "Hi, I'm Tom from Harbor Foods.\nMy pallet MER-60311 is late.\nWhich order did I mention?\n" | python chat.py
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `try: text = input() except EOFError: break`.
- Use `input()` with no prompt argument, so nothing extra is printed.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/12-state
cat > chat.py <<'EOF'
from openai import OpenAI

client = OpenAI()
messages = [{"role": "system", "content": "You are Meridian Logistics' support assistant. Answer in at most two sentences."}]
while True:
    try:
        text = input().strip()
    except EOFError:
        break
    if text == "quit":
        break
    if not text:
        continue
    messages.append({"role": "user", "content": text})
    reply = client.chat.completions.create(model="lab-mini", messages=messages).choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    print(f"assistant: {reply}")
EOF
printf "Hi, I'm Tom from Harbor Foods.\nMy pallet MER-60311 is late.\nWhich order did I mention?\n" | python chat.py
```

</details>

## Check your work

```bash
D=/root/fde-lab/12-state; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/chat.py 2>/dev/null && [ -s $D/chat.py ] && echo "✅ chat.py reads the key from the environment" || echo "❌ chat.py must not contain a key - let the SDK read it from the environment"
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
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
r = subprocess.run([sys.executable, "chat.py"], input="Hello, this is Ana from Kestrel Foods.\n\nOur order MER-70413 is stuck.\nWhich order number did I give you?\nquit\nThis line must be ignored\n", capture_output=True, text=True)
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
lines = r.stdout.strip().splitlines()
ok(r.returncode == 0 and len(lines) == 3 and all(l.startswith("assistant: ") for l in lines), "three turns print three 'assistant:' lines; the blank line and everything after quit are skipped", f"expected exactly 3 'assistant: ' lines - got {lines} {r.stderr[-200:]}")
ok(lines and "MER-70413" in lines[-1], "the last answer remembers the order from turn two", f"the third answer should mention MER-70413 - got {lines[-1:]}")
roles = [x.get("roles") for x in rows if x.get("api") == "chat.completions"]
ok(roles == [["system", "user"], ["system", "user", "assistant", "user"], ["system", "user", "assistant", "user", "assistant", "user"]], "each request re-sent the system message and the full history", f"expected the history to grow by user/assistant pairs after the system message - got {roles}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Multi-turn chat = append user and assistant messages and re-send the list.
- The system message stays first, every time.
- Store history per conversation - never mix users.
