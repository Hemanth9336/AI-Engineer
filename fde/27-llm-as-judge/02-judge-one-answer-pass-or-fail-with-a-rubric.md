---
type: task
title: "Judge one answer pass or fail with a rubric"
minutes: 9
---

## Set up

`cases.jsonl` holds three bot answers to grade, each with the question and the expected answer.

```bash
mkdir -p /root/fde-lab/27-judge
cd /root/fde-lab/27-judge
cat > cases.jsonl <<'EOF'
{"id": "c1", "question": "How long do I have to report damage?", "expected": "Within 7 days of delivery, with photos.", "answer": "You have 7 days from delivery; include photos."}
{"id": "c2", "question": "What does an address change cost after dispatch?", "expected": "6 EUR and one extra working day.", "answer": "Changing the address after dispatch is free."}
{"id": "c3", "question": "When is support open?", "expected": "8:00 to 18:00 CET, Monday to Friday.", "answer": "Support is open 8:00 to 18:00 CET on weekdays."}
EOF
```

## What to build

Build a judge in `/root/fde-lab/27-judge`:

1. `rubric.txt` - your grading instructions. Start with:
   ```text
   Grade the answer against the expected answer. Pass if it contains the expected facts. Fail if a fact is missing or wrong.
   ```
2. `judge.py` with `judge(question, expected, answer)`:
   - Reads `rubric.txt` **on every call** (you'll edit it in the next task).
   - Calls `lab-smart` at `temperature=0` in JSON mode. System message: `You are a strict grader for a customer support assistant.` The user message holds the rubric, then `Question:`, `Expected answer:` and `Answer to grade:` lines, then: `Reply with JSON: {"verdict": "pass" or "fail", "reason": "one sentence"}`
   - Returns `{"verdict": "pass"|"fail", "reason": ...}`, lower-casing the verdict, and raises `ValueError` if it's neither.
3. `python judge.py CASES` prints `<id> <verdict> - <reason>` per case, then `pass rate: N/M`.

```bash
cd /root/fde-lab/27-judge
python judge.py cases.jsonl
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Write the JSON example in the prompt with single-quoted Python strings, so you don't have to escape its braces in an f-string.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/27-judge
cat > rubric.txt <<'EOF'
Grade the answer against the expected answer. Pass if it contains the expected facts. Fail if a fact is missing or wrong.
EOF
cat > judge.py <<'EOF'
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
python judge.py cases.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/27-judge; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/judge.py 2>/dev/null && [ -s $D/judge.py ] && echo "✅ judge.py reads the key from the environment" || echo "❌ judge.py must not contain a key - let the SDK read it from the environment"
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
Path("/tmp/judge-cases.jsonl").write_text("".join(json.dumps(c) + "\n" for c in [
    {"id": "k1", "question": "How long do I have to report damage?", "expected": "Within 7 days of delivery, with photos.", "answer": "Damage must be reported within 7 days, with photos of the item."},
    {"id": "k2", "question": "How heavy can a standard pallet be?", "expected": "Up to 800 kg and 1.8 m high.", "answer": "Pallets can go up to 2,000 kg."},
]))
rc, out, err = run("judge.py", "/tmp/judge-cases.jsonl")
lines = out.splitlines()
ok(rc == 0 and len(lines) == 3 and lines[0].startswith("k1 pass") and lines[1].startswith("k2 fail") and lines[2] == "pass rate: 1/2", "the judge passed the right answer and failed the wrong one", f"expected 'k1 pass ...', 'k2 fail ...', 'pass rate: 1/2' - got {lines} {err[-200:]}")
sys.path.insert(0, ".")
try:
    import judge
    import types
    fake = types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda **k: types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='{"verdict": "maybe", "reason": "unsure"}'))]))))
    judge.client = fake
    try:
        judge.judge("q", "e", "a")
        raised = False
    except ValueError:
        raised = True
    ok(raised, "a verdict other than pass or fail raises ValueError", "judge() must raise ValueError when the verdict isn't pass or fail")
except Exception as e:
    print(f"❌ import judge failed: {e}")
rubric = Path("rubric.txt").read_text() if Path("rubric.txt").exists() else ""
ok(len(rubric.split()) >= 8, "the rubric lives in rubric.txt", "write your grading instructions in rubric.txt")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-smart" and (.client | startswith("OpenAI/Python")) and .json_mode and .temperature == 0 and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-smart call" || echo "❌ the gateway has no lab-smart call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A judge grades an answer against the expected answer and a rubric.
- Binary verdicts with a reason are more consistent than 1-10 scores.
- Use a strong model at temperature 0 with structured output - and reject bad verdicts.
