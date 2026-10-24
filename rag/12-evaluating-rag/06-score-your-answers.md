---
type: task
title: "Score your answers"
minutes: 10
---

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/12-eval /root/answers
cd /root/rag-lab/12-eval
[ -f rag_lib.py ] || { echo "rag_lib.py is missing - run the previous task's Set up first"; false; }
```

## What to build

Write `/root/rag-lab/12-eval/eval_answers.py`, used as `python eval_answers.py EVAL_FILE OUT_FILE`:

1. For every item, call `rag_lib.answer(question)`.
2. Mark it **correct** if `expect` is set and the answer contains it (ignoring case), or if `expect` is null and the answer is exactly `I don't know based on the documents.`.
3. Write OUT_FILE as JSON:

   ```json
   { "total": 10, "correct": 10, "accuracy": 1.0,
     "results": [ { "question": "...", "expect": "...", "answer": "...", "correct": true } ] }
   ```

   with `accuracy` rounded to 3 decimals and the results in eval-file order.

```bash
python eval_answers.py eval.json /root/answers/12-answers.json
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `from rag_lib import REFUSAL, answer`.
- `item["expect"].lower() in got.lower()`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/12-eval
cat > eval_answers.py <<'EOF'
import json
import sys

from rag_lib import REFUSAL, answer

if len(sys.argv) != 3:
    print("usage: eval_answers.py EVAL_FILE OUT_FILE", file=sys.stderr)
    sys.exit(2)
results = []
for item in json.load(open(sys.argv[1])):
    got = answer(item["question"])["answer"]
    correct = item["expect"].lower() in got.lower() if item["expect"] else got == REFUSAL
    results.append({"question": item["question"], "expect": item["expect"], "answer": got, "correct": correct})
correct = sum(r["correct"] for r in results)
out = {"total": len(results), "correct": correct, "accuracy": round(correct / len(results), 3), "results": results}
json.dump(out, open(sys.argv[2], "w"), indent=2)
print(f"accuracy: {correct}/{len(results)}")
EOF
python eval_answers.py eval.json /root/answers/12-answers.json
python -c "import json; d = json.load(open('/root/answers/12-answers.json')); print(d['correct'], d['total'])"
```

</details>

## Check your work

```bash
D=/root/rag-lab/12-eval; cd $D 2>/dev/null || echo "❌ create $D"
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
REFUSAL = "I don't know based on the documents."
ev = load("eval.json") or []
r = load("/root/answers/12-answers.json") or {}
res = r.get("results") or []
ok(r.get("total") == 10 and len(res) == 10 and [x.get("question") for x in res] == [e["question"] for e in ev], "12-answers.json has all 10 results in order", "/root/answers/12-answers.json needs total 10 and one result per eval item, in order")
def right(e, a):
    return e["expect"].lower() in a.lower() if e["expect"] else a == REFUSAL
ok(res and all(x.get("correct") == right(e, x.get("answer", "")) for x, e in zip(res, ev)), "every 'correct' flag follows the two rules", "a 'correct' flag doesn't match its answer - contains expect (any case), or exactly the refusal when expect is null")
ok(r.get("correct") == sum(bool(x.get("correct")) for x in res) and r.get("accuracy") == round(r.get("correct", 0) / max(len(res), 1), 3), "correct and accuracy add up", "correct should count the true flags and accuracy = correct / total rounded to 3")
ok(r.get("correct") == 10, "10 of 10 answers are correct", f"expected 10 of 10 correct - got {r.get('correct')}; look at the wrong ones")
probe = [
    {"question": "When are production deploys allowed?", "source": "deploys.md", "expect": "FRIDAYS"},
    {"question": "How long are database backups kept?", "source": "backups.md", "expect": "35 DAYS"},
    {"question": "Which band is playing at the summer party?", "source": None, "expect": None},
    {"question": "How often must secrets be rotated?", "source": "security.md", "expect": None},
]
Path("/tmp/probe-eval.json").write_text(json.dumps(probe))
rc, out, err = run("eval_answers.py", "/tmp/probe-eval.json", "/tmp/probe-answers.json")
p = load("/tmp/probe-answers.json") or {}
ok(rc == 0 and [x.get("correct") for x in p.get("results", [])] == [False, True, True, False] and p.get("accuracy") == 0.5, "on a new eval file: wrong fact, case-insensitive match, refusal and a missed refusal are all scored right", f"on the checker's eval file expected flags [False, True, True, False] and accuracy 0.5 - got {[x.get('correct') for x in p.get('results', [])]} {err[-150:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Answer accuracy: contains the expected fact, or exactly refuses when nothing should be found.
- Read it next to retrieval hit rate to know which half to fix.
- Keep the eval set in git and run it on every change.
