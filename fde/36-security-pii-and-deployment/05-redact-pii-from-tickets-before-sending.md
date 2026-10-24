---
type: task
title: "Redact PII from tickets before sending"
minutes: 9
---

## Set up

`tickets.jsonl` holds three Kestrel Foods tickets containing names, emails, phone numbers, an IBAN and a card number.

```bash
mkdir -p /root/fde-lab/36-pii
cd /root/fde-lab/36-pii
cat > tickets.jsonl <<'EOF'
{"id": "K-301", "body": "Hi, this is Jan de Vries, jan.devries@harbor-foods.nl, phone +31 20 794 5521. Pallet MER-70413 arrived damaged on 2026-03-11, please refund to NL91 ABNA 0417 1643 00."}
{"id": "K-302", "body": "Card 4111 1111 1111 1111 was charged twice for order MER-55120. Call me on 06-12345678."}
{"id": "K-303", "body": "Where is order MER-60311? It was due on 2026-03-14 and tracking hasn't moved."}
EOF
rm -f outbound.jsonl
```

## What to build

1. Write `/root/fde-lab/36-pii/redact.py` with `redact(text)` returning `(clean_text, counts)` - for example `("Mail [EMAIL]", {"EMAIL": 1})` - applying these patterns **in this order**:

   | Label | Pattern |
   |---|---|
   | `EMAIL` | `[\w.+-]+@[\w-]+(?:\.[\w-]+)+` |
   | `IBAN` | `\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,3})?\b` |
   | `CARD` | `\b(?:\d[ -]?){12,15}\d\b` |
   | `PHONE` | `(?<!\w)\+?\d{1,3}[ -]?\(?\d{2,4}\)?[ -]?\d{3,4}[ -]?\d{3,4}(?!\w)` |

   Also add `find_pii(text)`, returning the labels `redact` would replace (for example `["EMAIL", "CARD"]`) - running the patterns in order means a card number isn't also reported as a phone number.
2. Write `summarise.py`, used as `python summarise.py TICKETS`: for each ticket, redact the body, build the prompt `Summarise this support ticket in one sentence:` + a blank line + the clean body, **append `{"ticket": id, "prompt": prompt}` to `outbound.jsonl`** before sending, call `lab-fast`, and print `<id> redacted=<counts> summary=<reply>`.

```bash
cd /root/fde-lab/36-pii
python summarise.py tickets.jsonl
cat outbound.jsonl
```

Order ids (`MER-70413`) and dates must survive redaction.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `pattern.subn(replacement, text)` returns the new text and the number of replacements.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/36-pii
cat > redact.py <<'EOF'
import re

PATTERNS = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,3})?\b")),
    ("CARD", re.compile(r"\b(?:\d[ -]?){12,15}\d\b")),
    ("PHONE", re.compile(r"(?<!\w)\+?\d{1,3}[ -]?\(?\d{2,4}\)?[ -]?\d{3,4}[ -]?\d{3,4}(?!\w)")),
]


def redact(text):
    counts = {}
    for label, pattern in PATTERNS:
        text, n = pattern.subn(f"[{label}]", text)
        if n:
            counts[label] = n
    return text, counts


def find_pii(text):
    return list(redact(text)[1])

EOF
cat > summarise.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

from redact import redact

client = OpenAI()
OUTBOUND = Path(__file__).with_name("outbound.jsonl")

for line in open(sys.argv[1]):
    if not line.strip():
        continue
    ticket = json.loads(line)
    clean, counts = redact(ticket["body"])
    prompt = f"Summarise this support ticket in one sentence:\n\n{clean}"
    with open(OUTBOUND, "a") as f:
        f.write(json.dumps({"ticket": ticket["id"], "prompt": prompt}) + "\n")
    reply = client.chat.completions.create(model="lab-fast", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
    print(f"{ticket['id']} redacted={counts} summary={reply}")

EOF
python summarise.py tickets.jsonl
cat outbound.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/36-pii; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/summarise.py 2>/dev/null && [ -s $D/summarise.py ] && echo "✅ summarise.py reads the key from the environment" || echo "❌ summarise.py must not contain a key - let the SDK read it from the environment"
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
    from redact import redact
    cases = [
        ("Mail me at a.b+c@kestrel.co.uk today", "Mail me at [EMAIL] today", {"EMAIL": 1}),
        ("IBAN DE89 3704 0044 0532 0130 00 please", "IBAN [IBAN] please", {"IBAN": 1}),
        ("card 5500-0000-0000-0004 and +44 20 7946 0958", "card [CARD] and [PHONE]", {"CARD": 1, "PHONE": 1}),
        ("Order MER-81234 on 2026-03-14 at 10:30", "Order MER-81234 on 2026-03-14 at 10:30", {}),
    ]
    bad = [(t, redact(t)) for t, want, c in cases if redact(t) != (want, c)]
    ok(not bad, "redact() handles four unseen texts, leaving order ids and dates alone", f"wrong results (input, got): {bad}")
except Exception as e:
    print(f"❌ import redact failed: {e}")
Path("outbound.jsonl").unlink(missing_ok=True)
b = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("summarise.py", "tickets.jsonl")
rows = [json.loads(l) for l in open("outbound.jsonl")] if Path("outbound.jsonl").exists() else []
gw = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][b:]
text = " ".join(r.get("prompt", "") for r in rows)
ok(rc == 0 and [r.get("ticket") for r in rows] == ["K-301", "K-302", "K-303"] and len([g for g in gw if g.get("api") == "chat.completions"]) == 3, "three prompts were logged to outbound.jsonl and sent", f"expected three outbound lines and three chat calls - got {[r.get('ticket') for r in rows]} {err[-200:]}")
leaks = [s for s in ("jan.devries@", "5521", "NL91", "4111", "12345678") if s in text]
ok(rows and not leaks and "MER-70413" in text and "2026-03-11" in text and "[IBAN]" in text, "outbound prompts contain no PII but keep order ids and dates", f"leaked: {leaks}" if leaks else "the order ids and dates must survive redaction")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Redact before text leaves the customer: the model can't leak what it never saw.
- Apply the most specific patterns first, and test that needed ids survive.
- Log outbound prompts after redaction, never before.
