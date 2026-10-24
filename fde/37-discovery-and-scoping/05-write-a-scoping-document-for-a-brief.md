---
type: task
title: "Write a scoping document for a brief"
minutes: 10
---

## Set up

`brief.md` is the brief Harbor Foods sent before your first meeting.

```bash
mkdir -p /root/fde-lab/37-scoping
cd /root/fde-lab/37-scoping
cat > brief.md <<'EOF'
# Brief: Harbor Foods - AI for supplier support

From: Marta Kovacs, Head of Supplier Operations, Harbor Foods
Harbor Foods runs three warehouses supplied by 1,400 food suppliers.

## What we see today
- Our 6-person supplier desk gets about 2,300 emails a month. Roughly 60% are repeat questions
  about delivery slots, temperature rules, pallet labels and invoice disputes.
- The answers are in our 40-page supplier handbook (PDF) and the supplier portal FAQ.
- Average first reply time is 2.5 working days. Suppliers complain; trucks get turned away
  because rules were misunderstood (about 35 rejected deliveries a month).
- Emails live in Zendesk. Invoice data lives in SAP.

## Ideas people have raised
- Our CFO wants AI to "automatically resolve invoice disputes" in SAP.
- IT wants a chatbot on the supplier portal.
- The desk team wants help drafting replies faster.

## Constraints
- Supplier emails contain names, phone numbers and bank details.
- We want something live with real suppliers within 8 weeks.
EOF
```

## What to build

Read the brief and write `/root/fde-lab/37-scoping/scope.md` - the one-page scoping document you'd send back. Use these `##` sections, each with real content:

`Problem`, `Users`, `Use case`, `Success metrics`, `In scope`, `Out of scope`, `Data sources`, `Risks`, `Timeline`

- **Use case** - pick **one** use case from the brief and describe it in a few sentences.
- **Success metrics** - at least **three** bullets, each with a number (a target or a baseline).
- **Out of scope** - at least **two** bullets, each with a reason. Say what happens to the ideas you didn't pick.
- **Data sources** - name the actual systems and documents from the brief.
- **Risks** - at least **two** bullets, including how you'll handle the personal data.
- **Timeline** - fits the customer's 8 weeks.

```bash
cd /root/fde-lab/37-scoping
grep '^## ' scope.md
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Good metrics compare to today's numbers in the brief: 2.5 days, 2,300 emails, 35 rejected deliveries.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/37-scoping
cat > scope.md <<'EOF'
# Scoping: Harbor Foods supplier support assistant

## Problem
The supplier desk answers ~2,300 emails a month; ~60% are repeat questions already answered in the handbook. First replies take 2.5 working days, and misunderstood rules cause ~35 rejected deliveries a month.

## Users
- Primary: the 6 supplier desk agents (draft replies for them to review and send).
- Later: suppliers themselves, via the portal, once quality is proven.

## Use case
A reply-drafting assistant inside Zendesk: for each incoming email, retrieve the relevant handbook and FAQ sections and draft an answer with citations. An agent reviews, edits and sends it.

## Success metrics
- First reply time for repeat questions: from 2.5 working days to under 4 working hours.
- At least 70% of drafts sent with no or light edits (measured in Zendesk).
- 90% correct on a 100-question golden set agreed with the desk team; 100% of out-of-scope questions refused.
- Rejected deliveries caused by misunderstood rules: down 30% after 3 months.

## In scope
- Questions about delivery slots, booking, temperature rules, pallet labels and invoice dispute process.
- English-language emails in Zendesk.

## Out of scope
- Automatically resolving invoice disputes or writing to SAP (needs finance rules and approvals - revisit after the pilot).
- A public supplier chatbot on the portal (phase 2, once drafts reach the quality bar).
- Emails in other languages - almost all supplier email is in English; revisit if the pilot succeeds.

## Data sources
- Supplier handbook PDF (40 pages), split into sections.
- Supplier portal FAQ.
- 6 months of resolved Zendesk tickets, redacted, to build the golden set.

## Risks
- Supplier emails contain PII and bank details: redact before any model call; agree logging with the DPO.
- Handbook and FAQ may contradict each other: desk lead to own a single source of truth.
- Agents may over-trust drafts: keep human review mandatory during the pilot.

## Timeline
- Weeks 1-2: golden set with the desk team, ingestion and prototype.
- Weeks 3-4: evals, redaction, Zendesk integration.
- Weeks 5-8: pilot with all 6 agents, weekly metric review, go/no-go at week 8.
EOF
grep '^## ' scope.md
```

</details>

## Check your work

```bash
D=/root/fde-lab/37-scoping; cd $D 2>/dev/null || echo "❌ create $D"
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

s = sections("scope.md")
want = ['problem', 'users', 'use case', 'success metrics', 'in scope', 'out of scope', 'data sources', 'risks', 'timeline']
missing = [h for h in want if not s.get(h)]
ok(not missing, "scope.md has all nine sections, each with content", f"missing or empty sections: {missing}")
metrics = bullets(s.get("success metrics", []))
ok(len([m for m in metrics if re.search(r"\d", m)]) >= 3, "at least three success metrics with numbers", f"Success metrics needs 3+ bullets with a number - got {metrics}")
out = bullets(s.get("out of scope", []))
ok(len(out) >= 2 and all(len(o.split()) >= 6 for o in out), "out of scope lists at least two items with reasons", f"Out of scope needs 2+ bullets, each with a short reason - got {out}")
data = " ".join(s.get("data sources", [])).lower()
ok(sum(k in data for k in ("handbook", "faq", "zendesk", "sap")) >= 2, "data sources name the systems from the brief", "Data sources should name the real sources from the brief (handbook, FAQ, Zendesk...)")
risks = bullets(s.get("risks", []))
ok(len(risks) >= 2 and re.search(r"pii|personal|redact|bank|privacy|gdpr", " ".join(risks), re.I), "risks include how personal data is handled", f"Risks needs 2+ bullets including personal data handling - got {risks}")
ok(re.search(r"week", " ".join(s.get("timeline", [])), re.I), "the timeline is planned in weeks", "Timeline should lay out the 8 weeks")
PYEOF
```

## What you learned

- A scoping document picks one use case and writes down why the others wait.
- Success metrics compare to today's numbers.
- Data sources, risks and timeline make the plan concrete enough to sign.
