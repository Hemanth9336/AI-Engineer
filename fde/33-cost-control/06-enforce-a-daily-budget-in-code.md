---
type: task
title: "Enforce a daily budget in code"
minutes: 8
---

## Set up

```bash
mkdir -p /root/fde-lab/33-cost
cd /root/fde-lab/33-cost
rm -f usage.json
```

## What to build

Write `/root/fde-lab/33-cost/budget.py`:

- The daily limit comes from the `DAILY_TOKEN_LIMIT` environment variable (default `20000`).
- Usage is stored in `usage.json` next to the script, as `{"2026-03-14": 1234}` - tokens used per day (`date.today().isoformat()`).
- `ask(question)` raises `BudgetExceeded` **before** calling the API when today's usage is already at or over the limit. Otherwise it calls `lab-mini` and adds the response's `usage.total_tokens` to today's total.
- `python budget.py QUESTION` prints the answer, or - when over budget - prints `Daily AI budget reached - please try again tomorrow.`, writes the details to stderr and exits with status `3`.

```bash
cd /root/fde-lab/33-cost
python budget.py "When is support open?"
cat usage.json
DAILY_TOKEN_LIMIT=1 python budget.py "When is support open?"; echo "exit $?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Read `usage.json` fresh in each function - another process may have updated it.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/33-cost
cat > budget.py <<'EOF'
import json
import os
import sys
from datetime import date
from pathlib import Path

from openai import OpenAI

USAGE = Path(__file__).with_name("usage.json")
MESSAGE = "Daily AI budget reached - please try again tomorrow."


class BudgetExceeded(Exception):
    pass


def limit():
    return int(os.environ.get("DAILY_TOKEN_LIMIT", "20000"))


def used_today():
    usage = json.loads(USAGE.read_text()) if USAGE.exists() else {}
    return usage.get(date.today().isoformat(), 0)


def record(tokens):
    usage = json.loads(USAGE.read_text()) if USAGE.exists() else {}
    today = date.today().isoformat()
    usage[today] = usage.get(today, 0) + tokens
    USAGE.write_text(json.dumps(usage))


def ask(question):
    if used_today() >= limit():
        raise BudgetExceeded(f"{used_today()} of {limit()} tokens used today")
    resp = OpenAI().chat.completions.create(
        model="lab-mini", temperature=0,
        messages=[{"role": "system", "content": "You are Meridian Logistics' support assistant."}, {"role": "user", "content": question}],
    )
    record(resp.usage.total_tokens)
    return resp.choices[0].message.content


if __name__ == "__main__":
    try:
        print(ask(sys.argv[1]))
    except BudgetExceeded as e:
        print(MESSAGE)
        print(f"[budget] {e}", file=sys.stderr)
        sys.exit(3)

EOF
python budget.py "When is support open?"
cat usage.json
DAILY_TOKEN_LIMIT=1 python budget.py "When is support open?" || echo "blocked as expected"
```

</details>

## Check your work

```bash
D=/root/fde-lab/33-cost; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/budget.py 2>/dev/null && [ -s $D/budget.py ] && echo "✅ budget.py reads the key from the environment" || echo "❌ budget.py must not contain a key - let the SDK read it from the environment"
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
from datetime import date
today = date.today().isoformat()
Path("usage.json").write_text(json.dumps({"2020-01-01": 999999}))
def logged():
    return [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
b = len(logged())
env = dict(os.environ, DAILY_TOKEN_LIMIT="5000")
r = subprocess.run([sys.executable, "budget.py", "Where is my parcel?"], capture_output=True, text=True, env=env)
new = logged()[b:]
usage = load("usage.json") or {}
ok(r.returncode == 0 and len(new) == 1 and new[0].get("model") == "lab-mini" and usage.get(today) == new[0].get("total_tokens"),
   "a call under budget went to lab-mini and today's usage records its tokens", f"expected one lab-mini call and usage.json[{today!r}] equal to its total_tokens - got {usage}, {[x.get('total_tokens') for x in new]} {r.stderr[-200:]}")
ok(usage.get("2020-01-01") == 999999, "other days' usage is left alone", "keep other dates in usage.json - only today's total counts")
Path("usage.json").write_text(json.dumps({today: 5000}))
b = len(logged())
r = subprocess.run([sys.executable, "budget.py", "Where is my parcel?"], capture_output=True, text=True, env=env)
ok(r.returncode == 3 and r.stdout.strip() == 'Daily AI budget reached - please try again tomorrow.' and len(logged()) == b, "at the limit the script refuses with exit 3 and makes no call", f"with 5000 of 5000 used expected exit 3, the budget message and no API call - got exit {r.returncode}, {r.stdout[-150:]!r}")
Path("usage.json").write_text(json.dumps({today: 4999}))
r = subprocess.run([sys.executable, "budget.py", "Where is my parcel?"], capture_output=True, text=True, env=env)
ok(r.returncode == 0 and (load("usage.json") or {}).get(today, 0) > 5000, "just under the limit the call goes through and usage passes the limit", "with 4999 of 5000 used the call should still go through and be recorded")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Budgets cap the worst case that caching and routing can't.
- Check the budget before the call and record actual usage after it.
- What happens at the limit - stop, downgrade or alert - is a business decision.
