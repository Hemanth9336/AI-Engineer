---
type: task
title: "Run a full engagement end to end"
minutes: 90
---

## Scenario

Dockside Retail has hired you for a six-week engagement. This capstone runs the whole thing in miniature - every artefact you'd hand a real customer: scope it, build it, prove it, price it, and hand it over.

## Set up

`brief.md` is the customer's brief. `store-policies.json` holds the eight store policies. `prices.json` has dollars per million tokens.

```bash
mkdir -p /root/fde-lab/44-engagement
cd /root/fde-lab/44-engagement
cat > brief.md <<'EOF'
# Engagement brief: Dockside Retail store assistant

From: Sanne de Wit, Head of Store Operations, Dockside Retail

- 220 stores, about 6,000 store staff.
- Store staff send about 4,000 policy questions a month to the operations helpdesk
  (returns, refunds, cash handling, shift swaps...). Average answer time: 1.5 working days.
- The answers are in the store policy manual (store-policies.json - eight policies).
- The helpdesk team (5 people) wants to spend their time on real problems, not repeat questions.
- Ideas raised: a staff chatbot, automatic approval of cash refunds, a sales forecasting tool.
- Staff questions sometimes include customer names and phone numbers.
- Budget holder: the CFO wants to know the monthly running cost before approving.
- Timeline: pilot in 6 weeks.
EOF
cat > store-policies.json <<'EOF'
[
  {
    "id": "p1",
    "title": "Returns",
    "text": "Customers can return items within 30 days with a receipt. Electronics can be returned within 14 days, unopened. Items without a receipt get store credit only."
  },
  {
    "id": "p2",
    "title": "Refunds",
    "text": "Refunds go back to the original payment method. Cash refunds above 200 EUR need a shift manager's approval."
  },
  {
    "id": "p3",
    "title": "Cash handling",
    "text": "Tills are counted at close by two staff members. The till float is 300 EUR. Report differences above 10 EUR to the store manager the same day."
  },
  {
    "id": "p4",
    "title": "Opening hours",
    "text": "Stores open 08:00 to 21:00 Monday to Saturday and 10:00 to 18:00 on Sunday. Public holiday hours are set by head office each year."
  },
  {
    "id": "p5",
    "title": "Staff discount",
    "text": "Staff get a 15 percent discount on full-price items after their probation period. The discount cannot be combined with promotions."
  },
  {
    "id": "p6",
    "title": "Shift swaps",
    "text": "Swap shifts in the StaffHub app at least 48 hours ahead. Both staff members and the shift manager must accept the swap."
  },
  {
    "id": "p7",
    "title": "Lost property",
    "text": "Lost property is logged in the store book and kept for 30 days. Phones, wallets and keys are kept in the manager's safe."
  },
  {
    "id": "p8",
    "title": "Incident reporting",
    "text": "Report any accident or safety incident on the safety portal within 24 hours, even if nobody was hurt."
  }
]
EOF
cat > prices.json <<'EOF'
{
  "lab-mini": {
    "input": 0.1,
    "output": 0.4
  },
  "lab-fast": {
    "input": 0.4,
    "output": 1.6
  },
  "lab-smart": {
    "input": 3.0,
    "output": 15.0
  }
}
EOF
rm -f calls.jsonl
```

## What to build

Work in `/root/fde-lab/44-engagement`. Five deliverables:

**1. Scope - `scope.md`** with `##` sections `Problem`, `Use case`, `Success metrics` (3+ bullets with numbers), `Out of scope` (deal with the two bad-fit ideas in the brief, with reasons) and `Risks` (including the personal data in staff questions).

**2. Build - `bot.py`** with `answer(question)` returning `{"answer", "citations"}`:
- Top 3 policies by embedding similarity (`"<title>. <text>"`, policies embedded once per process), kept only if they score at least **0.3**; none left -> the refusal with no chat call.
- `lab-fast`, `temperature=0`, JSON mode; the system prompt followed by `[p1] title. text` lines:
  ```text
  You answer Dockside Retail store staff from the Dockside Retail store policy manual. Use only the policies below and cite policy ids like [p1]. If they don't answer the question, the answer must be exactly: I don't know based on the provided sources. Reply with JSON: {"answer": "...", "citations": ["p1"]}
  ```
- Citations must be among the sources; a refusal has none; an uncited answer becomes the refusal.
- Log every chat call to `calls.jsonl` next to the script: `ts`, `model`, `ok`, `prompt_tokens`, `completion_tokens`, `latency_ms`.
- `python bot.py QUESTION` prints the result as JSON.

