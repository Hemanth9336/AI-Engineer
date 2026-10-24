---
type: task
title: "Write a pilot success criteria file"
minutes: 9
---

## Set up

```bash
mkdir -p /root/fde-lab/40-pilot
cd /root/fde-lab/40-pilot
```

## What to build

Write `/root/fde-lab/40-pilot/pilot.json` for a six-agent pilot of the Harbor Foods reply-drafting assistant:

```json
{"use_case": "...", "users": 6, "start": "YYYY-MM-DD", "duration_weeks": 6, "decision_date": "YYYY-MM-DD",
 "metrics": [{"name": "...", "kind": "quality|adoption|safety|efficiency", "target": 90, "unit": "...", "measured_by": "..."}],
 "go_if": "...", "stop_if": "..."}
```

- At least **four** metrics, covering **quality**, **adoption** and **safety** (efficiency is a bonus). Every `target` is a number and every `measured_by` names a real measurement.
- `duration_weeks` between 2 and 12; `decision_date` after `start`, no more than two weeks after the pilot ends.
- `go_if` and `stop_if` are concrete sentences.

```bash
cd /root/fde-lab/40-pilot
jq '.metrics[] | {kind, name, target}' pilot.json
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Include at least one safety metric with a target of 0 (leaks) or 100 (trap refusals).

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/40-pilot
cat > pilot.json <<'EOF'
{
  "use_case": "Reply drafts for the Harbor Foods supplier desk, reviewed by agents in Zendesk",
  "users": 6,
  "start": "2026-05-04",
  "duration_weeks": 6,
  "decision_date": "2026-06-15",
  "metrics": [
    {
      "name": "Golden-set correctness",
      "kind": "quality",
      "target": 90,
      "unit": "percent",
      "measured_by": "Weekly eval run on the 100-question golden set"
    },
    {
      "name": "Drafts sent with light or no edits",
      "kind": "quality",
      "target": 70,
      "unit": "percent",
      "measured_by": "Zendesk edit-distance report"
    },
    {
      "name": "Agents using drafts weekly",
      "kind": "adoption",
      "target": 5,
      "unit": "agents of 6",
      "measured_by": "Call logs per agent per week"
    },
    {
      "name": "Trap questions refused",
      "kind": "safety",
      "target": 100,
      "unit": "percent",
      "measured_by": "Weekly eval run, trap slice"
    },
    {
      "name": "PII in outbound prompts",
      "kind": "safety",
      "target": 0,
      "unit": "leaks",
      "measured_by": "Nightly check_redaction.py on the outbound log"
    },
    {
      "name": "First reply time for repeat questions",
      "kind": "efficiency",
      "target": 4,
      "unit": "working hours",
      "measured_by": "Zendesk first-reply report"
    }
  ],
  "go_if": "All quality and safety targets met for the last two weeks, and at least 5 of 6 agents still using drafts.",
  "stop_if": "Any PII leak, trap refusal below 95%, or correctness below 80% after week 4 fixes."
}
EOF
jq '.metrics[] | {kind, name, target}' pilot.json
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
from datetime import date, timedelta
p = load("pilot.json")
ok(isinstance(p, dict), "pilot.json is valid JSON", "pilot.json is missing or isn't valid JSON")
p = p if isinstance(p, dict) else {}
ms = p.get("metrics") if isinstance(p.get("metrics"), list) else []
ok(len(ms) >= 4 and {"quality", "adoption", "safety"} <= {m.get("kind") for m in ms}, f"{len(ms)} metrics covering quality, adoption and safety", f"need 4+ metrics with kinds including quality, adoption and safety - got {[m.get('kind') for m in ms]}")
ok(ms and all(isinstance(m.get("target"), (int, float)) and not isinstance(m.get("target"), bool) and len(str(m.get("measured_by", "")).split()) >= 2 and str(m.get("name", "")).strip() for m in ms), "every metric has a name, a numeric target and how it's measured", "each metric needs a name, a numeric target and a measured_by description")
try:
    start, dec = date.fromisoformat(p.get("start", "")), date.fromisoformat(p.get("decision_date", ""))
    weeks = p.get("duration_weeks")
    good = isinstance(weeks, int) and 2 <= weeks <= 12 and start < dec <= start + timedelta(weeks=weeks + 2)
except Exception:
    good = False
ok(good, "the duration and decision date fit together", "duration_weeks must be 2-12 and decision_date after start, at most two weeks after the pilot ends (ISO dates)")
ok(len(str(p.get("go_if", "")).split()) >= 6 and len(str(p.get("stop_if", "")).split()) >= 6, "go and stop criteria are written out", "go_if and stop_if need concrete sentences")
ok(isinstance(p.get("users"), int) and p.get("users") > 0 and str(p.get("use_case", "")).strip(), "use case and number of users are set", "set use_case and users")
PYEOF
```

## What you learned

- Agree pilot success before it starts, or the decision becomes political.
- Cover quality, adoption, safety and efficiency - each with a number and a measurement.
- Keep the criteria in a file so the goalposts can't move.
