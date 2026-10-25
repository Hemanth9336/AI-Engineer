---
type: task
title: "Refactor with Claude Code and keep the instructions portable"
minutes: 17
---

## Scenario

Half the team uses Claude Code, half uses Codex. The rules live in a Claude-only `CLAUDE.md`, so Codex users never see them. You will move the rules where both tools read them, give both tools the same guardrails, and prove the setup with a real refactor.

## Set up

Set up creates a git repo at `/root/mastery/037-portable`: a billing module with the same line calculation copied into two functions, a test suite, and a Claude-only `CLAUDE.md` holding the team's four rules.

```bash
rm -rf /root/mastery/037-portable && mkdir -p /root/mastery/037-portable/billing /root/mastery/037-portable/tests && cd /root/mastery/037-portable
git init -q -b main && git config user.name 'Lab Learner' && git config user.email learner@lab.invalid
cat > CLAUDE.md <<'EOF'
# Billing service

- Run the tests with `python3 -m unittest -q`.
- Money is integer cents everywhere. Never use float for money.
- Keep public function signatures unchanged; refactors must not break callers.
- Never push; open a pull request instead.
EOF
cat > billing/__init__.py <<'EOF'

EOF
cat > billing/invoice.py <<'EOF'
TAX_RATE_BP = 2500  # basis points: 25.00%


def invoice_total(items):
    total = 0
    for item in items:
        line = item["unit_cents"] * item["qty"]
        if item.get("taxable", True):
            line += (line * TAX_RATE_BP + 5000) // 10000
        total += line
    return total


def invoice_lines(items):
    out = []
    for item in items:
        line = item["unit_cents"] * item["qty"]
        if item.get("taxable", True):
            line += (line * TAX_RATE_BP + 5000) // 10000
        out.append(f"{item['sku']}: {line}")
    return out
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_invoice.py <<'EOF'
import unittest

from billing.invoice import invoice_lines, invoice_total

ITEMS = [{"sku": "A", "unit_cents": 1999, "qty": 3}, {"sku": "B", "unit_cents": 250, "qty": 4, "taxable": False}]


class InvoiceTest(unittest.TestCase):
    def test_total(self):
        self.assertEqual(invoice_total(ITEMS), 8496)

    def test_lines(self):
        self.assertEqual(invoice_lines(ITEMS), ["A: 7496", "B: 1000"])

    def test_empty(self):
        self.assertEqual(invoice_total([]), 0)
EOF
python3 -m unittest -q && git add -A && git commit -qm 'billing service' && echo 'seeded repo at commit' $(git rev-parse --short HEAD)
```

## What to build

1. Create `AGENTS.md` with the four rules from `CLAUDE.md` (the test command, integer cents, unchanged signatures, never push). Replace `CLAUDE.md` with an `@AGENTS.md` import followed by a `## Claude Code only` section. Don't copy any shared rule into `CLAUDE.md`.
2. Give both tools the same guardrails:
   - `.claude/settings.json`: allow `Bash(python3 -m unittest *)`, deny `Bash(git push *)`.
   - `.codex/config.toml`: `sandbox_mode = "workspace-write"`, `approval_policy = "on-request"`.
   - `.codex/rules/default.rules`: a `forbidden` `prefix_rule` for `git push` with a `justification` and `match` / `not_match` examples, plus an `allow` rule for `python3 -m unittest`. If Codex is installed, test it with `codex execpolicy check`.
3. Trust the folder. Then prove the import reaches Claude: run `claude -p 'What does your project say about money? Quote the rule exactly.'` with JSON output, saved as `rules-check.json`.
4. Run the refactor headless, allowing only `Read` and `Edit` on the command line, and save `refactor.json`:
   > Refactor billing/invoice.py: extract the duplicated line calculation into one private helper _line_cents(item) that both public functions use. Follow the project instructions, then run the tests.
5. Run the tests yourself, then commit everything in one commit.

The checker validates both tools' configs, recomputes the invoice on rounding edge cases against the original code, and reads the refactor transcript.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Claude Code ignores AGENTS.md whenever a CLAUDE.md exists - the import is what keeps both.
- The rules file is Starlark: Python syntax, one prefix_rule(...) call per rule.
- If Claude never runs the tests, the folder is not trusted yet, so the project allow rule is inactive.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/037-portable
cat > AGENTS.md <<'EOF'
# Billing service

Instructions for any coding agent working in this repository.

- Run the tests with `python3 -m unittest -q`.
- Money is integer cents everywhere. Never use float for money.
- Keep public function signatures unchanged; refactors must not break callers.
- Never push; open a pull request instead.
EOF
cat > CLAUDE.md <<'EOF'
@AGENTS.md