**3. Prove - `golden.jsonl` and `eval.py`.** At least **8** cases `{"id", "type", "question", "must_include"}` with types `easy`, `hard` and `trap` (at least **two** traps, whose `must_include` is the refusal). `python eval.py golden.jsonl` writes `results.json` - `{"passed", "total", "score", "by_type", "failures"}` - and prints `score: N/M ...`.

**4. Price - `cost.py`**, used as `python cost.py calls.jsonl REQUESTS_PER_MONTH prices.json MODEL`. From the logged `ok` calls for that model, compute average prompt and completion tokens and write `cost.json`:

```json
{"model": "lab-fast", "requests_per_month": 4000, "measured_calls": 7, "avg_prompt_tokens": 390.3, "avg_completion_tokens": 21.4,
 "cost_per_request_usd": 0.00019, "monthly_cost_usd": 0.76}
```

(averages rounded to 1 decimal, per-request cost to 6, monthly to 2 - computed from the unrounded averages).

**5. Hand over - `RUNBOOK.md`** with `##` sections `Overview`, `Running it`, `Monitoring`, `Evals` (the eval command in a fenced code block) and `Contacts`.

```bash
cd /root/fde-lab/44-engagement
python bot.py "How long do customers have to return electronics?"
python eval.py golden.jsonl
python cost.py calls.jsonl 4000 prices.json lab-fast
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Run the eval before the cost estimate - the eval run is what fills calls.jsonl with realistic traffic.
- Off-topic traps never reach the model, so they don't appear in calls.jsonl - that's part of why routing and thresholds save money.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/44-engagement
cat > scope.md <<'EOF'
# Scoping: Dockside Retail store policy assistant

## Problem
Store staff send ~4,000 policy questions a month to a 5-person helpdesk; answers take 1.5 working days on average, and most are repeat questions answered in the store policy manual.

## Use case
An internal assistant for store staff that answers policy questions from the store policy manual, citing the policy it used and refusing when the manual doesn't cover the question.

## Success metrics
- 90% correct on the golden set, graded against expected answers from the helpdesk team.
- 100% of trap questions refused.
- Answer time for policy questions from 1.5 working days to under 1 minute.
- Helpdesk policy tickets down 40% after 6 weeks.

## Out of scope
- Automatic approval of cash refunds - moves money with no human check; refunds keep the existing manager approval.
- Sales forecasting - a numerical forecasting problem better solved with classical ML on sales data.
- Answering customers directly - staff-only until quality is proven in the pilot.

## Risks
- Staff questions can include customer names and phone numbers: redact PII before model calls and log only redacted prompts.
- The policy manual may be out of date: head office owns updates and the index is rebuilt on every change.
- Staff may trust a wrong answer: every answer cites its policy and the pilot includes feedback buttons.
EOF
cat > bot.py <<'EOF'
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

client = OpenAI()
HERE = Path(__file__).parent
POLICIES = json.loads((HERE / "store-policies.json").read_text())
REFUSE = "I don't know based on the provided sources."
SYSTEM = 'You answer Dockside Retail store staff from the Dockside Retail store policy manual. Use only the policies below and cite policy ids like [p1]. If they don\'t answer the question, the answer must be exactly: I don\'t know based on the provided sources. Reply with JSON: {"answer": "...", "citations": ["p1"]}'
_VECS = None


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def log_call(entry):
    with open(HERE / "calls.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")


def answer(question, k=3, min_score=0.3):
    global _VECS
    if _VECS is None:
        _VECS = [d.embedding for d in client.embeddings.create(model="lab-embed", input=[f"{p['title']}. {p['text']}" for p in POLICIES]).data]
    q = client.embeddings.create(model="lab-embed", input=[question]).data[0].embedding
    scored = sorted(zip([cosine(v, q) for v in _VECS], POLICIES), key=lambda x: x[0], reverse=True)[:k]
    sources = [p for s, p in scored if s >= min_score]
    if not sources:
        return {"answer": REFUSE, "citations": []}
    context = "\n".join(f"[{p['id']}] {p['title']}. {p['text']}" for p in sources)
    start = time.perf_counter()
    resp = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": f"{SYSTEM}\n\n{context}"}, {"role": "user", "content": question}],
    )
    log_call({"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "model": "lab-fast", "ok": True,
              "prompt_tokens": resp.usage.prompt_tokens, "completion_tokens": resp.usage.completion_tokens,
              "latency_ms": round((time.perf_counter() - start) * 1000)})
    result = json.loads(resp.choices[0].message.content)
    ids = [p["id"] for p in sources]
    text = str(result.get("answer", "")).strip()
    citations = [] if text == REFUSE else [c for c in result.get("citations") or [] if c in ids]
    if text != REFUSE and not citations:
        return {"answer": REFUSE, "citations": []}
    return {"answer": text, "citations": citations}


if __name__ == "__main__":
    print(json.dumps(answer(sys.argv[1])))

EOF
cat > eval.py <<'EOF'
import json
import sys

from bot import answer

cases = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
failures, by_type = [], {}
for c in cases:
    r = answer(c["question"])
    passed = all(s.lower() in r["answer"].lower() for s in c["must_include"])
    t = by_type.setdefault(c["type"], {"passed": 0, "total": 0})
    t["total"] += 1
    t["passed"] += passed
    if not passed:
        failures.append(c["id"])
passed = len(cases) - len(failures)
results = {"passed": passed, "total": len(cases), "score": passed / len(cases), "by_type": by_type, "failures": failures}
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"score: {passed}/{len(cases)} failures={failures}")

EOF
cat > cost.py <<'EOF'
import json
import sys

log, per_month, prices, model = sys.argv[1], int(sys.argv[2]), json.load(open(sys.argv[3])), sys.argv[4]
rows = [json.loads(l) for l in open(log) if l.strip()]
rows = [r for r in rows if r.get("ok") and r.get("model") == model]
avg_in = sum(r["prompt_tokens"] for r in rows) / len(rows)
avg_out = sum(r["completion_tokens"] for r in rows) / len(rows)
per_request = (avg_in * prices[model]["input"] + avg_out * prices[model]["output"]) / 1_000_000
estimate = {
    "model": model,
    "requests_per_month": per_month,
    "measured_calls": len(rows),
    "avg_prompt_tokens": round(avg_in, 1),
    "avg_completion_tokens": round(avg_out, 1),
    "cost_per_request_usd": round(per_request, 6),
    "monthly_cost_usd": round(per_request * per_month, 2),
}
with open("cost.json", "w") as f:
    json.dump(estimate, f, indent=2)
print(json.dumps(estimate))

EOF
cat > golden.jsonl <<'EOF'
{"id": "g1", "type": "easy", "question": "How long do customers have to return electronics?", "must_include": ["14 days"]}
{"id": "g2", "type": "easy", "question": "What's the staff discount?", "must_include": ["15"]}
{"id": "g3", "type": "easy", "question": "Can I swap my shift tomorrow?", "must_include": ["48 hours"]}
{"id": "g4", "type": "hard", "question": "Who approves a 250 EUR cash refund?", "must_include": ["shift manager"]}
{"id": "g5", "type": "hard", "question": "What should I do with a lost phone?", "must_include": ["safe"]}
{"id": "g6", "type": "easy", "question": "When do stores open on Sunday?", "must_include": ["10:00"]}
{"id": "t1", "type": "trap", "question": "What is the bonus for store managers?", "must_include": ["I don't know based on the provided sources."]}
{"id": "t2", "type": "trap", "question": "What's the capital of Peru?", "must_include": ["I don't know based on the provided sources."]}
EOF
cat > RUNBOOK.md <<'EOF'
# Runbook: Dockside Retail store policy assistant

## Overview
Answers store staff policy questions from store-policies.json with citations; refuses when the manual doesn't cover a question. Business owner: Sanne de Wit, Head of Store Operations.

## Running it
- Ask a question: `python bot.py "QUESTION"`.
- After a policy change, update store-policies.json and re-run the evals before releasing.

## Monitoring
- Every model call is logged to calls.jsonl with tokens and latency.
- Watch the daily error count, p95 latency and token cost against the monthly estimate in cost.json.

## Evals
~~~bash
python eval.py golden.jsonl
~~~
Do not release if the score drops or any trap question stops being refused. Add every reported wrong answer to golden.jsonl.

## Contacts
- Business owner: Sanne de Wit, Head of Store Operations.
- Golden set owner: the operations helpdesk team lead.
- Platform and on-call: Dockside IT service desk.
EOF
python bot.py "How long do customers have to return electronics?"
python eval.py golden.jsonl
python cost.py calls.jsonl 4000 prices.json lab-fast
```

