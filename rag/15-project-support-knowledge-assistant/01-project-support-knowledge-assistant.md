---
type: task
title: "Project: Support Knowledge Assistant"
minutes: 60
---

## Scenario

Northwind support has six help-centre articles that answer most tickets. Agents spend their day finding the right article and rewriting it as a reply. Build an assistant that, for each new ticket, finds the best article, drafts a reply grounded in it, and **escalates** tickets that no article covers - without drafting anything for those.

The new idea here is a **relevance threshold**. Retrieval always returns *something*, even for a ticket about printers in Lisbon. You'll decide, from real scores, how close a match must be before the assistant is allowed to answer.

## Set up

Set up gives you `kb.json` (six articles with `id`, `title`, `text`) and `tickets.jsonl` (four tickets with `id` and `text`).

```bash
ailab status
mkdir -p /root/rag-lab/15-support /root/answers
cd /root/rag-lab/15-support
cat > kb.json <<'EOF'
[
  {
    "id": "kb-101",
    "title": "Resetting your password",
    "text": "If you can't sign in, use the Forgot password link on the login page. We email a reset link that is valid for 30 minutes. If the email does not arrive, check your spam folder or ask support to resend it."
  },
  {
    "id": "kb-102",
    "title": "Duplicate charges",
    "text": "If you were charged twice for one order, the second charge is usually a temporary authorization hold that disappears within 5 business days. If it is still there after 5 business days, reply with the order number and we refund it within 48 hours."
  },
  {
    "id": "kb-103",
    "title": "Changing your email address",
    "text": "Go to Settings, then Profile, and choose Change email. We send a confirmation link to the new address, and the change takes effect once you click it."
  },
  {
    "id": "kb-104",
    "title": "Missing deliveries",
    "text": "If your package shows as delivered but you don't have it, check with neighbours and your building's mailroom first. If it hasn't turned up after 48 hours, contact support and we will open an investigation with the courier and send a replacement."
  },
  {
    "id": "kb-105",
    "title": "Exporting invoices",
    "text": "All invoices are under Billing, then Invoices. Choose a date range and click Download to get a single PDF for that period. Invoices are kept for seven years."
  },
  {
    "id": "kb-106",
    "title": "Closing your account",
    "text": "To delete your account, go to Settings, then Privacy, and choose Delete account. Your data is permanently removed within 30 days, and the deletion cannot be undone."
  }
]
EOF
cat > tickets.jsonl <<'EOF'
{"id": "TCK-1", "text": "Hi, I've tried to log in five times and it says my password is incorrect. Can you help me get back in?"}
{"id": "TCK-2", "text": "My bank statement shows two payments for order 88412 but I only bought one thing."}
{"id": "TCK-3", "text": "The tracking says delivered yesterday but there's nothing at my door."}
{"id": "TCK-4", "text": "Do you have an office in Lisbon where I can drop off a printer?"}
EOF
wc -l tickets.jsonl
```

## What to build

**1. Look at real scores first.** Embed each article as its title, a newline, then its text. For each ticket, print the best article and its cosine similarity. You'll see three tickets match their articles well (around 0.5-0.6), and the Lisbon printer ticket's best match is around 0.2. That gap is where your threshold goes: use **0.35**.

**2. Write `/root/rag-lab/15-support/assist.py`**, used as `python assist.py TICKETS.jsonl`:

- Index the articles (any vector store under `/root/rag-lab/15-support/`; re-runs must not duplicate).
- For each ticket, retrieve the single best article and its cosine similarity, rounded to 3 decimals.
- If the score is **0.35 or more**: draft a short, friendly reply with `lab-fast` at `temperature=0`, grounded only in that article (article in the system message, ticket text as the user message).
- If the score is **below 0.35**: escalate - and make **no** chat call for that ticket.
- Print a JSON list, one object per ticket, in input order:

  ```json
  [
    { "ticket_id": "TCK-1", "article": "kb-101", "score": 0.613, "reply": "...", "escalate": false },
    { "ticket_id": "TCK-4", "article": null, "score": 0.213, "reply": null, "escalate": true }
  ]
  ```

```bash
python assist.py tickets.jsonl > /root/answers/15-results.json
```

The checker runs your assistant on tickets you haven't seen.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- With Chroma's cosine space, `score = 1 - distance`.
- Query all tickets at once: `query_texts=[t["text"] for t in tickets], n_results=1` - one embedding call.
- Return early for low scores, before any chat call.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/15-support
cat > assist.py <<'EOF'
import json
import os
import sys
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from openai import OpenAI

HERE = Path(__file__).resolve().parent
THRESHOLD = 0.35
client = OpenAI()
embed = OpenAIEmbeddingFunction(
    api_key_env_var="OPENAI_API_KEY", api_base=os.environ["OPENAI_BASE_URL"], model_name="lab-embed"
)
kb = chromadb.PersistentClient(path=str(HERE / "db")).get_or_create_collection(
    "help-articles", embedding_function=embed, configuration={"hnsw": {"space": "cosine"}}
)


