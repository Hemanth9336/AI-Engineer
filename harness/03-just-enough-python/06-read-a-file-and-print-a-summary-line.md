---
type: task
title: "Read a file and print a summary line"
minutes: 8
---

## Set up

```bash
mkdir -p /root/harness-lab/03-python
cd /root/harness-lab/03-python
cat > tickets.txt <<'EOF'
T-101 | high | Parcel arrived damaged and the customer wants a refund today
T-102 | low  | Change delivery address

T-103 | medium | Driver left the parcel at the wrong door
T-104 | high | Missing pallet from the Rotterdam shipment
EOF
```

## What to build

`tickets.txt` is a messy export: one ticket per line as `ID | priority | text`, with stray spaces and a blank line.

Write `/root/harness-lab/03-python/summary.py` with a function `summarize(path)` that **returns** one line:

```text
4 tickets, 2 high priority, longest: T-101
```

- skip blank lines and strip spaces around each field;
- "longest" is the ticket whose text has the most characters (first one wins on a tie).

When run as a script (`python summary.py FILE`) it prints `summarize(FILE)`. Use `if __name__ == "__main__":` so the checker can import the function.

```bash
cd /root/harness-lab/03-python
python summary.py tickets.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `parts = [p.strip() for p in line.split("|")]`.
- `max(tickets, key=lambda t: len(t[2]))` returns the first longest.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/03-python
cat > summary.py <<'EOF'
import sys


def summarize(path):
    tickets = [[p.strip() for p in line.split("|")] for line in open(path) if line.strip()]
    high = sum(1 for t in tickets if t[1] == "high")
    longest = max(tickets, key=lambda t: len(t[2]))
    return f"{len(tickets)} tickets, {high} high priority, longest: {longest[0]}"


if __name__ == "__main__":
    print(summarize(sys.argv[1]))
EOF
python summary.py tickets.txt
```

</details>

## Check your work

```bash
D=/root/harness-lab/03-python; cd $D 2>/dev/null || echo "❌ create $D"
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
rc, out, err = run("summary.py", "tickets.txt")
ok(rc == 0 and out == "4 tickets, 2 high priority, longest: T-101", "tickets.txt summarizes correctly", f"expected '4 tickets, 2 high priority, longest: T-101' - got {out!r} {err[-200:]}")
Path("/tmp/t2.txt").write_text("A-1 |low| short\r\n\r\n  A-2 | high |  a much longer ticket text here \r\nA-3 | high | also a much longer ticket txt  \r\n\n")
sys.path.insert(0, ".")
try:
    from summary import summarize
    got = summarize("/tmp/t2.txt")
except Exception as e:
    got = f"import failed: {e}"
ok(got == "3 tickets, 2 high priority, longest: A-2", "summarize() can be imported and handles Windows line endings and blank lines", f"from summary import summarize; summarize(file) should return '3 tickets, 2 high priority, longest: A-2' - got {got!r}")
PYEOF
```

## What you learned

- Functions with a `__main__` guard can be both run and imported.
- Real exports need `.strip()` and blank-line skipping.
- `max(..., key=...)` picks the best item by any measure.
