---
type: task
title: "Overlapping tools: the model picks wrong, fix the set"
minutes: 10
---

## Set up

`tools_v1.py` is the overlapping six-tool set from the lesson. `customers.json` and `invoices.json` are the data behind it.

```bash
mkdir -p /root/harness-lab/14-toolsets
cd /root/harness-lab/14-toolsets
cat > customers.json <<'EOF'
[
 {
  "id": "c-1001",
  "name": "Ana Lopez",
  "email": "ana@northwind.example",
  "plan": "pro",
  "region": "eu"
 },
 {
  "id": "c-1002",
  "name": "Ben Okafor",
  "email": "ben@okafor.example",
  "plan": "free",
  "region": "us"
 },
 {
  "id": "c-1003",
  "name": "Ana Berg",
  "email": "ana.berg@fjord.example",
  "plan": "team",
  "region": "eu"
 },
 {
  "id": "c-1004",
  "name": "Chen Wei",
  "email": "chen@lumen.example",
  "plan": "pro",
  "region": "apac"
 }
]
EOF
cat > invoices.json <<'EOF'
[
 {
  "id": "inv-201",
  "customer_id": "c-1001",
  "status": "paid",
  "amount": 49
 },
 {
  "id": "inv-202",
  "customer_id": "c-1001",
  "status": "unpaid",
  "amount": 49
 },
 {
  "id": "inv-203",
  "customer_id": "c-1003",
  "status": "unpaid",
  "amount": 199
 },
 {
  "id": "inv-204",
  "customer_id": "c-1004",
  "status": "paid",
  "amount": 49
 }
]
EOF
cat > tools_v1.py <<'EOF'
SCHEMAS = [
 {
  "type": "function",
  "function": {
   "name": "get_user",
   "description": "Gets a user.",
   "parameters": {
    "type": "object",
    "properties": {
     "id": {
      "type": "string"
     }
    },
    "required": [
     "id"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "fetch_user",
   "description": "Fetch user details.",
   "parameters": {
    "type": "object",
    "properties": {
     "email": {
      "type": "string"
     }
    },
    "required": [
     "email"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "lookup_customer",
   "description": "Look up a customer.",
   "parameters": {
    "type": "object",
    "properties": {
     "name": {
      "type": "string"
     }
    },
    "required": [
     "name"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "get_account",
   "description": "Get account info for a user.",
   "parameters": {
    "type": "object",
    "properties": {
     "id": {
      "type": "string"
     }
    },
    "required": [
     "id"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "get_invoices",
   "description": "Gets invoices.",
   "parameters": {
    "type": "object",
    "properties": {
     "user_id": {
      "type": "string"
     }
    },
    "required": [
     "user_id"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "list_bills",
   "description": "List bills for a customer.",
   "parameters": {
    "type": "object",
    "properties": {
     "customer": {
      "type": "string"
     }
    },
    "required": [
     "customer"
    ]
   }
  }
 }
]
EOF
```

## What to build

1. Write `/root/harness-lab/14-toolsets/tools_v2.py` with exactly three tools - `SCHEMAS` (definitions) and `IMPL` (name to function):
   - `find_customer(query)`: customers whose id or email equals the query, or whose name contains it (all case-insensitive). Return a list of `{"id", "name", "email"}` (at most 10), or the string `no customers match '<query>'`.
   - `get_customer(customer_id)`: the full customer record, or `error: no customer '<id>'. Use find_customer to look up the id.`
   - `list_invoices(customer_id, status=None)`: that customer's invoices, optionally only `paid` or `unpaid` (an `enum`). Unknown customer: the same error as `get_customer`.
   - Every description says when to use the tool, and both `get_customer` and `list_invoices` use the parameter name `customer_id`.
2. Write `pick.py` that asks `lab-fast` the four questions below once with the v1 set and once with the v2 set, records which tool the model picked first (or `null`), and writes `picks.json` as a list of `{"question", "version", "tool"}`:

   - What plan is ana@northwind.example on?
   - Does Ana Berg have unpaid invoices?
   - Show me customer c-1002.
   - List every invoice for c-1001.

