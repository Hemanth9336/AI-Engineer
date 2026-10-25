---
type: task
title: "Write the design doc"
minutes: 37
---

## Set up

Set up creates `/root/mastery/082-release-manager` with the app, its history, and the reference `SPEC.md` from step 081. It's rebuilt from the reference solution of every earlier capstone step, so a mistake earlier doesn't block you. To keep building on your own work instead, copy your files from the earlier step's folder over the top.

```bash
rm -rf /root/mastery/082-release-manager && mkdir -p /root/mastery/082-release-manager/app /root/mastery/082-release-manager/tests /root/mastery/082-release-manager/docs /root/mastery/082-release-manager/release /root/mastery/082-release-manager/.claude/hooks /root/mastery/082-release-manager/.claude/agents && cd /root/mastery/082-release-manager
g() { git -c user.name="Release Lab" -c user.email=lab@example.com "$@"; }
git init -q -b main
cat > app/pricing.py <<'EOF'
"""Pricing rules for the shop."""
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def _money(x):
    return Decimal(str(x)).quantize(CENT, rounding=ROUND_HALF_UP)


def apply_discount(total, pct):
    """Return total after a pct% discount, rounded half-up to the cent."""
    if not 0 <= pct <= 100:
        raise ValueError("pct must be between 0 and 100")
    return _money(Decimal(str(total)) * (100 - Decimal(str(pct))) / 100)


def tax(total, rate_pct):
    """Return the tax on total at rate_pct percent."""
    return _money(Decimal(str(total)) * Decimal(str(rate_pct)) / 100)


def bulk_price(unit, qty):
    """Unit price times qty, with 5% off for 10 or more items."""
    gross = Decimal(str(unit)) * qty
    return apply_discount(gross, 5) if qty >= 10 else _money(gross)
EOF
touch app/__init__.py tests/__init__.py
cat > tests/test_pricing.py <<'EOF'
import unittest
from decimal import Decimal

from app.pricing import apply_discount, bulk_price, tax


class PricingTest(unittest.TestCase):
    def test_discount(self):
        self.assertEqual(apply_discount(100, 15), Decimal("85.00"))

    def test_discount_rounds_half_up(self):
        self.assertEqual(apply_discount("0.05", 50), Decimal("0.03"))

    def test_discount_range(self):
        with self.assertRaises(ValueError):
            apply_discount(10, 120)

    def test_tax(self):
        self.assertEqual(tax(200, 8), Decimal("16.00"))

    def test_bulk_discount_from_ten(self):
        self.assertEqual(bulk_price(2, 10), Decimal("19.00"))

    def test_no_bulk_discount_below_ten(self):
        self.assertEqual(bulk_price(2, 9), Decimal("18.00"))
EOF
cat > .gitignore <<'EOF'
release/out/
__pycache__/
.claude/settings.local.json
EOF
echo 1.0.0 > VERSION
echo '# Pricing rules' > docs/pricing.md
git add -A && g commit -qm "chore: initial project" && g tag v1.0.0
echo '- Orders of 10 or more items get 5% off.' >> docs/pricing.md && git add -A && g commit -qm "feat: add bulk pricing for 10+ items"
echo '- Discounts round half-up to the cent.' >> docs/pricing.md && git add -A && g commit -qm "fix: round discounts half-up to the cent"
echo '- See app/pricing.py docstrings for each rule.' >> docs/pricing.md && git add -A && g commit -qm "docs: document pricing rules"
echo '- tax(total, rate_pct) takes 8 for 8%.' >> docs/pricing.md && git add -A && g commit -qm "feat!: tax rates are percentages, not fractions"
echo 1.1.0 > VERSION && git add -A && g commit -qm "chore: prepare 1.1.0"
cat > SPEC.md <<'EOF'
# Release manager - spec

## Goal
Decide, for the current commit of the pricing app, whether it can be released, and produce everything a human needs to press the button: a verdict, a changelog, and release notes.

## Users
- The on-call engineer who cuts the release.
- The support lead who reads the release notes.

## Inputs
- The git repository (history since the last tag, and `VERSION`).
- The test suite in `tests/`.

## Outputs
- `release/out/verdict.json`: go, no-go, or error, plus test counts, version, and commit.
- `release/out/CHANGELOG.md`: conventional commits since the last tag, grouped.
- `release/out/RELEASE_NOTES.md`: the verdict, customer-facing notes, and known issues.
- `release/out/activity.jsonl` and `release/out/guard.jsonl`: what the agents did and what was blocked.
- `GET /verdict` on `127.0.0.1:8787`, serving the current verdict.

## Done means
- [ ] `python3 release/check.py` exits 0 and writes verdict `go` on a green suite, and exits 1 with `no-go` when any test fails.
- [ ] `python3 release/changelog.py` groups every commit since the last tag into Breaking changes, Features, Fixes, and Other.
- [ ] `release/coordinate.sh` produces `RELEASE_NOTES.md` whose verdict always comes from `verdict.json`, never from a worker.
- [ ] Agents can't `git push`, `git tag`, `rm -rf`, or modify `tests/` - the guard denies it and logs to `guard.jsonl`.
- [ ] `curl 127.0.0.1:8787/verdict` returns the current verdict, and 503 when there is none.
- [ ] A seeded regression is found and fixed by the agent with the suite going from red to green and `tests/` unchanged.

## Non-goals
- Publishing: tagging, pushing, and uploading stay human steps.
- Deciding *what* goes into a release - it reports on the commit it is given.
- Any network access beyond the local model gateway.

## Risks
- An agent "fixes" the suite by editing tests - mitigated by the guard and a test hash.
- A worker hallucinates changes in the notes - mitigated by deriving notes only from the changelog file.
- A stale verdict is served after a failed run - mitigated by writing the verdict on every run, atomically.
EOF
chmod +x release/*.py release/*.sh .claude/hooks/*.py 2>/dev/null || true
git add -A && g commit -qm "chore: add release manager tooling"
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
git log --oneline | head -3
```

