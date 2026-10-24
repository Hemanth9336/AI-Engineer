---
type: task
title: "Catch the judge grading wrong and fix the rubric"
minutes: 10
---

## Set up

`labels.jsonl` holds four answers a Meridian support lead has labelled `pass` or `fail`. Set up replaces `rubric.txt` with a vague one a colleague wrote, and writes `judge.py` if you don't have it.

```bash
mkdir -p /root/fde-lab/27-judge
cd /root/fde-lab/27-judge
cat > labels.jsonl <<'EOF'
{"id": "h1", "question": "How long do I have to report damage?", "expected": "Within 7 days of delivery, with photos.", "answer": "Great question! We're always happy to help. You can report damage within 14 days of delivery - just send us some photos and we'll sort it out quickly.", "human": "fail"}
{"id": "h2", "question": "What does an address change cost after dispatch?", "expected": "6 EUR and one extra working day.", "answer": "6 EUR, plus one working day.", "human": "pass"}
{"id": "h3", "question": "When is support open?", "expected": "8:00 to 18:00 CET, Monday to Friday.", "answer": "Support is open 8:00 to 18:00 CET, Monday to Friday.", "human": "pass"}
{"id": "h4", "question": "How heavy can a standard pallet be?", "expected": "Up to 800 kg and 1.8 m high.", "answer": "Pallets can weigh up to 1,000 kg. Thanks for choosing Meridian, have a lovely day!", "human": "fail"}
EOF
cat > rubric.txt <<'EOF'
Grade whether the answer is helpful, polite and correct.
EOF
[ -f judge.py ] || cat > judge.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

client = OpenAI()
HERE = Path(__file__).parent
SYSTEM = "You are a strict grader for a customer support assistant."


def judge(question, expected, answer):
    rubric = (HERE / "rubric.txt").read_text().strip()
    prompt = (f"{rubric}\n\nQuestion: {question}\nExpected answer: {expected}\nAnswer to grade: {answer}\n\n"
              'Reply with JSON: {"verdict": "pass" or "fail", "reason": "one sentence"}')
    raw = client.chat.completions.create(
        model="lab-smart",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
    ).choices[0].message.content
    result = json.loads(raw)
    verdict = str(result.get("verdict", "")).strip().lower()
    if verdict not in ("pass", "fail"):
        raise ValueError(f"judge returned no verdict: {raw}")
    return {"verdict": verdict, "reason": result.get("reason", "")}


if __name__ == "__main__":
    cases = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    passed = 0
    for c in cases:
        v = judge(c["question"], c["expected"], c["answer"])
        passed += v["verdict"] == "pass"
        print(f"{c['id']} {v['verdict']} - {v['reason']}")
    print(f"pass rate: {passed}/{len(cases)}")
EOF
```

## What to build

1. Write `/root/fde-lab/27-judge/agreement.py`, used as `python agreement.py LABELS`. For each case it runs `judge()` and prints `<id> human=<label> judge=<verdict>`, adding ` DISAGREE` when they differ. Last line: `agreement: N/M`.
2. Run it with the vague rubric and read the disagreements. Which biases from the lesson do you see?
3. Rewrite `rubric.txt` so the judge grades facts, not style. It must contain these two rules:
   ```text
   Fail the answer if any number, deadline or amount differs from the expected answer.
   Ignore tone, politeness and length.
   ```
4. Run it again until agreement is `4/4`.

```bash
cd /root/fde-lab/27-judge
python agreement.py labels.jsonl
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The vague rubric passes a wrong deadline because the answer is friendly, and fails a correct answer because it's terse.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/27-judge
cat > agreement.py <<'EOF'
import json
import sys

from judge import judge

labels = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
agree = 0
for c in labels:
    v = judge(c["question"], c["expected"], c["answer"])["verdict"]
    same = v == c["human"]
    agree += same
    print(f"{c['id']} human={c['human']} judge={v}{'' if same else ' DISAGREE'}")
print(f"agreement: {agree}/{len(labels)}")

EOF
python agreement.py labels.jsonl
cat > rubric.txt <<'EOF'
Grade the answer against the expected answer.
Fail the answer if any number, deadline or amount differs from the expected answer.
Ignore tone, politeness and length.
Pass if it contains every expected fact.
EOF
python agreement.py labels.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/27-judge; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/agreement.py 2>/dev/null && [ -s $D/agreement.py ] && echo "✅ agreement.py reads the key from the environment" || echo "❌ agreement.py must not contain a key - let the SDK read it from the environment"
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
rc, out, err = run("agreement.py", "labels.jsonl")
ok(rc == 0 and out.splitlines()[-1:] == ["agreement: 4/4"], "with your rubric the judge agrees with the human labels 4/4", f"expected 'agreement: 4/4' - got {out[-300:]!r} {err[-200:]}")
import shutil, tempfile
tmp = tempfile.mkdtemp()
for f in ("judge.py", "agreement.py", "labels.jsonl"):
    if Path(f).exists():
        shutil.copy(f, tmp)
Path(tmp, "rubric.txt").write_text('Grade whether the answer is helpful, polite and correct.')
rc, out, err = run("agreement.py", "labels.jsonl", cwd=tmp)
ok(rc == 0 and out.splitlines()[-1:] == ["agreement: 1/4"] and out.count("DISAGREE") == 3, "with the vague rubric agreement.py reports 1/4 and flags the three disagreements", f"agreement.py should really call the judge: with the vague rubric expected 1/4 and three DISAGREE lines - got {out[-300:]!r} {err[-200:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-smart" and (.client | startswith("OpenAI/Python")) and .json_mode and .temperature == 0)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-smart call" || echo "❌ the gateway has no lab-smart call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Judges favour friendly, long answers and forgive wrong numbers unless told otherwise.
- Measure judge agreement against human labels, and read every disagreement.
- Concrete fail conditions in the rubric fix most judge errors.
