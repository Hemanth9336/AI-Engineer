---
type: task
title: "Write a handoff runbook"
minutes: 12
---

## Set up

`system.md` collects the facts about the Harbor Foods assistant at the end of the engagement.

```bash
mkdir -p /root/fde-lab/41-handoff
cd /root/fde-lab/41-handoff
cat > system.md <<'EOF'
# Harbor Foods supplier desk assistant - system facts

- Purpose: drafts replies to supplier emails in Zendesk; agents review and send.
- Code: git repository harbor-foods/desk-assistant, Python 3.12.
- Runs as: a container `desk-assistant` on the Harbor Foods Kubernetes cluster, namespace `ai-apps`.
- Model: lab-fast through the company AI gateway; fallback lab-mini (2 s timeout).
- Retrieval: handbook + portal FAQ, chunked by section, embedded with lab-embed; index rebuilt nightly at 02:00 by `reindex.py`.
- Prompts: prompts/v6.txt (current). Golden set: evals/golden.jsonl (112 cases).
- Evals: `python evals.py prompts/v6.txt evals/golden.jsonl` then `python gate.py results/v5.json results/v6.json`.
- Logs: calls in /var/log/desk-assistant/calls.jsonl; outbound prompts (redacted) in /var/log/desk-assistant/outbound.jsonl.
- Daily report: `python report.py /var/log/desk-assistant/calls.jsonl YYYY-MM-DD prices.json`, emailed 07:00.
- Budget: 3,000,000 tokens/day, enforced in code.
- Known issues seen in the pilot: re-index skipped empty articles; gateway timeouts at peak; handbook and FAQ contradicting each other on slot times.
- People: Marta Kovacs (Head of Supplier Operations, business owner), Tom Berger (IT platform team, on-call), Lena Ruiz (desk team lead, golden set owner), privacy@harborfoods.example (DPO).
EOF
```

## What to build

Write `/root/fde-lab/41-handoff/RUNBOOK.md` for the Harbor Foods IT team, using the facts in `system.md`. Use these `##` sections:

`Overview`, `Architecture`, `Running it`, `Monitoring`, `Common failures`, `Changing prompts`, `Evals`, `Contacts`

- **Common failures** - at least **three** `###` entries, each with a symptom, what to check, and the fix. Use the known issues.
- **Monitoring** - the real log path and what to watch (errors, latency, cost or budget, PII).
- **Changing prompts** - the steps, including running the evals and the gate before shipping.
- **Evals** - the exact commands in a fenced code block (fenced with three backticks or `~~~`).
- **Contacts** - at least three named people or addresses, with their roles.

```bash
cd /root/fde-lab/41-handoff
grep -E '^(##|###) ' RUNBOOK.md
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Write it for someone who joins the team next year and has never met you.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/41-handoff
cat > RUNBOOK.md <<'EOF'
# Runbook: Harbor Foods supplier desk assistant

## Overview
Drafts replies to supplier emails in Zendesk from the supplier handbook and portal FAQ. Agents review every draft before sending. Business owner: Marta Kovacs.

## Architecture
- Container `desk-assistant` in Kubernetes namespace `ai-apps`, code in harbor-foods/desk-assistant.
- Retrieval over handbook + FAQ sections embedded with lab-embed; index rebuilt nightly at 02:00 by `reindex.py`.
- Generation with lab-fast through the AI gateway; falls back to lab-mini after a 2 s timeout.
- PII is redacted before every model call.

## Running it
- Deploy: merge to main; the pipeline builds and rolls out the `desk-assistant` container.
- Restart: `kubectl -n ai-apps rollout restart deployment/desk-assistant`.
- Rebuild the index by hand: `python reindex.py`.

## Monitoring
- Call log: /var/log/desk-assistant/calls.jsonl. Daily report (calls, errors, cost, p95 latency) emailed at 07:00.
- Watch: error rate above 5%, p95 latency above 6 s, daily tokens near the 3,000,000 budget, any leak from the nightly check_redaction.py run on /var/log/desk-assistant/outbound.jsonl.

## Common failures
### Answers cite the wrong or old policy
- Symptom: drafts quote outdated slot times or miss an article.
- Check: the latest re-index log for skipped or empty articles; compare article counts with the previous run.
- Fix: correct the source export, re-run `python reindex.py`, add the question to the golden set.
### Timeouts and slow drafts at peak
- Symptom: p95 latency spikes, many `[fallback]` lines.
- Check: AI gateway status and the share of lab-mini calls in the daily report.
- Fix: none needed if the fallback holds; escalate to the gateway team if errors persist over 30 minutes.
### Budget reached
- Symptom: drafts stop with "Daily AI budget reached".
- Check: the daily report for unusual volume (loops, scripts).
- Fix: find the cause first; raise the budget only with Marta Kovacs' approval.

## Changing prompts
1. Copy the current prompt to a new version file, e.g. prompts/v7.txt - never edit v6 in place.
2. Run the evals and the gate against the current version (see Evals). Do not ship if the gate fails.
3. Record the change and the scores in CHANGELOG.md, then deploy.

## Evals
~~~bash
python evals.py prompts/v6.txt evals/golden.jsonl
python gate.py results/v5.json results/v6.json
~~~
The golden set (112 cases) is owned by Lena Ruiz. Add every reported wrong answer as a new case.

## Contacts
- Business owner: Marta Kovacs, Head of Supplier Operations.
- On-call / platform: Tom Berger, IT platform team.
- Golden set and agent feedback: Lena Ruiz, desk team lead.
- Data protection questions: privacy@harborfoods.example.
EOF
grep -E '^(##|###) ' RUNBOOK.md
```