def index_kb():
    articles = json.load(open(HERE / "kb.json"))
    kb.upsert(
        ids=[a["id"] for a in articles],
        documents=[f"{a['title']}\n{a['text']}" for a in articles],
        metadatas=[{"title": a["title"]} for a in articles],
    )


def draft(ticket, article_id, article):
    system = (
        "You are a friendly Northwind support agent. Write a short reply to the customer, "
        "using only the help article below. Do not promise anything the article does not say.\n\n"
        f'<article id="{article_id}">\n{article}\n</article>'
    )
    resp = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": ticket}],
    )
    return resp.choices[0].message.content.strip()


def triage(tickets):
    res = kb.query(query_texts=[t["text"] for t in tickets], n_results=1)
    results = []
    for t, ids, dists, docs in zip(tickets, res["ids"], res["distances"], res["documents"]):
        score = round(1 - dists[0], 3)
        if score < THRESHOLD:
            results.append({"ticket_id": t["id"], "article": None, "score": score, "reply": None, "escalate": True})
        else:
            results.append({"ticket_id": t["id"], "article": ids[0], "score": score,
                            "reply": draft(t["text"], ids[0], docs[0]), "escalate": False})
    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: assist.py TICKETS.jsonl", file=sys.stderr)
        sys.exit(2)
    index_kb()
    tickets = [json.loads(line) for line in open(sys.argv[1]) if line.strip()]
    print(json.dumps(triage(tickets), indent=2))
EOF
python assist.py tickets.jsonl > /root/answers/15-results.json
cat /root/answers/15-results.json
```

</details>

## Check your work

```bash
D=/root/rag-lab/15-support; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/assist.py 2>/dev/null && [ -s $D/assist.py ] && echo "✅ assist.py reads the key from the environment" || echo "❌ assist.py must not contain a key - let the SDK read it from the environment"
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
kbj = load("kb.json") or []
vec = dict(zip([a["id"] for a in kbj], E([f"{a['title']}\n{a['text']}" for a in kbj])))
def best(text):
    qv = E([text])[0]
    return max((cos(qv, v), i) for i, v in vec.items())
def verify(results, tickets, phrases, label):
    good = isinstance(results, list) and len(results) == len(tickets)
    ok(good and [r.get("ticket_id") for r in results] == [t["id"] for t in tickets], f"{label}: one result per ticket, in order", f"{label}: expected one result per ticket in input order - got {str(results)[:200]}")
    if not good:
        return
    for r, t in zip(results, tickets):
        s, art = best(t["text"])
        esc = s < 0.35
        shape = abs((r.get("score") or -9) - s) < 0.01
        if esc:
            ok(shape and r.get("escalate") is True and r.get("article") is None and r.get("reply") is None, f"{t['id']} escalates (score {s:.3f})", f"{t['id']} scores {s:.3f} - it should escalate with article null and reply null, got {r}")
        else:
            ph = phrases.get(t["id"], "")
            ok(shape and r.get("escalate") is False and r.get("article") == art and ph.lower() in (r.get("reply") or "").lower(), f"{t['id']} -> {art} (score {s:.3f}) with a grounded reply", f"{t['id']} should match {art} with score {s:.3f}, escalate false and a reply grounded in it - got {str(r)[:250]}")
tickets = [json.loads(l) for l in open("tickets.jsonl") if l.strip()]
verify(load("/root/answers/15-results.json"), tickets, {"TCK-1": "Forgot password", "TCK-2": "5 business days", "TCK-3": "48 hours"}, "15-results.json")
new = [
    {"id": "N-1", "text": "How can I permanently delete my account and data?"},
    {"id": "N-2", "text": "Who won the football match last night?"},
    {"id": "N-3", "text": "Where do I find my invoices from 2023?"},
    {"id": "N-4", "text": "Can you recommend a good pizza place near your office?"},
]
Path("/tmp/new-tickets.jsonl").write_text("\n".join(json.dumps(t) for t in new) + "\n")
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("/root/rag-lab/15-support/assist.py", "/tmp/new-tickets.jsonl")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
try:
    res = json.loads(out)
except ValueError:
    res = None
    print(f"❌ assist.py should print a JSON list - got {out[:200]!r} {err[-200:]}")
verify(res, new, {"N-1": "30 days", "N-3": "Billing"}, "new tickets")
chats = [r for r in rows if r.get("api") == "chat.completions"]
ok(len(chats) == 2 and all(r.get("system") and r.get("temperature") == 0 and r.get("model") == "lab-fast" for r in chats), "exactly 2 chat calls for 4 new tickets - none for escalations", f"expected 2 lab-fast calls (temperature 0, with a system message) for the 2 matching tickets - saw {len(chats)}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Retrieval always returns something - a relevance threshold decides when to answer.
- Set the threshold from real scores for your model and data, not a guess.
- Escalate below the threshold without calling the model: cheaper, and nothing invented.
