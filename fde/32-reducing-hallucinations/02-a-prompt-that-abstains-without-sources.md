---
type: task
title: "A prompt that abstains without sources"
minutes: 8
---

## Set up

```bash
mkdir -p /root/fde-lab/32-hallucinations
cd /root/fde-lab/32-hallucinations
cat > articles.json <<'EOF'
[
  {
    "id": "a1",
    "title": "Reporting a damaged parcel",
    "text": "Report damage within 7 days of delivery through the claims page. Attach photos of the item and the packaging. Claims are reviewed within 3 working days and approved claims are refunded to the original payment method."
  },
  {
    "id": "a2",
    "title": "Changing a delivery address",
    "text": "You can change the delivery address until the parcel leaves the depot. Open the order in your account and choose Edit address. After dispatch, address changes cost 6 EUR and add one working day."
  },
  {
    "id": "a3",
    "title": "International shipping and customs",
    "text": "International parcels outside the EU need a commercial invoice. Customs checks usually add 2 to 5 working days. Import duties are paid by the receiver unless the sender booked DDP (Delivered Duty Paid)."
  },
  {
    "id": "a4",
    "title": "Support hours",
    "text": "Customer support is open 8:00 to 18:00 CET, Monday to Friday. Urgent pallet issues for business accounts can use the 24/7 operations line."
  },
  {
    "id": "a5",
    "title": "Tracking a parcel",
    "text": "Enter the order id, for example MER-55120, on the tracking page. Status updates appear at every hub scan. If tracking has not changed for 3 working days, contact support."
  },
  {
    "id": "a6",
    "title": "Pallet weight limits",
    "text": "Standard pallets can weigh up to 800 kg and be up to 1.8 m high. Heavier pallets need a freight booking at least 2 working days in advance."
  },
  {
    "id": "a7",
    "title": "Dangerous goods",
    "text": "Lithium batteries, aerosols and flammable liquids are dangerous goods. They need a dangerous goods declaration and can only travel by road, never by air."
  },
  {
    "id": "a8",
    "title": "Invoices and payment terms",
    "text": "Business invoices are issued on the 1st of each month. Payment terms are 30 days. A fuel surcharge applies when the diesel index rises above the contract level."
  },
  {
    "id": "a9",
    "title": "Missed delivery",
    "text": "If nobody is home, the driver leaves a card and tries again the next working day. After two failed attempts the parcel waits at the local depot for 7 days, then returns to the sender."
  },
  {
    "id": "a10",
    "title": "Scanner error codes",
    "text": "Error E-4417 on a handheld scanner means the label barcode is unreadable. Re-print the label from the depot terminal. Error E-2210 means the scanner has lost its network connection."
  },
  {
    "id": "a11",
    "title": "Returns for business customers",
    "text": "Business customers can book a return collection up to 30 days after delivery. Returns of opened goods are accepted only if the original packaging is included."
  },
  {
    "id": "a12",
    "title": "Cold chain shipments",
    "text": "Chilled goods travel in refrigerated trucks between 2 and 8 degrees Celsius. Temperature logs are available on request for every cold chain shipment."
  }
]
EOF
cat > vectors.py <<'EOF'
import json
import math
from pathlib import Path

from openai import OpenAI

client = OpenAI()
ARTICLES = json.loads(Path(__file__).with_name("articles.json").read_text())


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def scored(query, articles=None):
    articles = ARTICLES if articles is None else articles
    vecs = [d.embedding for d in client.embeddings.create(model="lab-embed", input=[f"{a['title']}. {a['text']}" for a in articles] + [query]).data]
    q = vecs.pop()
    return sorted(((cosine(v, q), a) for v, a in zip(vecs, articles)), key=lambda x: x[0], reverse=True)
EOF
```

## What to build

Write `/root/fde-lab/32-hallucinations/abstain.py`:

