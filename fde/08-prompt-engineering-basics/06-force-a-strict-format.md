---
type: task
title: "Force a strict format"
minutes: 8
---

## Set up

```bash
mkdir -p /root/fde-lab/08-prompting
```

## What to build

Meridian's routing system accepts one line per ticket: `PRIORITY|TEAM`, where PRIORITY is `P1`, `P2` or `P3` and TEAM is `warehouse`, `billing` or `delivery`.

Write `/root/fde-lab/08-prompting/triage.py`, used as `python triage.py TICKET_TEXT`:

1. Call `lab-fast` at `temperature=0` with a system prompt that defines the format, the priorities (P1: safety risk or a business stopped; P2: money or a missed delivery; P3: everything else) and the teams.
2. Pass `stop=["\n"]` so the reply is at most one line.
3. Validate it with the regex `^(P1|P2|P3)\|(warehouse|billing|delivery)$`. Print the line and exit 0 if it matches; otherwise print `INVALID: <reply>` and exit 2.

```bash
cd /root/fde-lab/08-prompting
python triage.py "A forklift in your Leeds warehouse is leaking fuel next to our goods."
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `re.fullmatch(PATTERN, reply.strip())`.
- `sys.exit(2)` after printing the invalid line.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/08-prompting
cat > triage.py <<'EOF'
import re
import sys

from openai import OpenAI

SYSTEM = """You route Meridian Logistics support tickets. Reply with exactly one line in the form PRIORITY|TEAM and nothing else.
PRIORITY is one of: P1 (safety risk or a customer's business is stopped), P2 (money or a missed delivery), P3 (everything else).
TEAM is one of: warehouse (storage, handling, damage at a site), billing (invoices, charges, refunds), delivery (drivers, tracking, addresses, late parcels).
Example: P2|billing"""
FORMAT = r"^(P1|P2|P3)\|(warehouse|billing|delivery)$"

resp = OpenAI().chat.completions.create(
    model="lab-fast",
    temperature=0,
    stop=["\n"],
    messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": sys.argv[1]}],
)
reply = (resp.choices[0].message.content or "").strip()
if re.fullmatch(FORMAT, reply):
    print(reply)
else:
    print(f"INVALID: {reply}")
    sys.exit(2)
EOF
python triage.py "A forklift in your Leeds warehouse is leaking fuel next to our goods."
```

</details>

## Check your work

```bash
D=/root/fde-lab/08-prompting; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/triage.py 2>/dev/null && [ -s $D/triage.py ] && echo "✅ triage.py reads the key from the environment" || echo "❌ triage.py must not contain a key - let the SDK read it from the environment"
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
cases = [("You billed us 4,200 EUR for a shipment we cancelled last week.", "P2|billing"),
         ("Can your drivers use the rear entrance on Elm Street from now on?", "P3|delivery")]
for text, want in cases:
    rc, out, err = run("triage.py", text)
    ok(rc == 0 and out == want, f"'{text[:40]}...' -> {want}", f"'{text[:40]}...' should print {want} - got exit {rc}, {out!r} {err[-150:]}")
src = Path("triage.py").read_text()
ok("fullmatch" in src or "^(" in src, "triage.py validates the reply with an anchored regex", "validate the reply with re.fullmatch or an anchored ^...$ pattern")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and .temperature == 0 and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged lab-fast calls at temperature 0 with a system prompt" || echo "❌ no lab-fast call at temperature 0 with a system prompt"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Downstream code needs exact formats - describe, demonstrate, then constrain.
- `stop` sequences hard-limit the output shape.
- Validate every reply with an anchored check and handle the failure path.
