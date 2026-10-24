---
type: task
title: "Mine questions from a ticket dump"
minutes: 7
---

## Set up

`tickets.jsonl` is a small export from Meridian's helpdesk: each ticket has an `id`, the customer's `body` and the `resolved_article` the agent used (or `null`).

```bash
mkdir -p /root/fde-lab/26-golden
cd /root/fde-lab/26-golden
cat > tickets.jsonl <<'EOF'
{"id": "T-1001", "body": "Hi there. How long do I have to report a damaged box? It arrived crushed.", "resolved_article": "a1"}
{"id": "T-1002", "body": "Thanks for the help yesterday!", "resolved_article": null}
{"id": "T-1003", "body": "Hello. Can I still change the address? The parcel left the depot an hour ago.", "resolved_article": "a2"}
{"id": "T-1004", "body": "how long do I have to report a damaged box?", "resolved_article": "a1"}
{"id": "T-1005", "body": "My order MER-55120 is late. Where is it?", "resolved_article": "a5"}
{"id": "T-1006", "body": "Is anyone there on Saturday? I need help.", "resolved_article": "a4"}
{"id": "T-1007", "body": "Please call me back.", "resolved_article": "a4"}
{"id": "T-1008", "body": "Why was I charged a fuel surcharge?", "resolved_article": null}
{"id": "T-1009", "body": "Driver came twice and I missed him. What happens now? Thanks.", "resolved_article": "a9"}
{"id": "T-1010", "body": "Is anyone there on saturday?!", "resolved_article": "a4"}
{"id": "T-1011", "body": "Can I send lithium batteries by air? Asking for a client.", "resolved_article": "a7"}
{"id": "T-1012", "body": "Good morning! Driver came twice and I missed him... what happens now?", "resolved_article": "a9"}
EOF
```

## What to build

Write `/root/fde-lab/26-golden/mine.py`, used as `python mine.py TICKETS OUT`:

1. Skip tickets with no `resolved_article`.
2. Split the body into sentences with `re.split(r"(?<=[.!?])\s+", body.strip())` and take the **first sentence that ends with `?`**. Skip the ticket if there isn't one.
3. **De-duplicate**: two questions are the same when they match after lower-casing, replacing every character except `a-z`, `0-9` and space with a space, and collapsing whitespace. Keep the first one.
4. Write each kept question to `OUT` as JSONL: `{"id": ticket id, "question": ..., "source": resolved_article}`, in ticket order.
5. Print `N questions from M tickets`, then one line per source - `a9: 2` - counting **every** ticket with a question (duplicates included), most frequent first, ties by id.

```bash
cd /root/fde-lab/26-golden
python mine.py tickets.jsonl candidates.jsonl
cat candidates.jsonl
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Count the source before the duplicate check - the count is the demand signal, the file is the unique cases.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/26-golden
cat > mine.py <<'EOF'
import json
import re
import sys
from collections import Counter


def first_question(body):
    for sentence in re.split(r"(?<=[.!?])\s+", body.strip()):
        if sentence.strip().endswith("?"):
            return sentence.strip()
    return None


def normalise(text):
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())


def mine(tickets):
    out, seen, counts = [], set(), Counter()
    for t in tickets:
        if not t.get("resolved_article"):
            continue
        q = first_question(t["body"])
        if not q:
            continue
        counts[t["resolved_article"]] += 1
        key = normalise(q)
        if key in seen:
            continue
        seen.add(key)
        out.append({"id": t["id"], "question": q, "source": t["resolved_article"]})
    return out, counts


if __name__ == "__main__":
    tickets = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    rows, counts = mine(tickets)
    with open(sys.argv[2], "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"{len(rows)} questions from {len(tickets)} tickets")
    for source, n in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"{source}: {n}")

EOF
python mine.py tickets.jsonl candidates.jsonl
cat candidates.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/26-golden; cd $D 2>/dev/null || echo "❌ create $D"
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
hidden = [
    {"id": "X1", "body": "Hello! Can I ship a pallet of 900 kg? We have a big order.", "resolved_article": "a6"},
    {"id": "X2", "body": "Thank you so much.", "resolved_article": "a6"},
    {"id": "X3", "body": "can I ship a pallet of 900 KG", "resolved_article": "a6"},
    {"id": "X4", "body": "Hi. Can I ship a pallet of 900 kg?? Urgent.", "resolved_article": "a6"},
    {"id": "X5", "body": "When do invoices go out? And what are the terms?", "resolved_article": "a8"},
    {"id": "X6", "body": "When is support open?", "resolved_article": None},
    {"id": "X7", "body": "Where's my parcel? It's been a week.", "resolved_article": "a5"},
    {"id": "X8", "body": "Where's my parcel?", "resolved_article": "a5"},
]
Path("/tmp/hidden-tickets.jsonl").write_text("".join(json.dumps(t) + "\n" for t in hidden))
rc, out, err = run("mine.py", "/tmp/hidden-tickets.jsonl", "/tmp/hidden-out.jsonl")
got = [json.loads(l) for l in open("/tmp/hidden-out.jsonl")] if rc == 0 and Path("/tmp/hidden-out.jsonl").exists() else []
want = [{"id": "X1", "question": "Can I ship a pallet of 900 kg?", "source": "a6"},
        {"id": "X5", "question": "When do invoices go out?", "source": "a8"},
        {"id": "X7", "question": "Where's my parcel?", "source": "a5"}]
ok(got == want, "mine.py filtered, extracted and de-duplicated an unseen ticket dump correctly", f"on an unseen dump expected {want} - got {got} {err[-200:]}")
lines = out.splitlines()
ok(lines[:1] == ["3 questions from 8 tickets"] and lines[1:] == ["a5: 2", "a6: 2", "a8: 1"], "the summary counts every question per source, most frequent first", f"expected '3 questions from 8 tickets' then a5: 2, a6: 2, a8: 1 - got {lines}")
Path("/tmp/hidden-out.jsonl").unlink(missing_ok=True)
ok(Path("candidates.jsonl").exists() and len(Path("candidates.jsonl").read_text().splitlines()) == 6, "candidates.jsonl holds the six unique questions from the real dump", "run mine.py on tickets.jsonl to write candidates.jsonl (six unique questions)")
PYEOF
```

## What you learned

- Real tickets are the best source of eval questions.
- Filter, extract, de-duplicate and count in code; review the candidates by hand.
- Duplicate counts show where the volume is - weight the eval set toward it.
