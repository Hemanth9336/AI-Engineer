---
type: task
title: "Catch policy-violating outputs"
minutes: 9
---

## Set up

`policy.json` is Meridian's output policy. `replies.jsonl` holds five bot replies to screen.

```bash
mkdir -p /root/fde-lab/31-guardrails
cd /root/fde-lab/31-guardrails
cat > policy.json <<'EOF'
{
  "competitors": [
    "DHL",
    "UPS",
    "FedEx",
    "PostNL"
  ],
  "banned_phrases": [
    "guarantee",
    "we promise",
    "legal advice"
  ],
  "company_email_domain": "meridian.example"
}
EOF
cat > replies.jsonl <<'EOF'
{"id": "r1", "reply": "Your parcel is at the Leeds hub and should arrive tomorrow."}
{"id": "r2", "reply": "We guarantee delivery by Friday - faster than DHL!"}
{"id": "r3", "reply": "Sorry about the damage. We will refund you 120 EUR today."}
{"id": "r4", "reply": "Please send the photos to claims@meridian-claims.net and we'll review them."}
{"id": "r5", "reply": "Email photos to claims@meridian.example within 7 days of delivery."}
EOF
```

## What to build

Write `/root/fde-lab/31-guardrails/outfilter.py` with `violations(text)`, returning a list of strings (empty = ok), using `policy.json`:

- `competitor: <name>` - a competitor named as a whole word, any case.
- `banned phrase: <phrase>` - a banned phrase anywhere, any case.
- `amount promise` (at most once) - a sentence (split on `.`, `!`, `?`) containing a word starting with `refund`, `compensat` or `reimburs` **and** an amount like `120 EUR`, `45.50 euros` or `€80`.
- `external email: <address>` - an email address not at `company_email_domain`.

Also add `safe_reply(text)`, which returns `I can't confirm that here - a Meridian agent will follow up by email.` if there are violations, or the text unchanged. `python outfilter.py REPLIES` prints `<id> <violations or ok>` per line.

```bash
cd /root/fde-lab/31-guardrails
python outfilter.py replies.jsonl
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `\\bDHL\\b` with `re.I` matches 'dhl' but not 'adhland'.
- An email regex like `[\\w.+-]+@[\\w-]+(?:\\.[\\w-]+)+` is enough here.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/31-guardrails
cat > outfilter.py <<'EOF'
import json
import re
import sys
from pathlib import Path

POLICY = json.loads(Path(__file__).with_name("policy.json").read_text())
FALLBACK = "I can't confirm that here - a Meridian agent will follow up by email."
MONEY_WORD = re.compile(r"\b(refund|compensat|reimburs)\w*", re.I)
AMOUNT = re.compile(r"\d+(?:[.,]\d+)?\s?(?:EUR|euros?)\b|€\s?\d+", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def violations(text):
    found = []
    for name in POLICY["competitors"]:
        if re.search(rf"\b{re.escape(name)}\b", text, re.I):
            found.append(f"competitor: {name}")
    for phrase in POLICY["banned_phrases"]:
        if phrase.lower() in text.lower():
            found.append(f"banned phrase: {phrase}")
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if MONEY_WORD.search(sentence) and AMOUNT.search(sentence):
            found.append("amount promise")
            break
    for email in EMAIL.findall(text):
        if not email.lower().endswith("@" + POLICY["company_email_domain"]):
            found.append(f"external email: {email}")
    return found


def safe_reply(text):
    return FALLBACK if violations(text) else text


if __name__ == "__main__":
    for line in open(sys.argv[1]):
        if line.strip():
            r = json.loads(line)
            print(r["id"], violations(r["reply"]) or "ok")

EOF
python outfilter.py replies.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/31-guardrails; cd $D 2>/dev/null || echo "❌ create $D"
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
    import outfilter as of
except Exception as e:
    of = None
    print(f"❌ import outfilter failed: {e}")
if of:
    cases = [
        ("Your pallet will arrive on Thursday.", set()),
        ("We'll beat any ups price - that's a GUARANTEE.", {"competitor: UPS", "banned phrase: guarantee"}),
        ("You'll be compensated with €80. Thanks for waiting.", {"amount promise"}),
        ("A refund is possible. The fee is 6 EUR.", set()),
        ("We reimburse 45.50 euros for the delay.", {"amount promise"}),
        ("Write to help@meridian.example or to ops@fedex-partners.com.", {"competitor: FedEx", "external email: ops@fedex-partners.com"}),
        ("Our postnl partner handles Belgium.", {"competitor: PostNL"}),
    ]
    bad = []
    for text, want in cases:
        try:
            got = set(of.violations(text))
        except Exception as e:
            got = {f"error {e}"}
        if got != want:
            bad.append((text, sorted(want), sorted(got)))
    ok(not bad, "violations() is right on seven unseen replies", f"wrong results (text, expected, got): {bad}")
    ok(of.safe_reply("We guarantee it.") == "I can't confirm that here - a Meridian agent will follow up by email." and of.safe_reply("It arrives Friday.") == "It arrives Friday.", "safe_reply swaps violating replies for the fallback", "safe_reply should return the fallback on a violation and the text unchanged otherwise")
rc, out, err = run("outfilter.py", "replies.jsonl")
ok(rc == 0 and out.splitlines()[:1] == ["r1 ok"] and len(out.splitlines()) == 5 and "external email: claims@meridian-claims.net" in out, "outfilter.py screened replies.jsonl", f"expected five lines starting 'r1 ok' and flagging the external email - got {out[-300:]!r} {err[-200:]}")
PYEOF
```

## What you learned

- Rules that matter are enforced in code, not only in the prompt.
- Output filters catch commitments, banned phrases, competitors and foreign contact details.
- Replace violations with a safe fallback, log them, and keep the rules in a policy file.
