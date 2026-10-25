---
type: task
title: "Run a task in the background and collect its artifacts"
minutes: 17
---

## Set up

Set up creates `/root/mastery/025-background/src/` with two small modules, one carrying a TODO. The folder is not a git repository, so the background session edits it in place.

```bash
rm -rf /root/mastery/025-background && mkdir -p /root/mastery/025-background/src && cd /root/mastery/025-background
cat > src/cart.py <<'EOF'
def total(items):
    # TODO: handle discounts
    return sum(items)
EOF
cat > src/ship.py <<'EOF'
def quote(kg):
    return 5 + kg * 2
EOF
```

## What to build

Dispatch an audit that runs with no terminal attached, then collect what it left behind.

1. Give the folder project settings that let the run write under `artifacts/` and deny `git push` and `curl`. Open `claude` in the folder once, answer **Yes** to "Do you trust the files in this folder?", then `/exit`. Until a folder is trusted, Claude Code ignores its project **allow** rules (deny rules always apply). On a machine with no console, the warning it prints tells you the one-line alternative - setting `hasTrustDialogAccepted` for the folder in `~/.claude.json`.
2. Dispatch it in the background, named `audit-025`, in a mode where edits in this folder need no approval:
   > Audit src/ for TODO comments. Work only inside artifacts/: append one line per step to artifacts/progress.log, write artifacts/report.md with a line `TODOs: <count>` followed by one `path:line: text` line per TODO, and write artifacts/DONE containing `ok` as your very last action. Do not ask questions.
3. Poll `claude agents --json --all` until `audit-025` is `done`, then save that output as `sessions.json` and the session's logs as `session.log`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `--bg` takes the prompt as a positional argument and cannot be combined with `-p`.
- Read the state with `jq -r '[.[] | select(.name == "audit-025")][0].state'`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/025-background
mkdir -p .claude artifacts
cat > .claude/settings.json <<'EOF'
{
  "permissions": {
    "allow": ["Edit(/artifacts/**)"],
    "deny": ["Bash(git push *)", "Bash(curl *)"]
  }
}
EOF
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
claude --bg --name audit-025 --permission-mode acceptEdits "Audit src/ for TODO comments. Work only inside artifacts/: append one line per step to artifacts/progress.log, write artifacts/report.md with a line `TODOs: <count>` followed by one `path:line: text` line per TODO, and write artifacts/DONE containing `ok` as your very last action. Do not ask questions."
for i in $(seq 1 60); do
  latest=$(claude agents --json --all | jq -c '[.[] | select(.name == "audit-025")] | sort_by(.startedAt // 0) | last // {}')
  [ "$(echo "$latest" | jq -r '.state // "missing"')" = done ] && break; sleep 5
done
claude agents --json --all > sessions.json
claude logs "$(echo "$latest" | jq -r .id)" > session.log || true
cat artifacts/report.md
```

</details>

## Check your work

```bash
D=/root/mastery/025-background; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
s = load("sessions.json") or []
me = sorted([x for x in s if isinstance(x, dict) and x.get("name") == "audit-025"], key=lambda x: x.get("startedAt") or 0, reverse=True)
ok(me and me[0].get("kind") == "background" and me[0].get("state") == "done",
   "sessions.json shows audit-025 as a finished background session",
   f"save claude agents --json --all as sessions.json after audit-025 reaches done - found {me}")
names = sorted(os.listdir("artifacts")) if os.path.isdir("artifacts") else []
ok(set(names) >= {"DONE", "progress.log", "report.md"} and not [n for n in os.listdir(".") if n not in ("artifacts", "src", ".claude", "sessions.json", "session.log")],
   "the run wrote only to artifacts/: progress.log, report.md, and DONE", f"artifacts/ should hold progress.log, report.md, DONE and nothing should be written elsewhere - artifacts: {names}")
ok(names and text("artifacts/DONE").strip() == "ok" and os.path.getmtime("artifacts/DONE") >= max(os.path.getmtime("artifacts/" + n) for n in names),
   "DONE was written last", "artifacts/DONE should contain ok and be the last file written")
ok(text("artifacts/report.md").strip() == "TODOs: 1\nsrc/cart.py:2: TODO: handle discounts", "the report counts and lists the TODO",
   "artifacts/report.md should be 'TODOs: 1' then 'src/cart.py:2: TODO: handle discounts'")
ok(len([l for l in text("artifacts/progress.log").splitlines() if l.strip()]) >= 2, "progress.log records the steps", "append one line per step to artifacts/progress.log")
PYEOF
```

## What you learned

- claude --bg dispatches a full session that outlives your terminal; claude agents shows its state.
- A run nobody watches must have its permissions settled up front, or it waits in blocked.
- Artifacts in one folder, a progress log, and a DONE marker written last make results trustworthy.
