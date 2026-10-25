---
type: task
title: "Write the release manager spec"
minutes: 37
---

## Set up

Set up creates `/root/mastery/081-release-manager`: the pricing app (`app/pricing.py`, six tests, `VERSION` 1.1.0) as a git repo with conventional-commit history since the `v1.0.0` tag.

```bash
rm -rf /root/mastery/081-release-manager && mkdir -p /root/mastery/081-release-manager/app /root/mastery/081-release-manager/tests /root/mastery/081-release-manager/docs /root/mastery/081-release-manager/release /root/mastery/081-release-manager/.claude/hooks /root/mastery/081-release-manager/.claude/agents && cd /root/mastery/081-release-manager
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
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
git log --oneline | head -3
```

## What to build

Write `SPEC.md`, one page, with these sections. You can draft it with Claude in plan mode, but make every line yours.

- `## Goal`: one or two sentences.
- `## Users`: who reads the outputs.
- `## Inputs`.
- `## Outputs`. Name `release/out/verdict.json`, `release/out/CHANGELOG.md` and `release/out/RELEASE_NOTES.md`.
- `## Done means`: at least five `- [ ]` checklist items. Each one must be testable, so name the command, file or endpoint in backticks.
- `## Non-goals`: at least two bullets. Publishing must be one of them.
- `## Risks`: at least three bullets, each with its mitigation.

Keep it under 900 words. The spec is what the next seven steps are measured against.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- A good done-criterion names something you could check in CI: `python3 release/check.py` exits 1 when a test fails.
- Non-goals stop scope creep: say plainly that tagging and pushing stay human.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/081-release-manager
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
```

</details>

## Check your work

```bash
D=/root/mastery/081-release-manager; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
s = text("SPEC.md")
def section(name):
    m = re.search(rf"^## {name}\s*$(.*?)(?=^## |\Z)", s, re.M | re.S)
    return m[1] if m else None
need = ["Goal", "Users", "Inputs", "Outputs", "Done means", "Non-goals", "Risks"]
ok(all(section(n) is not None for n in need), "SPEC.md has all seven sections", f"add the sections: {[n for n in need if section(n) is None]}")
outs = section("Outputs") or ""
ok(all(p in outs for p in ["release/out/verdict.json", "release/out/CHANGELOG.md", "release/out/RELEASE_NOTES.md"]),
   "Outputs names the verdict, changelog, and release notes files", "name release/out/verdict.json, CHANGELOG.md, and RELEASE_NOTES.md under Outputs")
done_items = re.findall(r"^- \[ \] (.+)$", section("Done means") or "", re.M)
ok(len(done_items) >= 5 and all("`" in i for i in done_items), f"{len(done_items)} testable done-criteria, each naming a command, file, or endpoint",
   "write at least five '- [ ]' items under Done means, each with something in backticks")
ng = re.findall(r"^- (.+)$", section("Non-goals") or "", re.M)
ok(len(ng) >= 2 and any(re.search(r"publish|push|tag", i, re.I) for i in ng), "Non-goals keep publishing out of scope", "list at least two non-goals, including publishing (tag/push)")
ok(len(re.findall(r"^- .+$", section("Risks") or "", re.M)) >= 3, "at least three risks", "list at least three risks with mitigations")
ok(len(s.split()) <= 900, f"one page ({len(s.split())} words)", f"cut it to 900 words or fewer - it has {len(s.split())}")
PYEOF
```

## What you learned

- A spec's 'done means' section is a list of checks, each naming a command, file, or endpoint you can test.
- Non-goals (publishing stays human) and risks with mitigations shape the design before any code exists.
