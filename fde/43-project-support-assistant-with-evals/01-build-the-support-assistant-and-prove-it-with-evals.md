---
type: task
title: "Build the support assistant and prove it with evals"
minutes: 75
---

## Scenario

Meridian Logistics wants a support assistant that answers two kinds of question: **where is my order** (from their orders API) and **what's the policy** (from the help articles). Their head of support won't approve a pilot on a demo - she wants a golden dataset and an eval report.

You'll combine tool calling (topics 11 and 20), a customer API (topic 23), retrieval (topic 14) and evals (topics 26-28).

## Set up

Set up starts Meridian's orders API on `127.0.0.1:4570` (`GET /orders/MER-90001` returns the order, unknown ids return `404` with `{"error": "no such order"}`), and writes the twelve help articles to `articles.json`.

```bash
mkdir -p /root/fde-lab/43-support-evals
cd /root/fde-lab/43-support-evals
cat > orders.json <<'EOF'
{
  "MER-90001": {
    "status": "delivered, signed by J. Okafor",
    "updated": "2026-03-12"
  },
  "MER-90002": {
    "status": "held at customs - commercial invoice missing",
    "updated": "2026-03-13"
  },
  "MER-90003": {
    "status": "awaiting collection at depot LDS-02",
    "depot_hours": "06:00-20:00",
    "updated": "2026-03-14"
  },
  "MER-90004": {
    "status": "in transit to Rotterdam hub RTM-01",
    "updated": "2026-03-14"
  }
}
EOF
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
cat > mock_api.py <<'EOF'
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ORDERS = json.loads(Path(__file__).with_name("orders.json").read_text())


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True})
        m = re.fullmatch(r"/orders/([A-Za-z0-9-]+)", self.path)
        if not m:
            return self._send(404, {"error": "unknown path"})
        order = ORDERS.get(m[1].upper())
        if order:
            return self._send(200, {"order_id": m[1].upper(), **order})
        self._send(404, {"error": "no such order"})


ThreadingHTTPServer(("127.0.0.1", 4570), H).serve_forever()
EOF
curl -fsS -o /dev/null http://127.0.0.1:4570/health 2>/dev/null || (nohup python mock_api.py > mock_api.out 2>&1 &)
for i in $(seq 1 20); do curl -fsS -o /dev/null http://127.0.0.1:4570/health 2>/dev/null && break; sleep 0.5; done
curl -fsS http://127.0.0.1:4570/health && echo "  <- Meridian orders API is up on 127.0.0.1:4570"
```

## What to build

**1. `assistant.py`** with `run(question, max_steps=5)` returning `{"answer": str, "tools": [names of tools called, in order]}`:

- Two tools: `get_order(order_id)` - calls the API (a 404 returns its JSON error body as the result), and `search_help(query)` - the **two** best-matching articles by embedding similarity, as `[{"id", "title", "text"}]`. Embed the articles once per process.
- The tool loop on `lab-fast` at `temperature=0`, with this system prompt:
  ```text
  You are Meridian Logistics' support assistant. Use get_order for questions about a specific order and search_help for policy questions. Answer in one or two sentences. If the tools don't give you the answer, reply exactly: I don't know based on the provided sources.
  ```
- A max-steps guard (topic 21). `python assistant.py QUESTION` prints the result as JSON.

**2. `golden.jsonl`** - at least **8** cases: `{"id", "type", "question", "expect_tool", "must_include"}`. Types `order`, `policy` and `trap`; at least **three** `get_order` cases (one with an unknown order id), **two** `search_help` cases, and **one** trap whose `must_include` is the refusal and `expect_tool` is `null`.

**3. `eval.py`** - used as `python eval.py GOLDEN`. A case passes when every `must_include` string is in the answer (case-insensitive) **and**, if `expect_tool` is set, that tool was called. Write `report.json`:

```json
{"passed": 7, "total": 8, "score": 0.875, "by_type": {"order": {"passed": 4, "total": 5}}, "failures": ["o5"]}
```

and print `score: N/M`. Trace each case to stderr.

