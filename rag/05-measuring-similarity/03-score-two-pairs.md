---
type: task
title: "Score two pairs"
minutes: 14
---

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/05-similarity /root/answers
```

## What to build

Write `/root/rag-lab/05-similarity/similarity.py`:

1. A function `cosine(a, b)` in plain Python (no numpy), using the full formula.
2. When run as `python similarity.py TEXT1 TEXT2`, it embeds both texts with `lab-embed` and prints their cosine similarity to 4 decimal places.
3. When run with **no arguments**, it scores these two pairs:
   - pair a: `How do I reset my password?` vs `I forgot my login password`
   - pair b: `How do I reset my password?` vs `The office is closed on Friday`

   and writes `/root/answers/05-scores.txt` in exactly this format:

   ```text
   pair_a=0.xxxx
   pair_b=0.xxxx
   closer=a
   ```

   where `closer` is whichever pair scored higher.
4. Importing it (`from similarity import cosine`) must not make any model call.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Embed all three texts in one call, then compute two scores.
- Use `f"{score:.4f}"` for 4 decimal places.
- `closer = "a" if pair_a > pair_b else "b"`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/05-similarity
cat > similarity.py <<'EOF'
import math
import sys


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def embed(texts):
    from openai import OpenAI

    return [d.embedding for d in OpenAI().embeddings.create(model="lab-embed", input=texts).data]


if __name__ == "__main__":
    if len(sys.argv) == 3:
        a, b = embed(sys.argv[1:3])
        print(f"{cosine(a, b):.4f}")
    else:
        q, same, other = embed(["How do I reset my password?", "I forgot my login password", "The office is closed on Friday"])
        pair_a, pair_b = cosine(q, same), cosine(q, other)
        closer = "a" if pair_a > pair_b else "b"
        with open("/root/answers/05-scores.txt", "w") as f:
            f.write(f"pair_a={pair_a:.4f}\npair_b={pair_b:.4f}\ncloser={closer}\n")
        print(open("/root/answers/05-scores.txt").read())
EOF
python similarity.py
python similarity.py "The disk is full" "We ran out of storage"
```

</details>

## Check your work

```bash
D=/root/rag-lab/05-similarity; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/similarity.py 2>/dev/null && [ -s $D/similarity.py ] && echo "✅ similarity.py reads the key from the environment" || echo "❌ similarity.py must not contain a key - let the SDK read it from the environment"
! grep -q 'numpy' similarity.py && echo "✅ cosine() is plain Python" || echo "❌ write cosine() without numpy"
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
import importlib
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
m = importlib.import_module("similarity")
after = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
ok(after == before, "importing similarity makes no model call", "importing similarity.py made a model call - put the demo behind if __name__ == '__main__':")
c = m.cosine
ok(abs(c([1, 0], [0, 1])) < 1e-9 and abs(c([1, 2], [2, 4]) - 1) < 1e-9 and abs(c([1, 0], [-1, 0]) + 1) < 1e-9 and abs(c([3, 4], [4, 3]) - 0.96) < 1e-9,
   "cosine() is correct on test vectors (including unnormalised ones)", "cosine() gives wrong results - check the dot product and both lengths")
lines = dict(l.split("=", 1) for l in Path("/root/answers/05-scores.txt").read_text().split() if "=" in l) if Path("/root/answers/05-scores.txt").exists() else {}
q, s, o = E(["How do I reset my password?", "I forgot my login password", "The office is closed on Friday"])
try:
    pa, pb = float(lines.get("pair_a")), float(lines.get("pair_b"))
except (TypeError, ValueError):
    pa = pb = None
ok(pa is not None and abs(pa - cos(q, s)) < 0.001 and abs(pb - cos(q, o)) < 0.001, "05-scores.txt has the right pair_a and pair_b", "/root/answers/05-scores.txt needs pair_a=... and pair_b=... matching the real scores")
ok(lines.get("closer") == "a", "closer=a", "05-scores.txt needs closer=a")
x, y = "My invoice shows the wrong amount", "I was billed incorrectly"
rc, out, err = run("similarity.py", x, y)
want = cos(*E([x, y]))
try:
    got = float(out.split()[-1])
except Exception:
    got = None
ok(rc == 0 and got is not None and abs(got - want) < 0.001, "python similarity.py TEXT1 TEXT2 prints the right score for a new pair", f"python similarity.py TEXT1 TEXT2 should print {want:.4f} for a new pair - got {out[-80:]!r}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Cosine similarity = dot product divided by both lengths; only direction counts.
- 1 means same direction, 0 unrelated; with normalised vectors it equals the dot product.
- Trust the ranking more than any absolute score.
