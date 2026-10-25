---
type: task
title: "A gate that fails on score drop"
minutes: 10
---

## Set up

Same folder, with `evals/results_v1.json` (baseline) and `evals/results_v2.json` (candidate) from the previous task.

```bash
mkdir -p /root/harness-lab/33-regression
cd /root/harness-lab/33-regression
```

## What to build

Write `/root/harness-lab/33-regression/gate.py` - the check that runs in CI before a harness change can merge:

`python gate.py BASELINE CANDIDATE [--max-drop X] [--must-pass ID ...]`

1. Score both runs **over the baseline's task ids** (a task missing from the candidate counts as failed).
2. Print `score <before> -> <after>; regressions: <ids or none>`.
3. **FAIL** (print a line starting `FAIL:` with the reasons, exit 1) if the score dropped by more than `--max-drop` (default 0), or if any `--must-pass` task fails in the candidate.
4. Otherwise print `PASS` and exit 0.

```bash
cd /root/harness-lab/33-regression
python gate.py evals/results_v1.json evals/results_v2.json --must-pass no-delete; echo "exit $?"
python gate.py evals/results_v1.json evals/results_v1.json; echo "exit $?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `argparse` with `nargs="*"` gives you a list for `--must-pass`.
- Compare floats with a small tolerance, so a 0.0 max-drop doesn't fail on rounding.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/33-regression
cat > gate.py <<'EOF'
"""Fail if a candidate eval run is worse than the baseline.

python gate.py BASELINE CANDIDATE [--max-drop 0.0] [--must-pass ID ...]
"""
import argparse
import json
import sys

ap = argparse.ArgumentParser()
ap.add_argument("baseline")
ap.add_argument("candidate")
ap.add_argument("--max-drop", type=float, default=0.0)
ap.add_argument("--must-pass", nargs="*", default=[])
a = ap.parse_args()
base, cand = json.load(open(a.baseline)), json.load(open(a.candidate))
before = {t["id"]: t["pass"] for t in base["tasks"]}
after = {t["id"]: t["pass"] for t in cand["tasks"]}
score_before = sum(before.values()) / len(before)
score_after = sum(after.get(i, False) for i in before) / len(before)
regressions = [i for i in before if before[i] and not after.get(i, False)]
failed_must = [i for i in a.must_pass if not after.get(i, False)]
problems = []
if score_before - score_after > a.max_drop + 1e-9:
    problems.append(f"score dropped {score_before:.3f} -> {score_after:.3f} (more than {a.max_drop:.3f})")
if failed_must:
    problems.append(f"must-pass tasks failed: {', '.join(failed_must)}")
print(f"score {score_before:.3f} -> {score_after:.3f}; regressions: {', '.join(regressions) or 'none'}")
if problems:
    print("FAIL: " + "; ".join(problems))
    sys.exit(1)
print("PASS")

EOF
python gate.py evals/results_v1.json evals/results_v2.json --must-pass no-delete || echo "gate failed with exit $?"
python gate.py evals/results_v1.json evals/results_v1.json
```

</details>

## Check your work

```bash
D=/root/harness-lab/33-regression; cd $D 2>/dev/null || echo "❌ create $D"
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
sys.path.insert(0, '/opt/harness')
from labmock import MockModel
import tempfile
d = Path(tempfile.mkdtemp())
def write(name, passes):
    (d / name).write_text(json.dumps({"score": round(sum(passes.values()) / len(passes), 3), "tasks": [{"id": k, "pass": v} for k, v in passes.items()]}))
    return str(d / name)
def gate(*args):
    r = subprocess.run([sys.executable, "gate.py", *args], capture_output=True, text=True, timeout=30)
    return r.returncode, r.stdout
base = write("base.json", {"a": True, "b": True, "c": False, "safe": True})
cases = [
    ("identical runs pass", [base, base], 0, None),
    ("a score drop fails", [base, write("drop.json", {"a": True, "b": False, "c": False, "safe": True})], 1, "b"),
    ("a swap at the same score passes, but the regression is printed", [base, write("swap.json", {"a": False, "b": True, "c": True, "safe": True})], 0, "a"),
    ("--max-drop allows a small drop", [base, write("small.json", {"a": True, "b": False, "c": False, "safe": True}), "--max-drop", "0.3"], 0, "b"),
    ("a failing --must-pass task fails even when the score is fine", [base, write("must.json", {"a": True, "b": True, "c": True, "safe": False}), "--must-pass", "safe"], 1, "safe"),
    ("a task missing from the candidate counts as failed", [base, write("miss.json", {"a": True, "c": False, "safe": True})], 1, "b"),
    ("an improvement passes", [base, write("up.json", {"a": True, "b": True, "c": True, "safe": True})], 0, None),
]
for name, args, code, reg in cases:
    rc, out = gate(*args)
    first = out.splitlines()[0] if out.strip() else ""
    good = rc == code and first.startswith("score ") and (("regressions: none" in first) if reg is None else (reg in first.split("regressions:", 1)[-1])) and (("FAIL:" in out) == (code == 1)) and (out.strip().endswith("PASS") == (code == 0))
    ok(good, name, f"{name}: exit {rc} (expected {code}), output {out.strip()[:200]!r}")
rc, out = gate("evals/results_v1.json", "evals/results_v2.json", "--must-pass", "no-delete")
ok(rc == 1 and "no-delete" in out, "the gate blocks prompt_v2", f"exit {rc}: {out[-150:]!r}")
PYEOF
```

## What you learned

- A regression gate compares a candidate eval run to a baseline and fails the change automatically.
- Score drops and failed must-pass tasks are hard failures; regressions are always reported.
- Score over the baseline's tasks, so removing a task can't hide a failure.
