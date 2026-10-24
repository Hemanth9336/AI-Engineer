---
type: task
title: "Build a minimal proof of concept from a brief"
minutes: 12
---

## Set up

`brief.md` is the one-week PoC brief. `handbook.json` is Harbor Foods' supplier handbook split into eight sections.

```bash
mkdir -p /root/fde-lab/38-poc
cd /root/fde-lab/38-poc
cat > brief.md <<'EOF'
# PoC brief: supplier desk answer drafts

Goal: show in one week that the assistant can draft correct, cited answers to supplier questions from the handbook.

- Input: one supplier question.
- Output: a short answer citing the handbook section it came from, or a clear refusal if the handbook doesn't cover it.
- Data: `handbook.json` - the handbook split into eight sections.
- Demo: Friday, to Marta Kovacs and two desk agents.
EOF
cat > handbook.json <<'EOF'
[
  {
    "id": "h1",
    "title": "Delivery slots",
    "text": "Suppliers deliver to the Harbor Foods warehouse Monday to Saturday. Ambient goods: 06:00 to 14:00. Chilled and frozen goods: 04:00 to 09:00 only."
  },
  {
    "id": "h2",
    "title": "Booking a delivery slot",
    "text": "Book every delivery in the supplier portal at least 48 hours ahead. Unbooked trucks are turned away at the gate."
  },
  {
    "id": "h3",
    "title": "Temperature requirements",
    "text": "Chilled goods must arrive between 0 and 5 degrees Celsius, frozen goods at -18 degrees or colder. Each delivery needs a temperature log."
  },
  {
    "id": "h4",
    "title": "Pallet labels",
    "text": "Every pallet needs an SSCC label on two sides showing the purchase order number, product code and best-before date."
  },
  {
    "id": "h5",
    "title": "Rejected deliveries",
    "text": "Deliveries that fail the temperature or label check are rejected at the dock. The supplier collects rejected goods within 24 hours at its own cost."
  },
  {
    "id": "h6",
    "title": "Invoice disputes",
    "text": "Raise invoice disputes in the supplier portal within 30 days of the invoice date. Disputes are answered within 10 working days."
  },
  {
    "id": "h7",
    "title": "Allergen information",
    "text": "Product specifications must list the 14 major allergens. Send updated specifications to quality@harborfoods.example before a recipe change ships."
  },
  {
    "id": "h8",
    "title": "Supplier contacts",
    "text": "Goods-in desk: +31 10 555 0100, staffed from 04:00 to 14:00. Supplier account managers answer email within one working day."
  }
]
EOF
```

## What to build

**1. Build the PoC** in `/root/fde-lab/38-poc/poc.py`, used as `python poc.py QUESTION`:

- Retrieve the **top 3** handbook sections by embedding similarity (`"<title>. <text>"`).
- Call `lab-fast` at `temperature=0` in JSON mode. Put the sources after the system prompt as `[h1] title. text` lines, using this system prompt:
  ```text
  You draft answers for the Harbor Foods supplier desk from the Harbor Foods supplier handbook. Use only the sections below. If they don't answer the question, the answer must be exactly: I don't know based on the provided sources. Reply with JSON: {"answer": "... [h1]", "source": "h1" or null}
  ```
- If `source` isn't one of the retrieved ids, set it to `null`.
- Print the result as one JSON line.

**2. Write `POC_NOTES.md`** with three `##` sections - `What it does`, `Cut for the PoC` and `Needed before production` - each with at least **three** bullets.

