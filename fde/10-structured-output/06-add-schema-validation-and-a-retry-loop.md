---
type: task
title: "Add schema validation and a retry loop"
minutes: 8
---

## Set up

```bash
mkdir -p /root/fde-lab/10-structured
```

## What to build

Write `/root/fde-lab/10-structured/robust.py` with:

- `SCHEMA` - the schema from the lesson.
- `validate(obj)` - returns a list of error messages (empty when valid).
- `extract_with_retry(ticket, ask, max_attempts=3)`:
  1. Builds the messages (the extraction system prompt from the previous task, then the ticket).
  2. Calls `ask(messages)`, which returns raw reply text.
  3. Parses it; on invalid JSON **or** schema errors, appends the bad reply as an `assistant` message and a `user` message containing the word `validation` and the errors, then tries again.
  4. Returns `(data, attempts)` on success, or `(None, attempts)` after `max_attempts` failures.
- A `__main__` block for `python robust.py TICKET_TEXT`, where `ask` calls `lab-mini` in JSON mode at temperature 0. It prints the data as JSON (or `null`), and prints `attempts: N` to **stderr**.

```bash
cd /root/fde-lab/10-structured
python robust.py "Order MER-55120 arrived with two crushed cases. We need a refund before Friday."
```

The checker imports `extract_with_retry` and drives it with fake `ask` functions, as well as running the script for real.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Wrap `json.loads` and `validate` together: `try: obj = json.loads(raw); errors = validate(obj) except json.JSONDecodeError as e: errors = [str(e)]`.
- `print(f"attempts: {n}", file=sys.stderr)`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/10-structured
cat > robust.py <<'EOF'
import json
import sys

from jsonschema import Draft202012Validator

SYSTEM = 'Extract fields from a Meridian Logistics support ticket. Reply with a JSON object with exactly these keys: "order_id" (like MER-12345, or null if none is mentioned), "issue" (one of: damaged, late, lost, address, billing, other), "urgency" (one of: low, medium, high). Example: {"order_id": "MER-10001", "issue": "late", "urgency": "medium"}'
SCHEMA = {
    "type": "object",
    "required": ["order_id", "issue", "urgency"],
    "additionalProperties": False,
    "properties": {
        "order_id": {"type": ["string", "null"], "pattern": "^MER-[0-9]{5}$"},
        "issue": {"enum": ["damaged", "late", "lost", "address", "billing", "other"]},
        "urgency": {"enum": ["low", "medium", "high"]},
    },
}


def validate(obj):
    return [e.message for e in Draft202012Validator(SCHEMA).iter_errors(obj)]


def extract_with_retry(ticket, ask, max_attempts=3):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": ticket}]
    for attempt in range(1, max_attempts + 1):
        raw = ask(messages)
        try:
            obj = json.loads(raw)
            errors = validate(obj)
        except json.JSONDecodeError as e:
            errors = [f"invalid JSON: {e}"]
        if not errors:
            return obj, attempt
        messages = messages + [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": f"Your JSON failed validation: {'; '.join(errors)}. Reply again with corrected JSON only."},
        ]
    return None, max_attempts


if __name__ == "__main__":
    from openai import OpenAI

    client = OpenAI()

    def ask(messages):
        resp = client.chat.completions.create(model="lab-mini", temperature=0, response_format={"type": "json_object"}, messages=messages)
        return resp.choices[0].message.content

    data, attempts = extract_with_retry(sys.argv[1], ask)
    print(json.dumps(data))
    print(f"attempts: {attempts}", file=sys.stderr)
EOF
python robust.py "Order MER-55120 arrived with two crushed cases. We need a refund before Friday."
```

</details>

## Check your work

```bash
D=/root/fde-lab/10-structured; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/robust.py 2>/dev/null && [ -s $D/robust.py ] && echo "✅ robust.py reads the key from the environment" || echo "❌ robust.py must not contain a key - let the SDK read it from the environment"
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
sys.path.insert(0, ".")
try:
    import robust
except Exception as e:
    robust = None
    print(f"❌ import robust failed: {e}")
if robust:
    ok(robust.validate({"order_id": "MER-12345", "issue": "late", "urgency": "low"}) == [] and len(robust.validate({"order_id": "12345", "issue": "broken", "urgency": "low", "x": 1})) >= 3, "validate() accepts a good object and lists every problem in a bad one", "validate() should return [] for a valid object and one message per problem otherwise")
    seen = []
    replies = iter(['Sure! {"order_id": "MER-12345"}', '{"order_id": "MER-12345", "issue": "broken", "urgency": "high"}', '{"order_id": "MER-12345", "issue": "damaged", "urgency": "high"}'])
    def ask(messages):
        seen.append([dict(m) for m in messages])
        return next(replies)
    data, n = robust.extract_with_retry("Order MER-12345 is damaged", ask)
    ok(data == {"order_id": "MER-12345", "issue": "damaged", "urgency": "high"} and n == 3, "bad JSON, then a schema error, then success: returns the data after 3 attempts", f"expected the valid object after 3 attempts - got {data}, {n}")
    ok(len(seen) == 3 and seen[1][-2]["role"] == "assistant" and seen[1][-1]["role"] == "user" and "validation" in seen[1][-1]["content"] and "broken" in seen[2][-1]["content"], "each retry sends back the bad reply and the validation errors", "a retry should append the bad reply (assistant) and a user message with 'validation' and the errors")
    calls = []
    def always_bad(messages):
        calls.append(1)
        return "{}"
    data, n = robust.extract_with_retry("x", always_bad, max_attempts=2)
    ok(data is None and n == 2 and len(calls) == 2, "it gives up after max_attempts and returns None", f"with max_attempts=2 and only bad replies expected (None, 2) and 2 calls - got ({data}, {n}) and {len(calls)} calls")
rc, out, err = run("robust.py", "Our pallet for order MER-70413 never arrived and the tracking stopped in Hamburg a week ago.")
try:
    d = json.loads(out)
except ValueError:
    d = "bad"
ok(rc == 0 and isinstance(d, dict) and d.get("order_id") == "MER-70413" and "attempts:" in err, "the script extracts a real ticket and reports attempts on stderr", f"python robust.py TICKET should print valid data and 'attempts: N' on stderr - got {out[:200]!r} {err[-150:]!r}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-mini" and (.client | startswith("OpenAI/Python")) and .json_mode and .temperature == 0)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-mini call" || echo "❌ the gateway has no lab-mini call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A schema defines correct output; a validator lists every problem.
- Retry with the exact errors appended - and cap the attempts.
- Inject the API call (`ask`) so the retry logic can be tested without a model.
