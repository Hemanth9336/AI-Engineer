---
type: task
title: "Build a prompt string from pieces"
minutes: 7
---

## Set up

```bash
mkdir -p /root/fde-lab/05-python
```

## What to build

Write `/root/fde-lab/05-python/prompt.py`, used as `python prompt.py CUSTOMER QUESTION [MAX_WORDS]`. It prints exactly three lines:

```text
You are a support assistant for CUSTOMER.
Customer question: QUESTION
Answer in at most MAX_WORDS words. The question is N characters long.
```

- CUSTOMER and QUESTION have surrounding spaces removed.
- MAX_WORDS is optional and defaults to `50`.
- N is the length of the cleaned question.

```bash
cd /root/fde-lab/05-python
python prompt.py "Meridian Logistics" "  Where is my parcel?  "
python prompt.py "Kestrel Bank" "Can I raise my card limit?" 30
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `max_words = sys.argv[3] if len(sys.argv) > 3 else "50"`.
- `.strip()` removes the spaces; build each line with an f-string.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/05-python
cat > prompt.py <<'EOF'
import sys

customer = sys.argv[1].strip()
question = sys.argv[2].strip()
max_words = sys.argv[3] if len(sys.argv) > 3 else "50"
print(f"You are a support assistant for {customer}.")
print(f"Customer question: {question}")
print(f"Answer in at most {max_words} words. The question is {len(question)} characters long.")
EOF
python prompt.py "Meridian Logistics" "  Where is my parcel?  "
```

</details>

## Check your work

```bash
D=/root/fde-lab/05-python; cd $D 2>/dev/null || echo "❌ create $D"
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
def want(c, q, m="50"):
    c, q = c.strip(), q.strip()
    return f"You are a support assistant for {c}.\nCustomer question: {q}\nAnswer in at most {m} words. The question is {len(q)} characters long."
ok(Path("prompt.py").exists(), "prompt.py exists", "write prompt.py")
rc, out, err = run("prompt.py", " Harbor Insurance ", "  How do I file a claim?   ")
ok(rc == 0 and out == want(" Harbor Insurance ", "  How do I file a claim?   "), "default MAX_WORDS and stripping work", f"expected:\n{want('Harbor Insurance', 'How do I file a claim?')}\ngot:\n{out} {err[-200:]}")
rc, out, err = run("prompt.py", "Kestrel Bank", "Can I raise my limit?", "25")
ok(rc == 0 and out == want("Kestrel Bank", "Can I raise my limit?", "25"), "an explicit MAX_WORDS is used", f"with MAX_WORDS 25 expected:\n{want('Kestrel Bank', 'Can I raise my limit?', '25')}\ngot:\n{out} {err[-200:]}")
PYEOF
```

## What you learned

- f-strings build prompts from pieces: `f"... {value} ..."`.
- `sys.argv` holds command-line arguments as strings.
- `.strip()` cleans the messy input customers and files always have.
