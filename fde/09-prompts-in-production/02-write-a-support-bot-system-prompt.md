---
type: task
title: "Write a support bot system prompt"
minutes: 9
---

## Set up

```bash
mkdir -p /root/fde-lab/09-prompts
```

## What to build

Write Meridian's support bot system prompt in `/root/fde-lab/09-prompts/support.txt`. It must cover all seven sections from the lesson, and in particular:

- scope: deliveries, tracking, damage claims, invoices and addresses;
- out-of-scope questions get **exactly** this reply: `Sorry, I can only help with Meridian deliveries, invoices and claims.`
- injury, legal action, or a very upset customer: say a human agent will contact them (use the word `human`);
- at most 80 words, plain sentences.

Then write `bot.py`, used as `python bot.py QUESTION`, that loads `support.txt` as the system message and asks `lab-fast` at `temperature=0`, printing the reply.

```bash
cd /root/fde-lab/09-prompts
python bot.py "My parcel MER-55120 arrived damaged, what do I do?"
python bot.py "Can you write me a poem about the sea?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Quote the refusal sentence exactly in the prompt, and say 'reply with exactly this sentence'.
- Load the file next to the script: `Path(__file__).with_name("support.txt").read_text()`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/09-prompts
cat > support.txt <<'EOF'
You are the support assistant for Meridian Logistics customers.
Help only with deliveries, tracking, damage claims, invoices and delivery addresses.
For any other request, reply with exactly this sentence and nothing else: Sorry, I can only help with Meridian deliveries, invoices and claims.
Use only facts you are given in this conversation. If you don't know, say so and offer to connect the customer with a human agent.
If the customer mentions an injury, legal action, or is very upset, tell them a human agent will contact them today.
Write plain sentences, at most 80 words, no markdown.
EOF
cat > bot.py <<'EOF'
import sys
from pathlib import Path

from openai import OpenAI

SYSTEM = Path(__file__).with_name("support.txt").read_text()
resp = OpenAI().chat.completions.create(
    model="lab-fast",
    temperature=0,
    messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": sys.argv[1]}],
)
print(resp.choices[0].message.content.strip())
EOF
python bot.py "My parcel MER-55120 arrived damaged, what do I do?"
python bot.py "Can you write me a poem about the sea?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/09-prompts; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/bot.py 2>/dev/null && [ -s $D/bot.py ] && echo "✅ bot.py reads the key from the environment" || echo "❌ bot.py must not contain a key - let the SDK read it from the environment"
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
REFUSAL = 'Sorry, I can only help with Meridian deliveries, invoices and claims.'
p = Path("support.txt").read_text() if Path("support.txt").exists() else ""
ok(REFUSAL in p and "human" in p.lower() and "80" in p, "support.txt has the exact refusal, the human escalation and the length limit", "support.txt must quote the refusal sentence exactly, mention a human agent and the 80-word limit")
rc, out, err = run("bot.py", "What's a good recipe for banana bread?")
ok(rc == 0 and out.strip() == REFUSAL, "an out-of-scope question gets exactly the refusal", f"an out-of-scope question should reply exactly with the refusal - got {out[:200]!r} {err[-150:]}")
rc, out, err = run("bot.py", "I slipped on a broken pallet your driver left on my steps and hurt my back.")
ok(rc == 0 and "human" in out.lower() and out.strip() != REFUSAL, "an injury report is escalated to a human", f"an injury report should say a human agent will contact them - got {out[:200]!r}")
rc, out, err = run("bot.py", "How do I report a damaged parcel?")
ok(rc == 0 and out.strip() and out.strip() != REFUSAL and len(out.split()) <= 80, "an in-scope question is answered in at most 80 words", f"an in-scope question should get an answer of at most 80 words - got {out[:200]!r}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A production system prompt covers identity, scope, refusals, facts, unknowns, escalation and style.
- Fixed phrases for refusals and escalation make behaviour detectable by code and evals.
- Keep the prompt in a reviewable file the customer can sign off.