</details>

## Check your work

```bash
D=/root/fde-lab/41-handoff; cd $D 2>/dev/null || echo "❌ create $D"
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
import re
def sections(path):
    text = Path(path).read_text() if Path(path).exists() else ""
    out, name = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            name = m.group(1).strip().lower()
            out[name] = []
        elif name is not None and line.strip():
            out[name].append(line.strip())
    return out
def bullets(lines):
    return [l for l in lines if re.match(r"^([-*]|\d+\.)\s+\S", l)]

s = sections("RUNBOOK.md")
want = ['overview', 'architecture', 'running it', 'monitoring', 'common failures', 'changing prompts', 'evals', 'contacts']
missing = [h for h in want if not s.get(h)]
ok(not missing, "RUNBOOK.md has all eight sections with content", f"missing or empty sections: {missing}")
text = Path("RUNBOOK.md").read_text() if Path("RUNBOOK.md").exists() else ""
cf = re.search(r"^## Common failures\s*$(.*?)(?=^## |\Z)", text, re.M | re.S | re.I)
entries = re.split(r"^### ", cf.group(1), flags=re.M)[1:] if cf else []
good = [e for e in entries if re.search(r"symptom", e, re.I) and re.search(r"fix", e, re.I)]
ok(len(good) >= 3, f"{len(good)} failure entries with a symptom and a fix", f"Common failures needs 3+ '###' entries, each with a symptom and a fix - got {len(good)}")
mon = " ".join(s.get("monitoring", []))
ok("/var/log/desk-assistant/calls.jsonl" in mon and re.search(r"latency|p95", mon, re.I) and re.search(r"cost|budget|token", mon, re.I), "monitoring names the real log path, latency and cost", "Monitoring should give the calls.jsonl path and say what to watch: errors, latency, cost/budget")
ev = re.search(r"^## Evals\s*$(.*?)(?=^## |\Z)", text, re.M | re.S | re.I)
ok(ev and ("`" * 3 in ev.group(1) or "~" * 3 in ev.group(1)) and "evals.py" in ev.group(1) and "gate.py" in ev.group(1), "the Evals section has the exact commands in a code block", "put the evals.py and gate.py commands in a fenced code block under Evals")
ok(re.search(r"eval|gate", " ".join(s.get("changing prompts", [])), re.I), "prompt changes go through the evals and gate", "Changing prompts must include running the evals and the gate")
contacts = [l for l in s.get("contacts", []) if re.search(r"Kovacs|Berger|Ruiz|privacy@", l)]
ok(len(contacts) >= 3, "contacts list the named owners and their roles", f"Contacts should list at least three of the people from system.md - got {len(contacts)}")
PYEOF
```

## What you learned

- A runbook is written for the next owner, not for you.
- Common failures need a symptom, a check and a fix - from real incidents.
- Changes go through evals and the gate; owners and contacts are named.
