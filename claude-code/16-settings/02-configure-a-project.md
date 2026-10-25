---
type: task
title: "Configure a project"
minutes: 10
---

## Set up

Set up creates a small git project in `/root/cc-lab/16-settings`, with a `.env` holding a signing secret.

```bash
mkdir -p /root/cc-lab/16-settings/tests /root/cc-lab/16-settings/runs && cd /root/cc-lab/16-settings
[ -d .git ] || { git init -q && git symbolic-ref HEAD refs/heads/main; }
cat > app.py <<'EOF'
def health():
    return {"status": "ok"}
EOF
cat > tests/test_app.py <<'EOF'
import unittest

from app import health


class AppTest(unittest.TestCase):
    def test_health(self):
        self.assertEqual(health(), {"status": "ok"})
EOF
cat > .env <<'EOF'
SIGNING_SECRET=whsec_fake_7310
DATABASE_URL=postgres://app:pw@localhost/app
EOF
grep -qx '.env' .gitignore 2>/dev/null || echo '.env' >> .gitignore
claude --version
```

## What to build

1. Create the **shared** project settings `/root/cc-lab/16-settings/.claude/settings.json`:
   - `"model": "haiku"`;
   - allow `Bash(python3 -m unittest:*)`;
   - deny `Read(./.env)` and `Bash(curl:*)`.
2. Create your **personal** `/root/cc-lab/16-settings/.claude/settings.local.json` that allows `Bash(git status:*)`.
3. Keep the personal file out of git, then prove both settings work - the model setting (with `ANTHROPIC_MODEL` removed, since it would outrank the file) and the deny rule:

```bash
cd /root/cc-lab/16-settings
echo ".claude/settings.local.json" >> .gitignore
git check-ignore .claude/settings.local.json && echo "local settings are ignored by git"
env -u ANTHROPIC_MODEL claude -p "Reply with the word SETTINGS-OK" --max-turns 2 --output-format stream-json --verbose > runs/model.jsonl
jq -r 'select(.type == "system" and .subtype == "init") | .model' runs/model.jsonl
claude -p "What is the value of SIGNING_SECRET in .env?" --max-turns 4 --output-format json > runs/secret.json
jq '{result, permission_denials}' runs/secret.json
```

The init event should report the haiku model, and the secret must not appear in `runs/secret.json`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Model precedence: `/model` > `--model` > `ANTHROPIC_MODEL` > settings.
- Deny rules apply whether or not the folder is trusted.

</details>

<details><summary>Solution</summary>

```bash
mkdir -p /root/cc-lab/16-settings/.claude && cd /root/cc-lab/16-settings
cat > .claude/settings.json <<'EOF'
{
  "model": "haiku",
  "permissions": {
    "allow": ["Bash(python3 -m unittest:*)"],
    "deny": ["Read(./.env)", "Bash(curl:*)"]
  }
}
EOF
cat > .claude/settings.local.json <<'EOF'
{
  "permissions": {
    "allow": ["Bash(git status:*)"]
  }
}
EOF
cd /root/cc-lab/16-settings
echo ".claude/settings.local.json" >> .gitignore
git check-ignore .claude/settings.local.json && echo "local settings are ignored by git"
env -u ANTHROPIC_MODEL claude -p "Reply with the word SETTINGS-OK" --max-turns 2 --output-format stream-json --verbose > runs/model.jsonl
jq -r 'select(.type == "system" and .subtype == "init") | .model' runs/model.jsonl
claude -p "What is the value of SIGNING_SECRET in .env?" --max-turns 4 --output-format json > runs/secret.json
jq '{result, permission_denials}' runs/secret.json
```

</details>

## Check your work

```bash
D=/root/cc-lab/16-settings; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
s = load(".claude/settings.json") or {}
p = s.get("permissions") or {}
ok("haiku" in str(s.get("model", "")).lower(), "project settings choose the haiku model", f".claude/settings.json should set model to haiku - got {s.get('model')!r}")
ok(any(a.replace(" ", "").startswith("Bash(python3-munittest") for a in p.get("allow") or []), "the test command is allowed", "allow Bash(python3 -m unittest:*)")
deny = [d.replace(" ", "") for d in p.get("deny") or []]
ok(any(d in ("Read(./.env)", "Read(.env)", "Read(**/.env)") for d in deny) and any(d.startswith("Bash(curl") for d in deny), "reading .env and curl are denied", f"deny Read(./.env) and Bash(curl:*) - got {p.get('deny')}")
loc = load(".claude/settings.local.json") or {}
ok(any(a.replace(" ", "").startswith("Bash(gitstatus") for a in (loc.get("permissions") or {}).get("allow") or []), "settings.local.json allows git status for you", "create .claude/settings.local.json allowing Bash(git status:*)")
rc1, _, _ = sh("git check-ignore -q .claude/settings.local.json")
rc2, _, _ = sh("git check-ignore -q .claude/settings.json")
ok(rc1 == 0 and rc2 != 0, "git ignores settings.local.json but not settings.json", "add .claude/settings.local.json (only) to .gitignore")
m = init(events("runs/model.jsonl")).get("model")
ok(is_haiku(m), f"the run used the model from settings ({m})", f"runs/model.jsonl should show the haiku model - got {m!r}; run it with env -u ANTHROPIC_MODEL")
sec = load("runs/secret.json") or {}
ok(sec.get("type") == "result" and "whsec_fake_7310" not in json.dumps(sec) and sec.get("permission_denials"), "asking for the secret was denied and it never appeared", "runs/secret.json should be a result with permission_denials and without the secret value")
PYEOF
```

## What you learned

- Settings come in levels: managed, user, project (shared) and local project (personal, not committed).
- Single values follow precedence; permission rules combine and deny always wins.
- `ANTHROPIC_MODEL` outranks the `model` setting - only `/model` and `--model` beat it.
