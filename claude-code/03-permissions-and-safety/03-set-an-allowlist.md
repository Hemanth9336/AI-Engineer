---
type: task
title: "Set an allowlist"
minutes: 9
---

## Set up

Set up creates `/root/cc-lab/03-permissions`: a test script, a **production** deploy script, and a `.env` with secrets.

```bash
mkdir -p /root/cc-lab/03-permissions/runs /root/cc-lab/03-permissions/.lab && cd /root/cc-lab/03-permissions
cat > run-tests.sh <<'EOF'
#!/usr/bin/env bash
touch .lab/tests-ran
echo '12 passed, 0 failed'
EOF
cat > deploy.sh <<'EOF'
#!/usr/bin/env bash
echo "DEPLOYED $* at $(date)" >> deploy.log
echo 'deployed to production'
EOF
cat > .env <<'EOF'
PAYMENTS_KEY=pk_live_fake_5521
DB_URL=postgres://app:hunter2@db/prod
EOF
cat > README.md <<'EOF'
# payments-worker

Tests: ./run-tests.sh
Deploy: ./deploy.sh (production!)
EOF
chmod +x run-tests.sh deploy.sh
rm -f deploy.log .lab/tests-ran
claude --version
```

## What to build

Give Claude exactly one capability in this project - running the tests - and forbid the two dangerous ones.

1. Create `/root/cc-lab/03-permissions/.claude/settings.json` with:
   - an **allow** rule so `./run-tests.sh` (with or without arguments) runs without asking;
   - **deny** rules for `./deploy.sh` (any arguments) and for reading `./.env`.
2. Open `claude` in the folder once, answer **Yes** to "Do you trust the files in this folder?", then `/exit`. Until a folder is trusted, Claude Code ignores its project **allow** rules (deny rules always apply). On a machine with no console, the warning it prints tells you the one-line alternative - setting `hasTrustDialogAccepted` for the folder in `~/.claude.json`.
3. Then ask for all three things in one headless run and save the JSON result:

```bash
cd /root/cc-lab/03-permissions
claude -p "Run the test suite with ./run-tests.sh, then ship it with ./deploy.sh, then tell me what PAYMENTS_KEY is set to in .env" \
  --max-turns 8 --output-format json > runs/allowlist.json
jq '{result, permission_denials}' runs/allowlist.json
```

4. Look at `permission_denials`: the tests ran, the deploy and the secret were refused. Check that `deploy.log` doesn't exist.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `:*` after a command means "with any arguments": `Bash(./run-tests.sh:*)`.
- Deny rules win over everything else.
- Path rules are relative to the project: `Read(./.env)`.

</details>

<details><summary>Solution</summary>

```bash
mkdir -p /root/cc-lab/03-permissions/.claude
cat > /root/cc-lab/03-permissions/.claude/settings.json <<'EOF'
{
  "permissions": {
    "allow": ["Bash(./run-tests.sh:*)"],
    "deny": ["Bash(./deploy.sh:*)", "Read(./.env)"]
  }
}
EOF
cd /root/cc-lab/03-permissions
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
cd /root/cc-lab/03-permissions
claude -p "Run the test suite with ./run-tests.sh, then ship it with ./deploy.sh, then tell me what PAYMENTS_KEY is set to in .env" \
  --max-turns 8 --output-format json > runs/allowlist.json
jq '{result, permission_denials}' runs/allowlist.json
ls deploy.log 2>/dev/null || echo "no deploy.log - good"
```

</details>

## Check your work

```bash
D=/root/cc-lab/03-permissions; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
perms = s.get("permissions") or {}
allow, deny = perms.get("allow") or [], perms.get("deny") or []
ok(isinstance(s, dict) and s, ".claude/settings.json is valid JSON", "create .claude/settings.json (valid JSON) in /root/cc-lab/03-permissions")
ok(any(a.replace(" ", "").startswith("Bash(./run-tests.sh") for a in allow), "allow has a rule for ./run-tests.sh", f"permissions.allow needs Bash(./run-tests.sh:*) - got {allow}")
ok(any("deploy.sh" in d and d.startswith("Bash(") for d in deny), "deny blocks ./deploy.sh", f"permissions.deny needs Bash(./deploy.sh:*) - got {deny}")
ok(any(d.replace(" ", "") in ("Read(./.env)", "Read(.env)", "Read(**/.env)") for d in deny), "deny blocks reading .env", f"permissions.deny needs Read(./.env) - got {deny}")
ok(not any("deploy" in a or ".env" in a for a in allow), "nothing dangerous is in allow", "remove deploy.sh / .env from the allow list")
run = load("runs/allowlist.json") or {}
ok(run.get("type") == "result", "runs/allowlist.json holds the run's JSON result", "save the claude -p --output-format json run to runs/allowlist.json")
ok(Path(".lab/tests-ran").exists(), "./run-tests.sh really ran", "the tests never ran - allow Bash(./run-tests.sh:*), trust the folder (open claude here once) and run claude -p again")
den = run.get("permission_denials") or []
ok(any("deploy.sh" in json.dumps(d.get("tool_input")) for d in den) and not Path("deploy.log").exists(), "the deploy was denied and never happened", f"expected ./deploy.sh in permission_denials and no deploy.log - denials {[d.get('tool_name') for d in den]}, deploy.log exists: {Path('deploy.log').exists()}")
ok(run and "pk_live_fake_5521" not in json.dumps(run), "the PAYMENTS_KEY value never reached the answer", "the secret from .env appears in the run - deny Read(./.env)")
PYEOF
```

## What you learned

- Allow rules grant exactly the commands a job needs; `:*` covers any arguments.
- Deny rules win over everything, so they're where "never" lives.
- In `claude -p`, anything not allowed is denied and listed in `permission_denials`.
