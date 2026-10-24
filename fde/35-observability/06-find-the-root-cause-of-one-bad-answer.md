---
type: task
title: "Find the root cause of one bad answer"
minutes: 8
---

## Set up

`incident/` holds the customer's complaint, the call log (with answers), the retrieval log (what each request retrieved, from which index version) and the nightly re-index log.

```bash
mkdir -p /root/fde-lab/35-observability/incident
cd /root/fde-lab/35-observability/incident
cat > complaint.txt <<'EOF'
From: Priya Shah, Kestrel Foods operations
Date: 12 March 2026

Around 10:15 this morning your assistant told our team we have 30 days to report a damaged parcel.
Your own policy says 7 days. We nearly missed a claim because of this. What happened?
EOF
cat > calls.jsonl <<'EOF'
{"ts": "2026-03-10T09:12:40+00:00", "request_id": "r-7a01", "user": "kestrel-ops", "prompt_version": "v4", "model": "lab-fast", "ok": true, "question": "How long do we have to report a damaged parcel?", "answer": "Report damage within 7 days of delivery, with photos [a1]."}
{"ts": "2026-03-12T10:09:55+00:00", "request_id": "r-7b17", "user": "harbor-foods", "prompt_version": "v4", "model": "lab-fast", "ok": true, "question": "Can I change the delivery address?", "answer": "Until the parcel leaves the depot, yes; after dispatch it costs 6 EUR [a2]."}
{"ts": "2026-03-12T10:14:02+00:00", "request_id": "r-7b22", "user": "kestrel-ops", "prompt_version": "v4", "model": "lab-fast", "ok": true, "question": "How long do we have to report a damaged parcel?", "answer": "You can report it up to 30 days after delivery [a11]."}
{"ts": "2026-03-12T10:16:30+00:00", "request_id": "r-7b23", "user": "kestrel-ops", "prompt_version": "v4", "model": "lab-fast", "ok": false, "question": "How long do we have to report a damaged parcel?", "answer": null}
{"ts": "2026-03-12T11:40:12+00:00", "request_id": "r-7b40", "user": "dockside", "prompt_version": "v4", "model": "lab-fast", "ok": true, "question": "When is support open?", "answer": "8:00 to 18:00 CET, Monday to Friday [a4]."}
EOF
cat > retrieval.jsonl <<'EOF'
{"request_id": "r-7a01", "index_version": "2026-03-09", "retrieved": [{"id": "a1", "score": 0.71}, {"id": "a11", "score": 0.52}, {"id": "a9", "score": 0.4}]}
{"request_id": "r-7b17", "index_version": "2026-03-11", "retrieved": [{"id": "a2", "score": 0.77}, {"id": "a5", "score": 0.44}, {"id": "a9", "score": 0.38}]}
{"request_id": "r-7b22", "index_version": "2026-03-11", "retrieved": [{"id": "a11", "score": 0.52}, {"id": "a9", "score": 0.4}, {"id": "a5", "score": 0.33}]}
{"request_id": "r-7b40", "index_version": "2026-03-11", "retrieved": [{"id": "a4", "score": 0.57}, {"id": "a9", "score": 0.31}, {"id": "a1", "score": 0.3}]}
EOF
cat > index.log <<'EOF'
2026-03-09T02:00:01 reindex start version=2026-03-09 source=helpcentre-export.csv
2026-03-09T02:00:09 indexed 12 articles
2026-03-09T02:00:09 reindex done version=2026-03-09
2026-03-11T02:00:01 reindex start version=2026-03-11 source=helpcentre-export.csv
2026-03-11T02:00:04 skipped a1: empty text (export column 'body' blank)
2026-03-11T02:00:08 indexed 11 articles
2026-03-11T02:00:08 reindex done version=2026-03-11
EOF
```

## What to build

Investigate the complaint with `jq` and `grep`, then write `/root/fde-lab/35-observability/incident/rootcause.json`:

```json
{"request_id": "...", "stage": "data|retrieval|prompt|model", "missing_source": "article id or null",
 "evidence": "one or two sentences", "fix": "what you'd change so it can't happen again"}
```

- `request_id` - the call that produced the answer in the complaint.
- `stage` - where the failure started, using the table in the lesson.
- `missing_source` - the article that should have been used, if it never reached the model.

```bash
cd /root/fde-lab/35-observability/incident
cat complaint.txt
jq -c 'select(.user == "kestrel-ops")' calls.jsonl
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Compare the bad request with the same question on 10 March: what differs in retrieval, and why?

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/35-observability/incident
jq -c 'select(.user == "kestrel-ops")' calls.jsonl
jq -c 'select(.request_id == "r-7b22" or .request_id == "r-7a01")' retrieval.jsonl
grep -n "a1" index.log
cat > rootcause.json <<'EOF'
{"request_id": "r-7b22", "stage": "data", "missing_source": "a1",
 "evidence": "Index 2026-03-11 skipped a1 because its body was blank in the export, so retrieval only found a11 (30-day returns) and the model answered from it. On 10 March, with a1 indexed, the same question got 7 days.",
 "fix": "Fail the re-index when an article has empty text or the article count drops, restore a1, and add this question to the golden set."}
EOF
```

</details>

## Check your work

```bash
D=/root/fde-lab/35-observability/incident; cd $D 2>/dev/null || echo "❌ create $D"
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
r = load("rootcause.json") or {}
ok(r.get("request_id") == "r-7b22", "found the request behind the complaint", f"request_id should be the call that answered '30 days' to kestrel-ops - got {r.get('request_id')!r}")
ok(r.get("missing_source") == "a1", "named the article that never reached the model", f"missing_source should be the damage-reporting article - got {r.get('missing_source')!r}")
ok(r.get("stage") == "data", "placed the failure at the data stage", f"the article was retrievable before - look at index.log to see where it went (got stage {r.get('stage')!r})")
ev, fix = str(r.get("evidence", "")), str(r.get("fix", ""))
ok(len(ev.split()) >= 10 and ("index" in ev.lower() or "empty" in ev.lower() or "blank" in ev.lower()), "the evidence points at the re-index", "evidence should say what the logs show (10+ words) - mention the re-index or empty article")
ok(len(fix.split()) >= 8, "a fix is proposed", "describe a fix that prevents a repeat (8+ words)")
PYEOF
```

## What you learned

- Trace a bad answer backwards: request, answer, retrieval, index, data.
- A correct run of the same question is the best control.
- Fix the cause at its stage and add the case to the golden set.