## Claude Code only
- Use the Edit tool for code changes; do not rewrite files with shell redirection.
EOF
mkdir -p .claude .codex/rules
cat > .claude/settings.json <<'EOF'
{
  "permissions": {
    "allow": ["Bash(python3 -m unittest *)"],
    "deny": ["Bash(git push *)"]
  }
}
EOF
cat > .codex/config.toml <<'EOF'
# Codex project config - loads once the project is trusted
sandbox_mode = "workspace-write"   # writes inside the repo only; network off
approval_policy = "on-request"     # ask before stepping outside the sandbox
EOF
cat > .codex/rules/default.rules <<'EOF'
# Codex command rules (Starlark). The strictest matching decision wins.
prefix_rule(
    pattern = ["git", "push"],
    decision = "forbidden",
    justification = "Never push; open a pull request instead.",
    match = ["git push origin main", "git push --force"],
    not_match = ["git status", "git log --oneline"],
)

prefix_rule(
    pattern = ["python3", "-m", "unittest"],
    decision = "allow",
    justification = "The test suite is safe to run.",
    match = ["python3 -m unittest -q"],
)
EOF
if command -v codex >/dev/null; then
  codex execpolicy check --pretty --rules .codex/rules/default.rules -- git push origin main
else
  echo "codex not installed - the checker validates the rule file itself"
fi
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
claude -p 'What does your project say about money? Quote the rule exactly.' --output-format json < /dev/null > rules-check.json
jq -r .result rules-check.json
claude -p 'Refactor billing/invoice.py: extract the duplicated line calculation into one private helper _line_cents(item) that both public functions use. Follow the project instructions, then run the tests.' --allowedTools Read Edit --output-format json < /dev/null > refactor.json
jq -r .result refactor.json
python3 -m unittest -q
git add -A && git commit -qm 'refactor: extract _line_cents; share instructions through AGENTS.md'
git show --stat --oneline HEAD
```

</details>

## Check your work

```bash
D=/root/mastery/037-portable; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def transcript(sid):
    for f in glob.glob(os.path.expanduser(f"~/.claude/projects/*/{sid}.jsonl")):
        rows = []
        for line in open(f, errors="replace"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
        return f, rows
    return None, []
def rtext(b):
    c = b.get("content")
    return c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))
def result_for(rows, pred):
    ids = [u["id"] for u in uses(rows) if pred(u)]
    return [b for b in results(rows) if b.get("tool_use_id") in ids]
INV = 'TAX_RATE_BP = 2500  # basis points: 25.00%\n\n\ndef invoice_total(items):\n    total = 0\n    for item in items:\n        line = item["unit_cents"] * item["qty"]\n        if item.get("taxable", True):\n            line += (line * TAX_RATE_BP + 5000) // 10000\n        total += line\n    return total\n\n\ndef invoice_lines(items):\n    out = []\n    for item in items:\n        line = item["unit_cents"] * item["qty"]\n        if item.get("taxable", True):\n            line += (line * TAX_RATE_BP + 5000) // 10000\n        out.append(f"{item[\'sku\']}: {line}")\n    return out'

import ast
ag, cl = text("AGENTS.md"), text("CLAUDE.md")
need = ["python3 -m unittest -q", "integer cents", "signatures", "never push"]
ok(all(n in ag.lower() for n in need), "AGENTS.md holds the four shared rules", f"AGENTS.md should hold the test command, the money rule, the signatures rule, and the no-push rule - missing {[n for n in need if n not in ag.lower()]}")
ok("@AGENTS.md" in [l.strip() for l in cl.splitlines()], "CLAUDE.md imports AGENTS.md with an @AGENTS.md line", "CLAUDE.md needs a line that is exactly @AGENTS.md")
ok(cl and "integer cents" not in cl.lower() and "unittest" not in cl, "no shared rule is copied into CLAUDE.md", "keep shared rules only in AGENTS.md - CLAUDE.md should import them, not repeat them")
s = load(".claude/settings.json") or {}
p = s.get("permissions") or {}
ok("Bash(python3 -m unittest *)" in (p.get("allow") or []) and "Bash(git push *)" in (p.get("deny") or []),
   "Claude settings allow the tests and deny git push", ".claude/settings.json should allow Bash(python3 -m unittest *) and deny Bash(git push *)")
try:
    import tomllib
    cx = tomllib.loads(text(".codex/config.toml"))
except Exception as e:
    cx = {"error": str(e)}
ok(cx.get("sandbox_mode") == "workspace-write" and cx.get("approval_policy") == "on-request",
   "Codex config: workspace-write sandbox, on-request approvals", f".codex/config.toml should set sandbox_mode = \"workspace-write\" and approval_policy = \"on-request\" - got {cx}")
rl = []
def prefix_rule(pattern, decision="allow", justification=None, match=(), not_match=()):
    rl.append({"pattern": pattern, "decision": decision, "justification": justification, "match": list(match), "not_match": list(not_match)})
try:
    exec(compile(text(".codex/rules/default.rules") or "", "default.rules", "exec"), {"prefix_rule": prefix_rule})
except Exception as e:
    print(f"   (.codex/rules/default.rules did not load: {e})")
def hits(pattern, cmd):
    a = cmd.split()
    return len(a) >= len(pattern) and all((x in p) if isinstance(p, list) else x == p for p, x in zip(pattern, a))
