---
type: task
title: "Capture thumbs-down and add an escalation rule"
minutes: 9
---

## Set up

```bash
mkdir -p /root/fde-lab/40-pilot
cd /root/fde-lab/40-pilot
rm -f feedback.jsonl
```

## What to build

Write `/root/fde-lab/40-pilot/feedback.py`:

1. `record(request_id, rating, comment="")` - `rating` must be `up` or `down` (else raise `ValueError`). Append `{"ts", "request_id", "rating", "comment"}` to `feedback.jsonl` next to the script, and return the entry.
2. `should_escalate(question, answer, session_ratings=())` returns `(True, reason)` or `(False, None)`. Check in this order, using the question's lower-case words (`re.findall(r"[a-z']+", ...)`):
   - the answer is exactly `I don't know based on the provided sources.` -> `refusal`
   - the question contains `human`, `agent`, `person` or `someone` -> `asked for a human`
   - the question contains `furious`, `unacceptable`, `complaint`, `lawyer` or `scam` -> `angry customer`
   - `session_ratings` has two or more `down` -> `repeated thumbs-down`
3. `python feedback.py FEEDBACK_FILE` prints `thumbs down: N/M (P%)`, then `- <request_id>: <comment>` for each thumbs-down with a comment.

```bash
cd /root/fde-lab/40-pilot
python -c "import feedback as f; f.record('r-1', 'up'); f.record('r-2', 'down', 'cited the old label rules'); print(f.should_escalate('Can I talk to a person?', 'Sure.'))"
python feedback.py feedback.jsonl
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Return as soon as one rule matches - the order sets the reason.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/40-pilot
cat > feedback.py <<'EOF'
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).with_name("feedback.jsonl")
REFUSE = "I don't know based on the provided sources."
ANGRY = {"furious", "unacceptable", "complaint", "lawyer", "scam"}


def record(request_id, rating, comment=""):
    if rating not in ("up", "down"):
        raise ValueError(f"rating must be 'up' or 'down', got {rating!r}")
    entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "request_id": request_id, "rating": rating, "comment": comment}
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def should_escalate(question, answer, session_ratings=()):
    words = set(re.findall(r"[a-z']+", question.lower()))
    if answer.strip() == REFUSE:
        return True, "refusal"
    if words & {"human", "agent", "person", "someone"}:
        return True, "asked for a human"
    if words & ANGRY:
        return True, "angry customer"
    if list(session_ratings).count("down") >= 2:
        return True, "repeated thumbs-down"
    return False, None


if __name__ == "__main__":
    rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    down = [r for r in rows if r["rating"] == "down"]
    print(f"thumbs down: {len(down)}/{len(rows)} ({round(100 * len(down) / len(rows)) if rows else 0}%)")
    for r in down:
        if r.get("comment"):
            print(f"- {r['request_id']}: {r['comment']}")

EOF
python -c "import feedback as f; f.record('r-1', 'up'); f.record('r-2', 'down', 'cited the old label rules'); print(f.should_escalate('Can I talk to a person?', 'Sure.'))"
python feedback.py feedback.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/40-pilot; cd $D 2>/dev/null || echo "❌ create $D"
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
REFUSE = "I don't know based on the provided sources."
sys.path.insert(0, ".")
try:
    import feedback as f
except Exception as e:
    f = None
    print(f"❌ import feedback failed: {e}")
if f:
    cases = [
        (("Where is my pallet?", REFUSE, ()), (True, "refusal")),
        (("I want a human now, this is unacceptable", "Here is the status.", ()), (True, "asked for a human")),
        (("This is a SCAM. Where is my refund?", "It was refunded on Monday.", ("up",)), (True, "angry customer")),
        (("And the label rules?", "Labels go on two sides.", ("down", "up", "down")), (True, "repeated thumbs-down")),
        (("Thanks, and the slot times?", "Chilled goods: 04:00 to 09:00.", ("down",)), (False, None)),
        (("Is there someone who can check my booking?", "Bookings are in the portal.", ("down", "down")), (True, "asked for a human")),
        (("Anyone around on Sunday?", "No, Monday to Saturday.", ()), (False, None)),
    ]
    bad = []
    for args, want in cases:
        try:
            got = tuple(f.should_escalate(*args))
        except Exception as e:
            got = ("error", str(e))
        if got != want:
            bad.append((args[0], want, got))
    ok(not bad, "should_escalate gets seven unseen cases right, in the right order", f"wrong (question, expected, got): {bad}")
    try:
        f.record("r-x", "meh")
        raised = False
    except ValueError:
        raised = True
    ok(raised, "an invalid rating raises ValueError", "record() must raise ValueError unless rating is 'up' or 'down'")
    Path("feedback.jsonl").unlink(missing_ok=True)
    for rid, rating, c in [("q1", "up", ""), ("q2", "down", "wrong slot times"), ("q3", "down", ""), ("q4", "up", "")]:
        f.record(rid, rating, c)
    rows = [json.loads(l) for l in open("feedback.jsonl")]
    ok(len(rows) == 4 and {"ts", "request_id", "rating", "comment"} <= set(rows[0]) and rows[1]["comment"] == "wrong slot times", "record() appends complete lines to feedback.jsonl", f"expected four lines with ts, request_id, rating and comment - got {rows[:2]}")
rc, out, err = run("feedback.py", "feedback.jsonl")
ok(rc == 0 and out.splitlines() == ["thumbs down: 2/4 (50%)", "- q2: wrong slot times"], "the report counts thumbs-down and lists the comments", f"expected 'thumbs down: 2/4 (50%)' and '- q2: wrong slot times' - got {out!r} {err[-200:]}")
PYEOF
```

## What you learned

- Capture cheap feedback signals and link them to the request id.
- Escalate on refusals, requests for a person, anger and repeated thumbs-down.
- Track edit and escalation rates - they should fall as fixes land.
