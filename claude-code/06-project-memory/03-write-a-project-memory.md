---
type: task
title: "Write a project memory"
minutes: 9
---

## Set up

Set up creates `billing-svc` in `/root/cc-lab/06-memory`. Its README says almost nothing - the conventions only exist in people's heads, until now.

```bash
mkdir -p /root/cc-lab/06-memory/billing /root/cc-lab/06-memory/tests /root/cc-lab/06-memory/scripts /root/cc-lab/06-memory/migrations && cd /root/cc-lab/06-memory
cat > billing/__init__.py <<'EOF'

EOF
cat > billing/invoice.py <<'EOF'
def line_total_cents(unit_cents, qty):
    return unit_cents * qty


def invoice_total_cents(lines, tax_rate_bp):
    """lines: [(unit_cents, qty)], tax_rate_bp: tax in basis points (2000 = 20%)."""
    subtotal = sum(line_total_cents(u, q) for u, q in lines)
    return subtotal + (subtotal * tax_rate_bp + 5000) // 10000
EOF
cat > tests/test_invoice.py <<'EOF'
import unittest

from billing.invoice import invoice_total_cents


class InvoiceTest(unittest.TestCase):
    def test_total_with_tax(self):
        self.assertEqual(invoice_total_cents([(1999, 2), (500, 1)], 2000), 5398)


if __name__ == "__main__":
    unittest.main()
EOF
cat > scripts/test.sh <<'EOF'
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
python3 -m unittest discover -s tests -q
EOF
cat > migrations/001_init.sql <<'EOF'
CREATE TABLE invoices (id INTEGER PRIMARY KEY, total_cents INTEGER NOT NULL);
EOF
cat > README.md <<'EOF'
# billing-svc

Invoices for Stackline customers.
EOF
chmod +x scripts/test.sh
claude --version
```

## What to build

1. Write `/root/cc-lab/06-memory/CLAUDE.md` **by hand** (40 lines at most) with these sections:
   - `## Commands` - the test command is `./scripts/test.sh`;
   - `## Conventions` - money is stored as **integer cents**, never floats (add any other conventions you can see in `billing/invoice.py`);
   - `## Do not` - never edit files in `migrations/`; add a new migration instead.
2. Prove Claude reads it - ask a question only CLAUDE.md can answer:

```bash
cd /root/cc-lab/06-memory
claude -p "In two short lines: which command runs this project's tests, and how must money amounts be stored?" > memory-check.txt
cat memory-check.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The README doesn't mention the test script or cents - if the answer has them, they came from CLAUDE.md.
- Section headings must be exactly `## Commands`, `## Conventions` and `## Do not`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/06-memory
cat > CLAUDE.md <<'EOF'
# billing-svc

Invoice maths for Stackline customers. Python 3, standard library only.

## Commands
- Run all tests: `./scripts/test.sh`
- Run one test file: `python3 -m unittest tests.test_invoice`

## Conventions
- Money is always stored and computed as integer cents, never floats. Format to currency only when displaying.
- Tax rates are basis points (2000 = 20%). Round half up with integer maths.
- New code goes in `billing/`; every public function gets a test in `tests/`.

## Do not
- Never edit files in `migrations/` - add a new numbered migration instead.
- Don't add third-party dependencies without asking.
EOF
claude -p "In two short lines: which command runs this project's tests, and how must money amounts be stored?" > memory-check.txt
cat memory-check.txt
```

</details>

## Check your work

```bash
D=/root/cc-lab/06-memory; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
md = text("CLAUDE.md")
secs, cur = {}, None
for line in md.splitlines():
    m = re.match(r"^##\s+(.+?)\s*$", line)
    if m:
        cur = m.group(1).strip().lower()
        secs[cur] = ""
    elif cur:
        secs[cur] += line + "\n"
ok(md and len(md.splitlines()) <= 40, f"CLAUDE.md exists and is short ({len(md.splitlines())} lines)", "write CLAUDE.md in /root/cc-lab/06-memory, 40 lines at most")
ok("./scripts/test.sh" in secs.get("commands", ""), "## Commands gives ./scripts/test.sh", "add ./scripts/test.sh under '## Commands'")
ok("cents" in secs.get("conventions", "").lower(), "## Conventions says money is integer cents", "say under '## Conventions' that money is stored as integer cents")
ok("migrations" in secs.get("do not", ""), "## Do not protects migrations/", "say under '## Do not' never to edit migrations/")
ok(not re.search(r"sk-[A-Za-z0-9_-]{8,}|password\s*[:=]", md, re.I), "CLAUDE.md holds no secrets", "remove secrets from CLAUDE.md - it is committed and sent to the model")
ans = text("memory-check.txt").lower()
ok("scripts/test.sh" in ans and "cent" in ans, "Claude answered from CLAUDE.md: ./scripts/test.sh and integer cents", f"memory-check.txt should mention scripts/test.sh and cents - got {ans.strip()[:200]!r}")
ok(ran(r"which command runs this project's tests"), "the question was asked in a session in this folder", "run the claude -p question from inside /root/cc-lab/06-memory")
PYEOF
```

## What you learned

- CLAUDE.md is loaded into every session in the project - the place for commands, conventions and don'ts.
- Short, specific bullets beat generic advice; never put secrets in it.
- Test your memory file by asking a question only it can answer.
