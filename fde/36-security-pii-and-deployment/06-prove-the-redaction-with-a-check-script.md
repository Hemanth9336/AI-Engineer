---
type: task
title: "Prove the redaction with a check script"
minutes: 9
---

## Set up

If you skipped the previous task, Set up writes `redact.py` and `summarise.py` for you.

```bash
mkdir -p /root/fde-lab/36-pii
cd /root/fde-lab/36-pii
cat > tickets.jsonl <<'EOF'
{"id": "K-301", "body": "Hi, this is Jan de Vries, jan.devries@harbor-foods.nl, phone +31 20 794 5521. Pallet MER-70413 arrived damaged on 2026-03-11, please refund to NL91 ABNA 0417 1643 00."}
{"id": "K-302", "body": "Card 4111 1111 1111 1111 was charged twice for order MER-55120. Call me on 06-12345678."}
{"id": "K-303", "body": "Where is order MER-60311? It was due on 2026-03-14 and tracking hasn't moved."}
EOF
[ -f redact.py ] || cat > redact.py <<'EOF'
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
[ -f summarise.py ] || cat > summarise.py <<'EOF'
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
```

## What to build

"We redact PII" is a claim. A check that scans what was actually sent is evidence.

Write `/root/fde-lab/36-pii/check_redaction.py`, used as `python check_redaction.py OUTBOUND`:

- For every line, run `find_pii` on the prompt.
- Print `LEAK <ticket> <label>` for each hit, then `N leaks in M prompts`.
- Exit `1` if there are any leaks, else `0` - so it can run in CI or a nightly job.

```bash
cd /root/fde-lab/36-pii
rm -f outbound.jsonl
python summarise.py tickets.jsonl > /dev/null
python check_redaction.py outbound.jsonl; echo "exit $?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Import `find_pii` from `redact.py` so the check and the redaction share the same patterns.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/36-pii
cat > check_redaction.py <<'EOF'
import json
import sys

from redact import find_pii

rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
leaks = [(r["ticket"], label) for r in rows for label in find_pii(r["prompt"])]
for ticket, label in leaks:
    print(f"LEAK {ticket} {label}")
print(f"{len(leaks)} leaks in {len(rows)} prompts")
sys.exit(1 if leaks else 0)

EOF
rm -f outbound.jsonl
python summarise.py tickets.jsonl > /dev/null
python check_redaction.py outbound.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/36-pii; cd $D 2>/dev/null || echo "❌ create $D"
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
Path("outbound.jsonl").unlink(missing_ok=True)
run("summarise.py", "tickets.jsonl")
rc, out, err = run("check_redaction.py", "outbound.jsonl")
ok(rc == 0 and out.splitlines()[-1:] == ["0 leaks in 3 prompts"], "the real outbound log passes: 0 leaks in 3 prompts", f"expected exit 0 and '0 leaks in 3 prompts' - got exit {rc}, {out[-200:]!r} {err[-200:]}")
Path("/tmp/out36.jsonl").write_text(Path("outbound.jsonl").read_text() + json.dumps({"ticket": "K-999", "prompt": "Customer ana@example.com paid with 4000 0000 0000 0002"}) + "\n")
rc, out, err = run("check_redaction.py", "/tmp/out36.jsonl")
ok(rc == 1 and "LEAK K-999 EMAIL" in out and "LEAK K-999 CARD" in out and out.splitlines()[-1:] == ["2 leaks in 4 prompts"], "an injected leak is caught, named and fails the check", f"expected exit 1, LEAK K-999 EMAIL and CARD, and '2 leaks in 4 prompts' - got exit {rc}, {out[-300:]!r}")
PYEOF
```

## What you learned

- Prove redaction by scanning what was actually sent.
- Share one set of patterns between the redactor and the checker.
- A non-zero exit lets CI or a nightly job enforce it.
