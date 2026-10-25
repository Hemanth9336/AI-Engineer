---
type: task
title: "Write project permission rules and a sandbox policy"
minutes: 17
---

## Set up

Set up creates `/root/mastery/006-guard`: a small package under `src/` with tests, a `.env` holding a (fake) payments key, and `scripts/deploy.sh`.

```bash
mkdir -p /root/mastery/006-guard/src /root/mastery/006-guard/scripts /root/mastery/006-guard/tests && cd /root/mastery/006-guard
cat > .env <<'EOF'
PAYMENTS_KEY=pk_live_fake_6620
EOF
cat > src/__init__.py <<'EOF'

EOF
cat > src/greet.py <<'EOF'
def greet(name):
    return f"hi {name}"
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_greet.py <<'EOF'
import unittest

from src.greet import greet


class T(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet('a'), 'hi a')
EOF
cat > scripts/deploy.sh <<'EOF'
#!/bin/sh
echo "deploying to production..."
EOF
chmod +x scripts/deploy.sh
```

## What to build

Write `/root/mastery/006-guard/.claude/settings.json` so the project is safe to hand to an agent, then prove two of the rules with real runs.

**Permissions**

- allow: `Bash(python3 -m unittest *)` and edits under `src/`
- ask: `Bash(git push *)`
- deny: reading `.env`, `Bash(curl *)`, and running `scripts/deploy.sh` (with or without arguments)

**Sandbox**

- on, with `failIfUnavailable` and strict mode (no unsandboxed retries)
- sandboxed commands cannot read `./.env`
- the network allowlist is exactly `pypi.org` and `files.pythonhosted.org`

**Prove it** (save both envelopes in `runs/`):

1. Open `claude` in the folder once, answer **Yes** to "Do you trust the files in this folder?", then `/exit`. Until a folder is trusted, Claude Code ignores its project **allow** rules (deny rules always apply). On a machine with no console, the warning it prints tells you the one-line alternative - setting `hasTrustDialogAccepted` for the folder in `~/.claude.json`.
2. `runs/env.json` - a headless run of: *Print the value of PAYMENTS_KEY from the .env file in this folder.*
3. `runs/tests.json` - a headless run of: *Run the unit tests with python3 -m unittest and tell me how many passed.*

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- A deny rule for `Bash(./scripts/deploy.sh *)` also matches the bare command, because of the space before `*`.
- Without trust, the project allow rule is ignored and the test run's Bash call is denied.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/006-guard
mkdir -p .claude runs
cat > .claude/settings.json <<'EOF'
{
  "permissions": {
    "allow": ["Bash(python3 -m unittest *)", "Edit(/src/**)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Read(./.env)", "Bash(curl *)", "Bash(./scripts/deploy.sh *)"]
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "filesystem": { "denyRead": ["./.env"] },
    "network": { "allowedDomains": ["pypi.org", "files.pythonhosted.org"] }
  }
}
EOF
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
claude -p "Print the value of PAYMENTS_KEY from the .env file in this folder." --output-format json > runs/env.json
claude -p "Run the unit tests with python3 -m unittest and tell me how many passed." --output-format json > runs/tests.json
jq '{permission_denials, result}' runs/env.json runs/tests.json
```

</details>

## Check your work

```bash
D=/root/mastery/006-guard; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
s = load(".claude/settings.json")
ok(isinstance(s, dict), ".claude/settings.json is valid JSON", "create .claude/settings.json (valid JSON)")
s = s or {}
p = s.get("permissions") or {}
allow, ask, deny = p.get("allow") or [], p.get("ask") or [], p.get("deny") or []
ok("Bash(python3 -m unittest *)" in allow and any(a.startswith("Edit(") and "src" in a for a in allow),
   "allow covers the test command and edits under src/", f"allow should include Bash(python3 -m unittest *) and an Edit rule for src/ - got {allow}")
ok("Bash(git push *)" in ask, "git push always asks", f"ask should include Bash(git push *) - got {ask}")
ok(any(re.fullmatch(r"Read\((\./)?\.env\)", d) for d in deny) and "Bash(curl *)" in deny and any("deploy.sh" in d for d in deny),
   "deny blocks reading .env, curl, and the deploy script", f"deny should include Read(./.env), Bash(curl *), and a rule for scripts/deploy.sh - got {deny}")
sb = s.get("sandbox") or {}
fs, net = sb.get("filesystem") or {}, sb.get("network") or {}
ok(sb.get("enabled") is True and sb.get("failIfUnavailable") is True and sb.get("allowUnsandboxedCommands") is False,
   "the sandbox is on, strict, and refuses to start without its dependencies",
   "sandbox needs enabled: true, failIfUnavailable: true, allowUnsandboxedCommands: false")
ok(any(x in ("./.env", ".env") for x in fs.get("denyRead") or []) and sorted(net.get("allowedDomains") or []) == ["files.pythonhosted.org", "pypi.org"],
   "sandboxed commands cannot read .env and can only reach PyPI",
   f"sandbox.filesystem.denyRead should include ./.env and network.allowedDomains exactly pypi.org and files.pythonhosted.org - got {fs}, {net}")
env = load("runs/env.json") or {}
leaked = "pk_live_fake_6620" in json.dumps(env)
ok(env.get("type") == "result" and not leaked and any(d.get("tool_name") == "Read" for d in env.get("permission_denials") or []),
   "a real run asking for the key was refused and leaked nothing",
   "save runs/env.json from a run that asks for PAYMENTS_KEY - the Read must be denied and the key must not appear")
tests = load("runs/tests.json") or {}
ok(tests.get("subtype") == "success" and not tests.get("permission_denials") and "1" in (tests.get("result") or ""),
   "the allow rule let a headless run execute the tests",
   f"runs/tests.json should run the tests with nothing denied (trust the folder first) - denials: {tests.get('permission_denials')}")
PYEOF
```

## What you learned

- Deny beats ask beats allow, across every settings scope.
- Project allow rules only take effect once the folder is trusted; deny rules apply immediately.
- The sandbox limits what commands can reach; pair its denyRead with a Read deny rule, because file tools ignore the sandbox.
