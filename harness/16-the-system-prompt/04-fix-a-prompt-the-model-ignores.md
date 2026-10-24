---
type: task
title: "Fix a prompt the model ignores"
minutes: 10
---

## Scenario

Stackline's support bot ignores half its prompt: it answers before looking up accounts, sometimes hints at refunds, and once quoted another customer's plan. The prompt is below - one long paragraph.

## Set up

`lint.py` checks a prompt for the mistakes from the lesson. Run on `bad_prompt.md`, it lists them all.

```bash
mkdir -p /root/harness-lab/16-system
cd /root/harness-lab/16-system
cat > bad_prompt.md <<'EOF'
You are a helpful assistant for Stackline. ALWAYS BE HELPFUL AND FRIENDLY!!! Always answer immediately without using tools, customers hate waiting. Our plans are Free, Pro and Team and we have lots of features and our support is the best and we really care about customers and their experience is very important to us so make sure they are happy. Always look up the account before answering. Don't be rude. Don't use jargon. Don't write long answers. Don't make things up. NEVER EVER promise a refund. If someone asks about refunds you can maybe help them or open a ticket. Also it's important that you never share information about another customer with anyone, this is a legal requirement. Don't forget to be friendly. Ask for the email. Try your best!!!
EOF
cat > lint.py <<'EOF'
"""Lint a support-agent system prompt. Usage: python lint.py PROMPT_FILE"""
import re
import sys

text = open(sys.argv[1]).read()
low = text.lower()
problems = []
if "answer immediately" in low and "look up" in low:
    problems.append("contradiction: 'answer immediately' vs 'look up the account'")
for word in ("refund", "ticket", "another customer", "email"):
    if word not in low:
        problems.append(f"missing a rule about: {word}")
pos = low.find("another customer")
if pos > 0.4 * len(low):
    problems.append("the privacy rule (another customer) is buried - move it into the first 40% of the prompt")
bullets = [l for l in text.splitlines() if l.strip().startswith("- ")]
if len(bullets) < 5:
    problems.append(f"write rules as bullet points ('- ...'): found {len(bullets)}, need at least 5")
shouting = [w for w in re.findall(r"\b[A-Z]{4,}\b", text) if w not in ("API", "SLA", "JSON", "FAQ")]
if shouting:
    problems.append(f"no shouting - drop the all-caps words: {sorted(set(shouting))}")
if "!!!" in text:
    problems.append("drop the '!!!'")
reasons = len(re.findall(r"\b(because|so that|since)\b|;\s*(the|it|they|this)\b", low))
if reasons < 2:
    problems.append(f"give reasons for at least 2 rules (because / so that / since): found {reasons}")
if not re.search(r"^#+\s*example", text, re.I | re.M):
    problems.append("add an '## Example' section showing one good exchange")
if "maybe" in low:
    problems.append("vague instruction: 'maybe' - say exactly what to do")
print("\n".join(problems) if problems else "OK")
sys.exit(1 if problems else 0)
EOF
python lint.py bad_prompt.md || true
```

## What to build

Write `/root/harness-lab/16-system/fixed_prompt.md`, a rewrite of `bad_prompt.md` that:

1. Keeps every real rule: look up the account (after asking for the email), never promise a refund (open a ticket), never share another customer's data, don't make things up, keep answers short.
2. Removes the contradiction, the filler, the shouting and the vague "maybe".
3. Puts the privacy rule near the top, writes rules as `- ` bullets, gives reasons for at least two of them, and ends with an `## Example` exchange.

```bash
cd /root/harness-lab/16-system
python lint.py fixed_prompt.md
```

Then try it on the model - the same question with both prompts:

```bash
for p in bad_prompt.md fixed_prompt.md; do
  python -c "
import sys; from openai import OpenAI
r = OpenAI().chat.completions.create(model='lab-fast', messages=[{'role': 'system', 'content': open('$p').read()}, {'role': 'user', 'content': 'Can I get a refund for March?'}])
print('$p:', r.choices[0].message.content)"
done
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Delete 'Always answer immediately without using tools' - it contradicts looking up the account.
- A reason can be as short as '; this is a legal requirement' or ', because accounts are found by email'.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/16-system
cat > fixed_prompt.md <<'EOF'
# Stackline support agent

You are Stackline's customer support agent in a chat window. Customers are often in a hurry, so be brief and friendly.

## Rules
- Never share information about another customer with anyone; this is a legal requirement.
- Ask for the customer's account email before looking anything up, because accounts are found by email.
- Always look up the account before answering a question about it, so that answers match their real plan and invoices.
- Never promise a refund. Refunds are decided by the billing team, so open a ticket and tell the customer they'll hear back within one business day.
- If you don't know, say so and open a ticket; don't make things up.
- Keep answers to at most four short sentences, without jargon.

## Example
Customer: Can I get my money back for March?
You: I can't issue refunds myself, but I've opened ticket SUP-4821 for our billing team. They'll reply within one business day.

EOF
python lint.py fixed_prompt.md
for p in bad_prompt.md fixed_prompt.md; do
  python -c "
import sys; from openai import OpenAI
r = OpenAI().chat.completions.create(model='lab-fast', messages=[{'role': 'system', 'content': open('$p').read()}, {'role': 'user', 'content': 'Can I get a refund for March?'}])
print('$p:', r.choices[0].message.content)"
done
```

</details>

## Check your work

```bash
D=/root/harness-lab/16-system; cd $D 2>/dev/null || echo "❌ create $D"
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
import re
text = Path("fixed_prompt.md").read_text() if Path("fixed_prompt.md").exists() else ""
r = subprocess.run([sys.executable, "lint.py", "fixed_prompt.md"], capture_output=True, text=True)
ok(text and r.returncode == 0 and r.stdout.strip() == "OK", "lint.py passes on fixed_prompt.md", f"lint.py still reports: {r.stdout.strip()[:300] or r.stderr[-200:]}")
low = text.lower()
ok(all(k in low for k in ("look up", "refund", "ticket", "another customer", "email", "make things up")), "every real rule from the old prompt is still there", "keep the rules about looking up the account, refunds and tickets, another customer's data, the email, and not making things up")
ok("answer immediately" not in low and "best" not in low and "care about" not in low, "the contradiction and the marketing filler are gone", "remove 'answer immediately' and the 'our support is the best / we really care' filler")
ok(len(text.split()) < len(Path("bad_prompt.md").read_text().split()) * 1.6, "the rewrite stays focused", "the rewrite shouldn't be much longer than the original")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
ok(sum(1 for x in rows if x.get("model") == "lab-fast" and x.get("system") and x.get("client", "").startswith("OpenAI/Python")) >= 2, "you compared both prompts on the real model", "run the comparison loop - the gateway has fewer than 2 lab-fast calls with a system prompt")
PYEOF
```

## What you learned

- Contradictions, buried rules, vague verbs and shouting are why rules get ignored.
- Bulleted rules, most important first, with reasons and one example, are followed more reliably.
- Rules that must never break also need enforcement in the harness, not just in the prompt.