```bash
cd /root/fde-lab/38-poc
python poc.py "How long do I have to dispute an invoice?"
python poc.py "What is the penalty for a late delivery?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The second question is a trap - the handbook says nothing about penalties.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/38-poc
cat > poc.py <<'EOF'
import json
import math
import sys
from pathlib import Path

from openai import OpenAI

client = OpenAI()
HANDBOOK = json.loads(Path(__file__).with_name("handbook.json").read_text())
SYSTEM = 'You draft answers for the Harbor Foods supplier desk from the Harbor Foods supplier handbook. Use only the sections below. If they don\'t answer the question, the answer must be exactly: I don\'t know based on the provided sources. Reply with JSON: {"answer": "... [h1]", "source": "h1" or null}'


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def retrieve(question, k=3):
    vecs = [d.embedding for d in client.embeddings.create(model="lab-embed", input=[f"{h['title']}. {h['text']}" for h in HANDBOOK] + [question]).data]
    q = vecs.pop()
    return [h for _, h in sorted(zip([cosine(v, q) for v in vecs], HANDBOOK), key=lambda x: x[0], reverse=True)[:k]]


def draft(question):
    sections = retrieve(question)
    context = "\n".join(f"[{h['id']}] {h['title']}. {h['text']}" for h in sections)
    raw = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": f"{SYSTEM}\n\n{context}"}, {"role": "user", "content": question}],
    ).choices[0].message.content
    result = json.loads(raw)
    if result.get("source") not in [h["id"] for h in sections]:
        result["source"] = None
    return result


if __name__ == "__main__":
    print(json.dumps(draft(sys.argv[1])))

EOF
cat > POC_NOTES.md <<'EOF'
# PoC notes: supplier desk answer drafts

## What it does
- Takes one supplier question, retrieves the three closest handbook sections with embeddings, and drafts a short cited answer with lab-fast.
- Refuses with a fixed sentence when the handbook doesn't cover the question.
- Drops any citation that isn't one of the retrieved sections.

## Cut for the PoC
- No Zendesk integration - questions are typed on the command line.
- No PII redaction - the demo uses made-up questions only.
- Embeddings are recomputed on every call instead of stored in an index.
- No logging, monitoring or cost tracking.
- Evaluated on a handful of questions, not a golden set.

## Needed before production
- A golden set of 100 real supplier questions agreed with the desk team, with an eval run gating every change.
- PII redaction of supplier emails and an agreed logging policy.
- A persisted index rebuilt when the handbook changes.
- Zendesk integration with mandatory agent review before sending.
- Call logging, cost and latency monitoring, and timeouts with a fallback.
EOF
python poc.py "How long do I have to dispute an invoice?"
python poc.py "What is the penalty for a late delivery?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/38-poc; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/poc.py 2>/dev/null && [ -s $D/poc.py ] && echo "✅ poc.py reads the key from the environment" || echo "❌ poc.py must not contain a key - let the SDK read it from the environment"
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
import re
def sections(path):
    text = Path(path).read_text() if Path(path).exists() else ""
    out, name = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            name = m.group(1).strip().lower()
            out[name] = []
        elif name is not None and line.strip():
            out[name].append(line.strip())
    return out
def bullets(lines):
    return [l for l in lines if re.match(r"^([-*]|\d+\.)\s+\S", l)]

REFUSE = "I don't know based on the provided sources."
def ask(q):
    rc, out, err = run("poc.py", q)
    try:
        return json.loads(out.splitlines()[-1]), err
    except Exception:
        return {}, out[-200:] + err[-200:]
r, err = ask("What time can suppliers deliver chilled goods?")
ok(r.get("source") == "h1" and "04:00" in str(r.get("answer")) and "[h1]" in str(r.get("answer")), "the chilled-delivery question is answered from h1 with a citation", f"expected an answer citing [h1] with 04:00 - got {r} {err}")
r, err = ask("What happens if my delivery is rejected?")
ok(r.get("source") == "h5" and "24 hours" in str(r.get("answer")), "the rejected-delivery question is answered from h5", f"expected an answer from h5 mentioning 24 hours - got {r} {err}")
r, err = ask("What is the penalty for a late delivery?")
ok(r.get("answer") == REFUSE and r.get("source") is None, "the trap question is refused with no source", f"expected exactly the refusal and source null - got {r} {err}")
sys.path.insert(0, ".")
try:
    import poc, types
    poc.retrieve = lambda q, k=3: poc.HANDBOOK[:3]
    reply = '{"answer": "Invented [h7].", "source": "h7"}'
    poc.client = types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda **k: types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=reply))]))))
    ok(poc.draft("x").get("source") is None, "a citation outside the retrieved sections is dropped", "if source isn't one of the retrieved ids, set it to null")
except Exception as e:
    print(f"❌ import poc failed: {e}")
s = sections("POC_NOTES.md")
short = [h for h in ("what it does", "cut for the poc", "needed before production") if len(bullets(s.get(h, []))) < 3]
ok(not short, "POC_NOTES.md lists what it does, what was cut and what production needs", f"these sections need at least three bullets: {short}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and .json_mode and .temperature == 0 and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-fast call" || echo "❌ the gateway has no lab-fast call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A PoC proves the core loop on real data in days.
- Keep citations, refusals and keys-out-of-code even in a PoC.
- Write down every shortcut so the PoC isn't mistaken for a product.
