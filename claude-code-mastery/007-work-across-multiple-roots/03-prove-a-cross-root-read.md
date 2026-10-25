---
type: task
title: "Prove a cross-root read"
minutes: 20
---

## Set up

Set up creates two sibling folders: `/root/mastery/007-roots/app` (your project) and `/root/mastery/007-roots/shared`, which holds `contracts/order.json`.

```bash
mkdir -p /root/mastery/007-roots/app /root/mastery/007-roots/shared/contracts && cd /root/mastery/007-roots
cat > shared/contracts/order.json <<'EOF'
{
  "schema_version": "2026-07",
  "fields": ["id", "customer", "total_cents"]
}
EOF
cat > app/main.py <<'EOF'
print("orders app")
EOF
```

## What to build

From inside `/root/mastery/007-roots/app`, prove the session boundary before and after you grant the second root.

1. Run this prompt headless **without** any extra roots and save the envelope as `before.json`:

   > Read ../shared/contracts/order.json and reply with exactly one line: schema_version: <value>. If you cannot read it, reply with exactly: schema_version: unknown

2. Run the same prompt again with `--add-dir ../shared` and save the envelope as `after.json`.
3. Save the second run's answer line to `answer.txt` (`jq -r .result`).

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Run both commands from `app/` - the working directory is the boundary being tested.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/007-roots/app
claude -p "Read ../shared/contracts/order.json and reply with exactly one line: schema_version: <value>. If you cannot read it, reply with exactly: schema_version: unknown" --output-format json > before.json
claude -p "Read ../shared/contracts/order.json and reply with exactly one line: schema_version: <value>. If you cannot read it, reply with exactly: schema_version: unknown" --add-dir ../shared --output-format json > after.json
jq -r .result after.json > answer.txt
jq '{result, permission_denials}' before.json after.json
```

</details>

## Check your work

```bash
D=/root/mastery/007-roots/app; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
real = (load("../shared/contracts/order.json") or {}).get("schema_version")
b, a = load("before.json") or {}, load("after.json") or {}
bden = [d for d in b.get("permission_denials") or [] if d.get("tool_name") == "Read"]
ok(b.get("type") == "result" and bden and real not in (b.get("result") or ""),
   "before.json: without --add-dir the read was denied and the value never surfaced",
   "save before.json from a run WITHOUT --add-dir - its Read of ../shared should be in permission_denials")
ok(a.get("subtype") == "success" and not a.get("permission_denials") and real and real in (a.get("result") or ""),
   f"after.json: with --add-dir the agent read schema_version {real}",
   "save after.json from the same prompt run with --add-dir ../shared")
ok(text("answer.txt").strip() == f"schema_version: {real}", "answer.txt holds the one-line answer",
   f"answer.txt should be exactly 'schema_version: {real}' (jq -r .result after.json)")
ok(not os.path.exists("../shared/.claude"), "the shared folder was not turned into a project", "do not create config inside ../shared")
PYEOF
```

## What you learned

- The working directory is the default boundary; reads outside it are refused in headless runs.
- --add-dir grants file access to one more root for the session - and only that.
- Keep the before and after envelopes: they prove the grant, and only the grant, opened the boundary.