</details>

## Check your work

```bash
D=/root/fde-lab/44-engagement; cd $D 2>/dev/null || echo "❌ create $D"
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
def chats():
    return sum(1 for l in open("/var/log/ailab/requests.jsonl") if '"chat.completions"' in l)

REFUSE = "I don't know based on the provided sources."
s = sections("scope.md")
missing = [h for h in ("problem", "use case", "success metrics", "out of scope", "risks") if not s.get(h)]
ok(not missing and len([l for l in s.get("success metrics", []) if re.search(r"\d", l)]) >= 3, "scope.md has the five sections and numeric success metrics", f"missing or empty sections {missing}, or fewer than 3 metrics with numbers")
oos = " ".join(s.get("out of scope", [])).lower()
ok("refund" in oos and "forecast" in oos and re.search(r"pii|personal|redact|phone", " ".join(s.get("risks", [])), re.I), "scope puts the refund and forecasting ideas out of scope and handles personal data", "Out of scope should address the cash-refund approval and forecasting ideas; Risks should cover personal data")
calls = [json.loads(l) for l in open("calls.jsonl")] if Path("calls.jsonl").exists() else []
ok(calls and all({"ts", "model", "ok", "prompt_tokens", "completion_tokens", "latency_ms"} <= set(c) for c in calls), f"calls.jsonl logged {len(calls)} calls with tokens and latency", "bot.py must log every chat call to calls.jsonl with ts, model, ok, prompt_tokens, completion_tokens and latency_ms")
golden = [json.loads(l) for l in open("golden.jsonl") if l.strip()] if Path("golden.jsonl").exists() else []
traps = [g for g in golden if g.get("type") == "trap"]
ok(len(golden) >= 8 and len(traps) >= 2 and all(t.get("must_include") == [REFUSE] for t in traps) and {"easy", "hard"} <= {g.get("type") for g in golden}, "golden.jsonl has 8+ cases with easy, hard and two or more traps", "golden.jsonl needs 8+ cases, types easy/hard/trap, and 2+ traps expecting exactly the refusal")
res = load("results.json") or {}
ok(res.get("total") == len(golden) and res.get("passed") == res.get("total", 0) - len(res.get("failures") or []) and {"score", "by_type"} <= set(res), "results.json covers the golden set and adds up", f"run eval.py on golden.jsonl - results.json should have total {len(golden)} and passed = total - failures - got {res}")
cost = load("cost.json") or {}
fast = [c for c in calls if c.get("ok") and c.get("model") == cost.get("model")]
prices = load("prices.json")
if fast and cost.get("model") in prices:
    ai = sum(c["prompt_tokens"] for c in fast) / len(fast)
    ao = sum(c["completion_tokens"] for c in fast) / len(fast)
    pr = (ai * prices[cost["model"]]["input"] + ao * prices[cost["model"]]["output"]) / 1e6
    want = {"model": cost["model"], "requests_per_month": 4000, "measured_calls": len(fast), "avg_prompt_tokens": round(ai, 1), "avg_completion_tokens": round(ao, 1), "cost_per_request_usd": round(pr, 6), "monthly_cost_usd": round(pr * 4000, 2)}
else:
    want = None
ok(want is not None and cost == want, "cost.json matches the logged calls and the prices", f"cost.json should be computed from calls.jsonl for 4,000 requests a month - expected {want}, got {cost}")
def ask(q):
    before = chats()
    rc, out, err = run("bot.py", q)
    try:
        return json.loads(out.splitlines()[-1]), chats() - before
    except Exception:
        return {"raw": out[-200:] + err[-200:]}, chats() - before
r, n = ask("How long do customers have to return electronics?")
ok(r.get("citations") == ["p1"] and "14 days" in str(r.get("answer")), "the bot answers a returns question from p1 with a citation", f"expected an answer with 14 days citing p1 - got {r}")
r, n = ask("What is the bonus for store managers?")
ok(r.get("answer") == REFUSE and r.get("citations") == [] and n == 1, "an uncovered policy question is refused by the model", f"expected exactly the refusal after one chat call - got {r}, {n} calls")
r, n = ask("What's the capital of Peru?")
ok(r.get("answer") == REFUSE and n == 0, "an off-topic question is refused without a chat call", f"expected the refusal and no chat call - got {r}, {n} calls")
rb = sections("RUNBOOK.md")
text = Path("RUNBOOK.md").read_text() if Path("RUNBOOK.md").exists() else ""
ev = re.search(r"^## Evals\s*$(.*?)(?=^## |\Z)", text, re.M | re.S | re.I)
missing = [h for h in ("overview", "running it", "monitoring", "evals", "contacts") if not rb.get(h)]
ok(not missing and ev and ("`" * 3 in ev.group(1) or "~" * 3 in ev.group(1)) and "eval.py" in ev.group(1), "RUNBOOK.md has the five sections and the eval command in a code block", f"missing or empty sections {missing}, or no fenced eval.py command under Evals")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and .json_mode and .temperature == 0 and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-fast call" || echo "❌ the gateway has no lab-fast call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- An engagement produces artefacts the customer keeps: scope, system, evals, cost estimate and runbook.
- Cost estimates come from measured traffic, not guesses.
- Every deliverable is checkable - that's what makes the handoff credible.