```bash
cd /root/harness-lab/14-toolsets
python pick.py && cat picks.json
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `q in (c["id"].lower(), c["email"].lower()) or q in c["name"].lower()` after lowercasing the query.
- Make the descriptions point at each other: "Use find_customer first if you only have a name or email."

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/14-toolsets
cat > tools_v2.py <<'EOF'
import json
from pathlib import Path

HERE = Path(__file__).parent
CUSTOMERS = json.loads((HERE / "customers.json").read_text())
INVOICES = json.loads((HERE / "invoices.json").read_text())

SCHEMAS = [
    {"type": "function", "function": {
        "name": "find_customer",
        "description": "Find customers by id, email address or part of their name. Use it first whenever you don't already have a customer id. Returns id, name and email for up to 10 matches.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "A customer id (c-1001), an email address, or part of a name"}},
            "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "get_customer",
        "description": "Get the full record for one customer - plan, region, email - by customer id. Use find_customer first if you only have a name or email.",
        "parameters": {"type": "object", "properties": {
            "customer_id": {"type": "string", "description": "Customer id, for example c-1001"}},
            "required": ["customer_id"]}}},
    {"type": "function", "function": {
        "name": "list_invoices",
        "description": "List a customer's invoices by customer id, optionally only paid or only unpaid ones. Use it for any billing or payment question.",
        "parameters": {"type": "object", "properties": {
            "customer_id": {"type": "string", "description": "Customer id, for example c-1001"},
            "status": {"type": "string", "enum": ["paid", "unpaid"], "description": "Only invoices with this status; leave out for all"}},
            "required": ["customer_id"]}}},
]


def find_customer(query):
    q = query.strip().lower()
    hits = [c for c in CUSTOMERS if q in (c["id"].lower(), c["email"].lower()) or q in c["name"].lower()]
    if not hits:
        return f"no customers match {query!r}"
    return [{"id": c["id"], "name": c["name"], "email": c["email"]} for c in hits[:10]]


def get_customer(customer_id):
    c = next((c for c in CUSTOMERS if c["id"] == customer_id), None)
    return c or f"error: no customer {customer_id!r}. Use find_customer to look up the id."


def list_invoices(customer_id, status=None):
    if not any(c["id"] == customer_id for c in CUSTOMERS):
        return f"error: no customer {customer_id!r}. Use find_customer to look up the id."
    return [i for i in INVOICES if i["customer_id"] == customer_id and (status is None or i["status"] == status)]


IMPL = {"find_customer": find_customer, "get_customer": get_customer, "list_invoices": list_invoices}

EOF
cat > pick.py <<'EOF'
import json
import sys

from openai import OpenAI

import tools_v1
import tools_v2

QUESTIONS = ["What plan is ana@northwind.example on?", "Does Ana Berg have unpaid invoices?",
             "Show me customer c-1002.", "List every invoice for c-1001."]

client = OpenAI()
rows = []
for q in QUESTIONS:
    for version, schemas in (("v1", tools_v1.SCHEMAS), ("v2", tools_v2.SCHEMAS)):
        msg = client.chat.completions.create(model="lab-fast", tools=schemas, messages=[
            {"role": "system", "content": "You are Stackline's account assistant."},
            {"role": "user", "content": q}]).choices[0].message
        rows.append({"question": q, "version": version, "tool": msg.tool_calls[0].function.name if msg.tool_calls else None})
json.dump(rows, open(sys.argv[1] if len(sys.argv) > 1 else "picks.json", "w"), indent=2)
for r in rows:
    print(f"{r['version']}  {str(r['tool']):16} {r['question']}")

EOF
python pick.py && cat picks.json
```

</details>

## Check your work