```bash
cd /root/fde-lab/43-support-evals
python assistant.py "Where is order MER-90001?"
python eval.py golden.jsonl
cat report.json
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `urllib.error.HTTPError` has `.code` and `.read()` - the 404 body is the useful tool result.
- Write the golden set before you tune the prompt - otherwise you'll write cases your assistant already passes.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/43-support-evals
cat > assistant.py <<'EOF'
import json
import math
import sys
import urllib.error
import urllib.request
from pathlib import Path

from openai import OpenAI

client = OpenAI()
API = "http://127.0.0.1:4570"
ARTICLES = json.loads(Path(__file__).with_name("articles.json").read_text())
SYSTEM = "You are Meridian Logistics' support assistant. Use get_order for questions about a specific order and search_help for policy questions. Answer in one or two sentences. If the tools don't give you the answer, reply exactly: I don't know based on the provided sources."
TOOLS = [
    {"type": "function", "function": {
        "name": "get_order",
        "description": "Current status of a Meridian order by order id, like MER-12345.",
        "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}}},
    {"type": "function", "function": {
        "name": "search_help",
        "description": "Search Meridian's help articles for policy questions. Returns the two best matching articles.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
]
_VECS = None


def get_order(order_id):
    try:
        with urllib.request.urlopen(f"{API}/orders/{order_id.strip().upper()}", timeout=5) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}") or {"error": f"HTTP {e.code}"}


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def search_help(query):
    global _VECS
    if _VECS is None:
        _VECS = [d.embedding for d in client.embeddings.create(model="lab-embed", input=[f"{a['title']}. {a['text']}" for a in ARTICLES]).data]
    q = client.embeddings.create(model="lab-embed", input=[query]).data[0].embedding
    ranked = sorted(zip(_VECS, ARTICLES), key=lambda x: cosine(x[0], q), reverse=True)[:2]
    return [{"id": a["id"], "title": a["title"], "text": a["text"]} for _, a in ranked]


FUNCS = {"get_order": get_order, "search_help": search_help}


def run(question, max_steps=5):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    used = []
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", temperature=0, tools=TOOLS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return {"answer": (msg.content or "").strip(), "tools": used}
        messages.append(msg)
        for call in msg.tool_calls:
            name, args = call.function.name, json.loads(call.function.arguments)
            used.append(name)
            result = FUNCS[name](**args) if name in FUNCS else {"error": f"unknown tool {name}"}
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return {"answer": f"Stopped after {max_steps} steps without an answer.", "tools": used}


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1])))

EOF
cat > eval.py <<'EOF'
import json
import sys

from assistant import run


def evaluate(cases):
    failures, by_type = [], {}
    for c in cases:
        r = run(c["question"])
        text = r["answer"].lower()
        passed = all(s.lower() in text for s in c["must_include"]) and (c.get("expect_tool") is None or c["expect_tool"] in r["tools"])
        t = by_type.setdefault(c["type"], {"passed": 0, "total": 0})
        t["total"] += 1
        t["passed"] += passed
        if not passed:
            failures.append(c["id"])
        print(f"{c['id']} {'PASS' if passed else 'FAIL'} tools={r['tools']} answer={r['answer'][:80]!r}", file=sys.stderr)
    passed = len(cases) - len(failures)
    return {"passed": passed, "total": len(cases), "score": passed / len(cases), "by_type": by_type, "failures": failures}


if __name__ == "__main__":
    cases = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    report = evaluate(cases)
    with open("report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"score: {report['passed']}/{report['total']}")

EOF
cat > golden.jsonl <<'EOF'
{"id": "o1", "type": "order", "question": "Where is order MER-90001?", "expect_tool": "get_order", "must_include": ["delivered", "Okafor"]}
{"id": "o2", "type": "order", "question": "Why is MER-90002 stuck?", "expect_tool": "get_order", "must_include": ["customs", "commercial invoice"]}
{"id": "o3", "type": "order", "question": "Can I pick up MER-90003 today?", "expect_tool": "get_order", "must_include": ["LDS-02"]}
{"id": "o4", "type": "order", "question": "What's the status of MER-90004?", "expect_tool": "get_order", "must_include": ["Rotterdam"]}
{"id": "o5", "type": "order", "question": "Where is order MER-99999?", "expect_tool": "get_order", "must_include": ["can't find"]}
{"id": "p1", "type": "policy", "question": "How long do I have to report damage?", "expect_tool": "search_help", "must_include": ["7 days"]}
{"id": "p2", "type": "policy", "question": "Can I send lithium batteries by plane?", "expect_tool": "search_help", "must_include": ["road"]}
{"id": "t1", "type": "trap", "question": "Who is Meridian's CEO?", "expect_tool": null, "must_include": ["I don't know based on the provided sources."]}
EOF
python assistant.py "Where is order MER-90001?"
python eval.py golden.jsonl
cat report.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/43-support-evals; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/assistant.py 2>/dev/null && [ -s $D/assistant.py ] && echo "✅ assistant.py reads the key from the environment" || echo "❌ assistant.py must not contain a key - let the SDK read it from the environment"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/eval.py 2>/dev/null && [ -s $D/eval.py ] && echo "✅ eval.py reads the key from the environment" || echo "❌ eval.py must not contain a key - let the SDK read it from the environment"
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
REFUSE = "I don't know based on the provided sources."
rows = []
for line in (Path("golden.jsonl").read_text().splitlines() if Path("golden.jsonl").exists() else []):
    if line.strip():
        try:
            rows.append(json.loads(line))
        except ValueError:
            rows.append({})
keys = {"id", "type", "question", "expect_tool", "must_include"}
ok(len(rows) >= 8 and all(keys <= set(r) and isinstance(r.get("must_include"), list) and r["must_include"] for r in rows) and len({r.get("id") for r in rows}) == len(rows),
   f"golden.jsonl has {len(rows)} complete cases with unique ids", "golden.jsonl needs 8+ cases with id, type, question, expect_tool and a non-empty must_include list")
tools = [r.get("expect_tool") for r in rows]
traps = [r for r in rows if r.get("type") == "trap"]
ok(tools.count("get_order") >= 3 and tools.count("search_help") >= 2 and any(t.get("expect_tool") is None and t.get("must_include") == [REFUSE] for t in traps) and any(re.search(r"MER-\d+", r.get("question", "")) and r.get("expect_tool") == "get_order" and not any(o in r.get("question", "") for o in ['MER-90001', 'MER-90002', 'MER-90003', 'MER-90004']) for r in rows),
   "the golden set covers orders (including an unknown id), policies and a trap", "need 3+ get_order cases (one with an unknown order id), 2+ search_help cases and a trap expecting exactly the refusal")
rep = load("report.json") or {}
ok(rep.get("total") == len(rows) and {"passed", "total", "score", "by_type", "failures"} <= set(rep), "report.json covers your whole golden set", f"run eval.py on golden.jsonl - report.json should have total {len(rows)} - got {rep}")
r = subprocess.run([sys.executable, "assistant.py", "Where is order MER-90001?"], capture_output=True, text=True)
try:
    a = json.loads(r.stdout.splitlines()[-1])
except Exception:
    a = {}
ok(a.get("tools") == ["get_order"] and "okafor" in str(a.get("answer")).lower(), "the assistant looked the order up through the API", f"expected tools ['get_order'] and the signer's name in the answer - got {a} {r.stderr[-200:]}")
hidden = [
    {"id": "x1", "type": "order", "question": "Where is order MER-90001?", "expect_tool": "get_order", "must_include": ["delivered", "Okafor"]},
    {"id": "x2", "type": "order", "question": "Why is MER-90002 stuck?", "expect_tool": "get_order", "must_include": ["customs", "commercial invoice"]},
    {"id": "x3", "type": "order", "question": "Can I pick up MER-90003 today?", "expect_tool": "get_order", "must_include": ["LDS-02", "Saturday"]},
    {"id": "x4", "type": "policy", "question": "How long do I have to report damage?", "expect_tool": "search_help", "must_include": ["7 days"]},
    {"id": "x5", "type": "policy", "question": "Can I send lithium batteries by plane?", "expect_tool": "search_help", "must_include": ["ROAD"]},
    {"id": "x6", "type": "trap", "question": "Who is Meridian's CEO?", "expect_tool": None, "must_include": [REFUSE]},
    {"id": "x7", "type": "trap", "question": "Who is Meridian's CEO?", "expect_tool": "search_help", "must_include": [REFUSE]},
]
import shutil, tempfile
tmp = tempfile.mkdtemp()
for f in ("assistant.py", "eval.py", "articles.json"):
    if Path(f).exists():
        shutil.copy(f, tmp)
Path(tmp, "hidden.jsonl").write_text("".join(json.dumps(c) + "\n" for c in hidden))
r = subprocess.run([sys.executable, "eval.py", "hidden.jsonl"], capture_output=True, text=True, cwd=tmp)
got = load(Path(tmp, "report.json")) or {}
want = {"passed": 5, "total": 7, "by_type": {"order": {"passed": 2, "total": 3}, "policy": {"passed": 2, "total": 2}, "trap": {"passed": 1, "total": 2}}, "failures": ["x3", "x7"]}
ok({k: got.get(k) for k in want} == want and abs(got.get("score", 0) - 5 / 7) < 1e-6 and r.stdout.strip().endswith("score: 5/7"),
   "eval.py scored an unseen golden set correctly, including the tool requirement", f"on an unseen set expected {want} and 'score: 5/7' - got {got} {r.stdout[-100:]!r} {r.stderr[-300:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and (.tools | index("get_order")) and .temperature == 0)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-fast call" || echo "❌ the gateway has no lab-fast call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A support assistant combines API tools, retrieval and a guarded tool loop.
- A golden set covers each kind of question, including unknown ids and traps.
- Evals check both the answer and that the right tool was used.