push = [r for r in rl if r["decision"] == "forbidden" and hits(r["pattern"], "git push origin main") and not hits(r["pattern"], "git status")]
ok(push and push[0]["justification"], "a forbidden prefix_rule for git push, with a justification", "add prefix_rule(pattern = [\"git\", \"push\"], decision = \"forbidden\", justification = ...) to .codex/rules/default.rules")
ok(push and push[0]["match"] and push[0]["not_match"], "the push rule carries match and not_match examples", "give the push rule match and not_match examples - Codex checks them when the rules load")
bad = [m for r in rl for m in r["match"] if not hits(r["pattern"], m)] + [m for r in rl for m in r["not_match"] if hits(r["pattern"], m)]
ok(rl and not bad, "every match / not_match example agrees with its pattern", f"these examples contradict their rule's pattern: {bad}")
env = load("rules-check.json") or {}
ok("integer cents" in str(env.get("result", "")).lower(), "Claude quoted the money rule - the import reached it",
   f"rules-check.json should quote the money rule from AGENTS.md - got {str(env.get('result'))[:150]!r}")
src = text("billing/invoice.py")
try:
    tree = ast.parse(src)
except SyntaxError:
    tree = ast.parse("")
fns = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
calls = lambda f: {c.func.id for c in ast.walk(f) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
ok("_line_cents" in fns and all("_line_cents" in calls(fns[f]) for f in ("invoice_total", "invoice_lines") if f in fns),
   "_line_cents exists and both public functions call it", "define _line_cents(item) and call it from invoice_total and invoice_lines")
ok(src.count("TAX_RATE_BP + 5000") == 1, "the tax calculation now appears once", f"the tax expression should appear exactly once - found {src.count('TAX_RATE_BP + 5000')}")
sig = {f: [a.arg for a in fns[f].args.args] for f in ("invoice_total", "invoice_lines") if f in fns}
ok(sig == {"invoice_total": ["items"], "invoice_lines": ["items"]}, "public signatures are unchanged", f"invoice_total(items) and invoice_lines(items) must keep their signatures - got {sig}")
ok("float" not in src and not any(isinstance(n, ast.Constant) and isinstance(n.value, float) for n in ast.walk(tree)), "money stays integer cents (no floats)", "the refactor introduced a float - money must stay integer cents")
probe = [{"sku": "X", "unit_cents": 333, "qty": 3}, {"sku": "Y", "unit_cents": 1, "qty": 1}, {"sku": "Z", "unit_cents": 999, "qty": 2, "taxable": False}, {"sku": "W", "unit_cents": 2, "qty": 1}]
ref = {}
exec(INV, ref)
want = [ref["invoice_total"](probe), ref["invoice_lines"](probe)]
rc, out, err = sh([sys.executable, "-c", "import json, sys; from billing.invoice import invoice_total, invoice_lines; p = json.loads(sys.argv[1]); print(json.dumps([invoice_total(p), invoice_lines(p)]))", json.dumps(probe)])
ok(rc == 0 and out.strip() and json.loads(out) == want, "behavior matches the original on rounding edge cases", f"the refactor changed behavior: expected {want}, got {out.strip() or err.strip()[-200:]}")
rc, out, err = sh("python3 -m unittest -q")
ok(rc == 0, "the test suite passes", "python3 -m unittest -q fails:\n" + err[-400:])
env = load("refactor.json") or {}
f, rows = transcript(env.get("session_id") or "none")
ed = result_for(rows, lambda u: u.get("name") in ("Edit", "MultiEdit") and (u.get("input") or {}).get("file_path", "").endswith("billing/invoice.py"))
ok(ed and not all(b.get("is_error") for b in ed), "the refactor was done by Claude with the Edit tool", "refactor.json should come from a claude -p run that edited billing/invoice.py with Edit")
tst = result_for(rows, lambda u: u.get("name") == "Bash" and "python3 -m unittest" in (u.get("input") or {}).get("command", ""))
ok(tst and not tst[-1].get("is_error"), "Claude ran the tests itself, allowed by the project rule", "Claude should run python3 -m unittest -q during the refactor (the settings allow rule needs a trusted folder)")
rc, log, _ = sh("git log --format=%s")
rc2, files, _ = sh("git show --name-only --format= HEAD")
ok(len(log.split(chr(10))) >= 2 and "billing/invoice.py" in files and "AGENTS.md" in files, "the refactor and AGENTS.md are committed together",
   "commit the refactor with AGENTS.md, CLAUDE.md, and the configs (git add -A && git commit)")
PYEOF
```

## What you learned

- AGENTS.md as the single source of shared rules, with CLAUDE.md importing it, keeps Claude Code and Codex in step.
- One guardrail, two dialects: a Claude deny rule, and a Codex sandbox plus a forbidden prefix_rule.
- A refactor is accepted on evidence: tests, an edge-case behavior check, and a reviewed commit.