```bash
D=/root/harness-lab/14-toolsets; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/pick.py 2>/dev/null && [ -s $D/pick.py ] && echo "✅ pick.py reads the key from the environment" || echo "❌ pick.py must not contain a key - let the SDK read it from the environment"
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
sys.path.insert(0, ".")
try:
    import tools_v2 as t
    names = [s["function"]["name"] for s in t.SCHEMAS]
    fns = {s["function"]["name"]: s["function"] for s in t.SCHEMAS}
except Exception as e:
    t, names, fns = None, [], {}
    ok(False, "", f"tools_v2.py should define SCHEMAS and IMPL - {type(e).__name__}: {e}")
ok(sorted(names) == ["find_customer", "get_customer", "list_invoices"] and t and sorted(t.IMPL) == sorted(names), "tools_v2 has exactly find_customer, get_customer and list_invoices", f"expected exactly those three tools in SCHEMAS and IMPL - got {names}")
if len(fns) == 3:
    ok(all(len(f.get("description", "")) >= 50 and "use" in f["description"].lower() for f in fns.values()), "every description is specific and says when to use the tool", "each description needs 50+ characters and a 'use ...' sentence")
    ok(list(fns["get_customer"]["parameters"]["properties"]) == ["customer_id"] and "customer_id" in fns["list_invoices"]["parameters"]["properties"]
       and fns["list_invoices"]["parameters"]["properties"].get("status", {}).get("enum") == ["paid", "unpaid"], "one name for the id everywhere, and status is an enum", "get_customer and list_invoices should both take customer_id; status should be enum [paid, unpaid]")
    F, G, I = t.IMPL["find_customer"], t.IMPL["get_customer"], t.IMPL["list_invoices"]
    ok(F("ANA") == [{"id": "c-1001", "name": "Ana Lopez", "email": "ana@northwind.example"}, {"id": "c-1003", "name": "Ana Berg", "email": "ana.berg@fjord.example"}]
       and F("chen@lumen.example") == [{"id": "c-1004", "name": "Chen Wei", "email": "chen@lumen.example"}] and F("C-1002") == [{"id": "c-1002", "name": "Ben Okafor", "email": "ben@okafor.example"}]
       and F("zoe") == "no customers match 'zoe'", "find_customer matches name parts, emails and ids, case-insensitively", f"find_customer('ANA') gave {F('ANA')}, find_customer('zoe') gave {F('zoe')!r}")
    ok(G("c-1003").get("plan") == "team" if isinstance(G("c-1003"), dict) else False, "get_customer returns the full record", f"get_customer('c-1003') should include plan team - got {G('c-1003')}")
    ok(G("c-9") == "error: no customer 'c-9'. Use find_customer to look up the id." and I("c-9") == G("c-9"), "unknown ids point the model to find_customer", f"got {G('c-9')!r} / {I('c-9')!r}")
    ok([i["id"] for i in I("c-1001")] == ["inv-201", "inv-202"] and [i["id"] for i in I("c-1001", "unpaid")] == ["inv-202"] and I("c-1002") == [], "list_invoices filters by customer and status", f"got {I('c-1001')}, {I('c-1001', 'unpaid')}")
p = load("picks.json")
ok(isinstance(p, list) and len(p) == 8 and all(set(r) == {"question", "version", "tool"} for r in p) and sorted({r["version"] for r in p}) == ["v1", "v2"], "picks.json records the first tool picked for 4 questions x 2 sets", "run pick.py to write picks.json with 8 rows of question, version, tool")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
ok(any(sorted(x.get("tools") or []) == ["find_customer", "get_customer", "list_invoices"] and x.get("model") == "lab-fast" for x in rows), "the gateway logged real calls offering the new three-tool set", "no lab-fast call offering find_customer, get_customer and list_invoices yet")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Overlapping tools make the model pick at random; merge or separate them.
- One job per tool, one name per concept, and descriptions that say how tools relate.
- A small, clear set is cheaper per step and easier for the model to use well.