- `answer(question, min_score=0.3, k=3)` keeps the top `k` articles whose score is at least `min_score`.
- **No sources left** -> return the refusal with **no chat call**.
- Otherwise call `lab-fast` at `temperature=0` with a system prompt that: answers only from the sources, gives the exact refusal `I don't know based on the provided sources.` when they don't contain the answer, forbids outside knowledge, and handles partial coverage as in the lesson.
- Return `{"answer": ..., "sources": [ids], "called_model": bool}`; `python abstain.py QUESTION` prints it as JSON.

```bash
cd /root/fde-lab/32-hallucinations
python abstain.py "How many days does a parcel wait at the local depot?"
python abstain.py "How much does DDP cost?"
python abstain.py "Do you deliver to Iceland?"
```

Look at which ones called the model.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `scored()` already returns `(score, article)` pairs, best first.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/32-hallucinations
cat > abstain.py <<'EOF'
import json
import sys

from vectors import client, scored

REFUSE = "I don't know based on the provided sources."
SYSTEM = ("Answer the question using only the sources below. "
          f"If the sources don't contain the answer, reply exactly: {REFUSE} "
          "Do not use outside knowledge, even if you are confident. "
          "If the sources answer only part of the question, answer that part and say which part they don't cover.")


def answer(question, min_score=0.3, k=3):
    sources = [a for s, a in scored(question)[:k] if s >= min_score]
    if not sources:
        return {"answer": REFUSE, "sources": [], "called_model": False}
    context = "\n".join(f"[{a['id']}] {a['title']}. {a['text']}" for a in sources)
    reply = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": f"{SYSTEM}\n\nSources:\n{context}"}, {"role": "user", "content": question}],
    ).choices[0].message.content.strip()
    return {"answer": reply, "sources": [a["id"] for a in sources], "called_model": True}


if __name__ == "__main__":
    print(json.dumps(answer(sys.argv[1])))

EOF
python abstain.py "How many days does a parcel wait at the local depot?"
python abstain.py "How much does DDP cost?"
python abstain.py "Do you deliver to Iceland?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/32-hallucinations; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/abstain.py 2>/dev/null && [ -s $D/abstain.py ] && echo "✅ abstain.py reads the key from the environment" || echo "❌ abstain.py must not contain a key - let the SDK read it from the environment"
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
REFUSE = "I don't know based on the provided sources."
def chats():
    return sum(1 for l in open("/var/log/ailab/requests.jsonl") if '"chat.completions"' in l)
def ask(q):
    before = chats()
    rc, out, err = run("abstain.py", q)
    try:
        r = json.loads(out)
    except ValueError:
        r = {"raw": out[:200] + err[-200:]}
    return r, chats() - before
r, n = ask("Who will win the football tonight?")
ok(r.get("answer") == REFUSE and r.get("called_model") is False and r.get("sources") == [] and n == 0, "an off-topic question is refused with no model call", f"expected the refusal, no sources and no chat call - got {r} with {n} chat calls")
r, n = ask("Do you deliver to Iceland?")
ok(r.get("answer") == REFUSE and r.get("called_model") is True and n == 1, "an on-topic trap reaches the model, which refuses exactly", f"expected one chat call and exactly the refusal - got {r} with {n} chat calls")
r, n = ask("How many days does a parcel wait at the local depot?")
ok(r.get("called_model") is True and "7" in str(r.get("answer")) and r.get("answer") != REFUSE and "a9" in (r.get("sources") or []), "a covered question is answered from its sources", f"expected an answer with 7 days and a9 among the sources - got {r}")
sys.path.insert(0, ".")
try:
    import abstain
    before = chats()
    r = abstain.answer("How many days does a parcel wait at the local depot?", min_score=0.99)
    ok(r["answer"] == REFUSE and chats() == before, "min_score is respected", "with min_score=0.99 nothing qualifies, so expect the refusal and no chat call")
except Exception as e:
    print(f"❌ import abstain failed: {e}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and .temperature == 0 and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-fast call" || echo "❌ the gateway has no lab-fast call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A clean refusal is a good outcome; a confident wrong answer is the worst one.
- Skip the model call entirely when no source clears the threshold.
- Give the model an exact refusal and a rule for partial coverage.
