---
type: task
title: "Run one task on two models"
minutes: 23
---

## Set up

Set up creates `/root/mastery/008-models/tickets.txt`, five support tickets.

```bash
mkdir -p /root/mastery/008-models && cd /root/mastery/008-models
cat > tickets.txt <<'EOF'
T-101 | login page shows blank screen after password reset
T-102 | invoice PDF has wrong VAT number
T-103 | cannot upload avatar larger than 2 MB
T-104 | password reset email never arrives
T-105 | invoice totals round down instead of to nearest cent
EOF
```

## What to build

Measure the same task on two models from `/root/mastery/008-models`.

1. Run this prompt once with `--model haiku` and once with `--model sonnet`, saving the envelopes as `haiku.json` and `sonnet.json`:

   > Read tickets.txt and reply with only the ticket ids that are about invoices, comma separated.

2. Write `compare.txt` from the envelopes (not from memory):

```text
haiku: <duration_ms> ms, $<total_cost_usd>
sonnet: <duration_ms> ms, $<total_cost_usd>
faster: <haiku|sonnet>
cheaper: <haiku|sonnet>
```

Both answers must be correct - a fast wrong answer does not count.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `modelUsage` names the model that answered - check it matches the flag you passed.
- `jq -r .duration_ms haiku.json` prints one value; a short Python script can write all four lines.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/008-models
claude -p "Read tickets.txt and reply with only the ticket ids that are about invoices, comma separated." --model haiku --output-format json > haiku.json
claude -p "Read tickets.txt and reply with only the ticket ids that are about invoices, comma separated." --model sonnet --output-format json > sonnet.json
python3 - <<'EOF'
import json
h, s = json.load(open("haiku.json")), json.load(open("sonnet.json"))
with open("compare.txt", "w") as f:
    for name, r in (("haiku", h), ("sonnet", s)):
        f.write(f"{name}: {r['duration_ms']} ms, ${r['total_cost_usd']:.6f}\n")
    f.write("faster: " + ("haiku" if h["duration_ms"] <= s["duration_ms"] else "sonnet") + "\n")
    f.write("cheaper: " + ("haiku" if h["total_cost_usd"] <= s["total_cost_usd"] else "sonnet") + "\n")
EOF
cat compare.txt
```

</details>

## Check your work

```bash
D=/root/mastery/008-models; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
python3 - <<'PYEOF'
import glob, hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def text(p):
    try:
        return Path(p).read_text()
    except Exception:
        return ""
def sha(p):
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except Exception:
        return None
def sh(cmd, cwd=None, env=None, input=None, timeout=60):
    try:
        r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, cwd=cwd, input=input,
                           timeout=timeout, env=dict(os.environ, **(env or {})))
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"
def sessions(d):
    # Claude Code saves every session (console or -p) as ~/.claude/projects/<dir>/<id>.jsonl, one JSON row per event
    real, out = os.path.realpath(d), []
    for f in sorted(glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")), key=os.path.getmtime):
        rows = []
        for line in open(f, errors="replace"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
        if any(r.get("cwd") and os.path.realpath(r["cwd"]) == real for r in rows):
            out.append(rows)
    return out
def ran(pat, d=None):
    return [rows for rows in sessions(d or os.getcwd()) if any(re.search(pat, p, re.I | re.S) for p in prompts(rows))]
def content(r):
    c = (r.get("message") or {}).get("content")
    return c if isinstance(c, list) else ([{"type": "text", "text": c}] if isinstance(c, str) else [])
def prompts(rows):
    return [b.get("text", "") for r in rows if r.get("type") == "user" and not r.get("isMeta") for b in content(r) if b.get("type") == "text"]
def uses(rows):
    return [b for r in rows if r.get("type") == "assistant" for b in content(r) if b.get("type") == "tool_use"]
def results(rows):
    return [b for r in rows if r.get("type") == "user" for b in content(r) if b.get("type") == "tool_result"]
def models(rows):
    return {(r.get("message") or {}).get("model") for r in rows if r.get("type") == "assistant"} - {None, "<synthetic>"}
def is_haiku(m):
    return bool(m) and ("haiku" in m.lower() or m == os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL"))
def events(p):
    out = []
    for line in text(p).splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out
def init(ev):
    return next((e for e in ev if e.get("type") == "system" and e.get("subtype") == "init"), {})
def result(ev):
    return next((e for e in ev if e.get("type") == "result"), {})
def ev_uses(ev):
    return [b for e in ev if e.get("type") == "assistant" for b in content(e) if b.get("type") == "tool_use"]
h, s = load("haiku.json") or {}, load("sonnet.json") or {}
for name, r in (("haiku", h), ("sonnet", s)):
    ok(r.get("subtype") == "success" and (r.get("result") or "").replace(" ", "") in ("T-102,T-105", "T-105,T-102"),
       f"{name}.json answered correctly ({r.get('result')})", f"{name}.json should be a successful run answering T-102,T-105 - got {r.get('result')!r}")
hm, sm = set((h.get("modelUsage") or {}).keys()), set((s.get("modelUsage") or {}).keys())
haikuish = any(is_haiku(m) for m in hm)
ok(hm and sm and hm != sm and haikuish and not any(is_haiku(m) for m in sm),
   f"the two runs used different models ({sorted(hm)} vs {sorted(sm)})", f"run one with --model haiku and one with --model sonnet - modelUsage shows {sorted(hm)} and {sorted(sm)}")
lines = dict(l.split(": ", 1) for l in text("compare.txt").splitlines() if ": " in l)
def num(v, pat):
    m = re.search(pat, v or "")
    return float(m.group(1)) if m else None
good = True
for name, r in (("haiku", h), ("sonnet", s)):
    ms, cost = num(lines.get(name), r"(\d+)\s*ms"), num(lines.get(name), r"\$([0-9.]+)")
    good &= ms == r.get("duration_ms") and cost is not None and abs(cost - (r.get("total_cost_usd") or -1)) < 1e-6
ok(good, "compare.txt reports each run's duration_ms and total_cost_usd", "compare.txt lines should read like 'haiku: 812 ms, $0.000123' using the envelope values")
if h and s:
    fast = "haiku" if h["duration_ms"] <= s["duration_ms"] else "sonnet"
    cheap = "haiku" if h["total_cost_usd"] <= s["total_cost_usd"] else "sonnet"
    ok(lines.get("faster") == fast and lines.get("cheaper") == cheap, f"compare.txt picks faster: {fast}, cheaper: {cheap}",
       f"compare.txt should say faster: {fast} and cheaper: {cheap}, from the envelopes")
PYEOF
```

## What you learned

- Aliases (haiku, sonnet, opus) pick a model family; --model and /model choose per run or session.
- The envelope's duration_ms, total_cost_usd, and modelUsage turn model choice into a measurement.
- Compare price and speed only after both answers are correct.