## What to build

Write `DESIGN.md` with:

1. `## Components`: a Markdown table with the columns `Component | Kind | Reads | Writes`, one row for each of the eight components (exact names): release check runner, changelog generator, activity hook, triage worker, notes worker, coordinator, guard, verdict endpoint. `Kind` is `script` or `agent`.
2. `## Tool choices`: why the agents are agents, and which tools they get.
3. `## Data flow`: how `verdict.json` and `CHANGELOG.md` move through the system to `RELEASE_NOTES.md`.
4. `## Failure modes`: at least three bullets, each saying what the system *does* when that thing breaks.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Only two components need judgement over text. Everything else has one right answer.
- Write failure modes as 'X happens: the system does Y', for example 'a worker leaves no file: the coordinator exits 2'.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/082-release-manager
cat > DESIGN.md <<'EOF'
# Release manager - design

## Components

| Component | Kind | Reads | Writes |
|---|---|---|---|
| release check runner | script | `tests/`, `VERSION`, git HEAD | `release/out/verdict.json`, `release/out/test-output.txt` |
| changelog generator | script | git history since the last tag | `release/out/CHANGELOG.md` |
| activity hook | script | PostToolUse events | `release/out/activity.jsonl` |
| triage worker | agent | `verdict.json`, `test-output.txt` | `release/out/triage.json` |
| notes worker | agent | `CHANGELOG.md` | `release/out/notes-draft.md` |
| coordinator | script | every file above | `release/out/RELEASE_NOTES.md` |
| guard | script | PreToolUse events | allow or deny, `release/out/guard.jsonl` |
| verdict endpoint | script | `verdict.json` | HTTP responses on 127.0.0.1:8787 |

## Tool choices
Everything that must be exact - running tests, counting failures, grouping commits, merging files, blocking commands, serving JSON - is a script: cheap, deterministic, testable. Agents get the two jobs that need judgement over text: explaining failures and writing for customers. Workers get Read and Write only.

## Data flow
`check.py` -> `verdict.json` + `test-output.txt` -> triage worker -> `triage.json`.
`changelog.py` -> `CHANGELOG.md` -> notes worker -> `notes-draft.md`.
`coordinate.sh` runs both scripts, both workers in parallel, then `merge_notes.py` -> `RELEASE_NOTES.md`. The endpoint reads `verdict.json` on every request.

## Failure modes
- Test runner crashes or prints no summary: verdict `error`, exit 2, never `go`.
- A worker fails or leaves no artifact: the coordinator exits 2 and writes no notes.
- Triage disagrees with the verdict: the verdict wins, the notes carry a warning, exit 1.
- An agent tries a blocked command: the guard denies with a reason the agent sees, and logs it.
EOF
```

</details>

## Check your work

```bash
D=/root/mastery/082-release-manager; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
s = text("DESIGN.md")
EXPECT = {"release check runner": "script", "changelog generator": "script", "activity hook": "script", "triage worker": "agent", "notes worker": "agent", "coordinator": "script", "guard": "script", "verdict endpoint": "script"}
rows = {}
for line in s.splitlines():
    cells = [c.strip().strip("`*").lower() for c in line.strip().strip("|").split("|")]
    if len(cells) >= 4 and cells[0] in EXPECT:
        rows[cells[0]] = cells[1]
ok(set(rows) == set(EXPECT), "the components table has all eight components", f"missing rows: {sorted(set(EXPECT) - set(rows))}")
wrong = {k: v for k, v in rows.items() if v != EXPECT[k]}
ok(rows and not wrong, "every component has the right kind (two agents, six scripts)", f"reconsider: {wrong}")
ok(re.search(r"^\| *Component *\| *Kind *\| *Reads *\| *Writes *\|", s, re.M | re.I), "the table has Component, Kind, Reads, and Writes columns", "use the header | Component | Kind | Reads | Writes |")
def section(name):
    m = re.search(rf"^## {name}\s*$(.*?)(?=^## |\Z)", s, re.M | re.S)
    return m[1] if m else ""
df = section("Data flow")
ok("verdict.json" in df and "CHANGELOG.md" in df and "RELEASE_NOTES.md" in df, "Data flow traces verdict.json and CHANGELOG.md to RELEASE_NOTES.md", "describe the data flow through those files")
ok(len(section("Tool choices").split()) >= 20, "Tool choices explains the agent decisions", "explain why the agents are agents and what tools they get")
ok(len(re.findall(r"^- .+$", section("Failure modes"), re.M)) >= 3, "at least three failure modes", "list at least three failure modes and what the system does")
PYEOF
```

## What you learned

- Make a component an agent only when it needs judgement over text; everything with one right answer is a script.
- A components table whose reads/writes columns are files is the interface spec for the whole build.
