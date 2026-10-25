---
type: task
title: "Build the coordinator and worker agents"
minutes: 37
---

## Set up

Set up creates `/root/mastery/085-release-manager` with the app and the reference spec, design, check runner, activity hook, and changelog generator. It's rebuilt from the reference solution of every earlier capstone step, so a mistake earlier doesn't block you. To keep building on your own work instead, copy your files from the earlier step's folder over the top.

```bash
rm -rf /root/mastery/085-release-manager && mkdir -p /root/mastery/085-release-manager/app /root/mastery/085-release-manager/tests /root/mastery/085-release-manager/docs /root/mastery/085-release-manager/release /root/mastery/085-release-manager/.claude/hooks /root/mastery/085-release-manager/.claude/agents && cd /root/mastery/085-release-manager
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
cat > release/check.py <<'EOF'
#!/usr/bin/env python3
"""check.py - run the test suite and write release/out/verdict.json. Exit 0 = go, 1 = no-go, 2 = could not check."""
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "release" / "out"


def git_head():
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def write(verdict):
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "verdict.json.tmp"
    tmp.write_text(json.dumps(verdict, indent=2) + "\n")
    tmp.replace(OUT / "verdict.json")


def main():
    version = ROOT / "VERSION"
    base = {"version": version.read_text().strip() if version.exists() else None, "commit": git_head(),
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    if not (ROOT / "tests").is_dir():
        write({**base, "verdict": "error", "reason": "no tests/ directory"})
        return 2
    try:
        r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        write({**base, "verdict": "error", "reason": "the test suite timed out"})
        return 2
    out = r.stdout + r.stderr
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "test-output.txt").write_text(out)
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    if not ran:
        write({**base, "verdict": "error", "reason": "could not read the test summary"})
        return 2
    failed = int((re.search(r"failures=(\d+)", out) or [0, 0])[1])
    errors = int((re.search(r"errors=(\d+)", out) or [0, 0])[1])
    n = int(ran[1])
    go = r.returncode == 0 and n > 0 and failed == 0 and errors == 0
    write({**base, "verdict": "go" if go else "no-go", "tests": {"ran": n, "failed": failed, "errors": errors}})
    return 0 if go else 1


if __name__ == "__main__":
    sys.exit(main())
EOF
cat > .claude/settings.json <<'EOF'
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/activity.py"
          }
        ]
      }
    ]
  }
}
EOF
cat > .claude/hooks/activity.py <<'EOF'
#!/usr/bin/env python3
"""PostToolUse hook: append one JSON line per tool call to release/out/activity.jsonl. Never blocks the agent."""
import datetime
import json
import os
import sys
from pathlib import Path

try:
    ev = json.load(sys.stdin)
except ValueError:
    sys.exit(0)
inp = ev.get("tool_input") or {}
target = inp.get("file_path") or inp.get("command") or inp.get("pattern") or inp.get("url") or ""
out = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ev.get("cwd") or ".") / "release" / "out"
out.mkdir(parents=True, exist_ok=True)
line = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "session": ev.get("session_id"), "tool": ev.get("tool_name"), "target": str(target)[:200]}
with open(out / "activity.jsonl", "a") as f:
    f.write(json.dumps(line) + "\n")
EOF
cat > release/changelog.py <<'EOF'
#!/usr/bin/env python3
"""changelog.py [--since REF] - group conventional commits since the last tag into release/out/CHANGELOG.md."""
import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = [("breaking", "Breaking changes"), ("feat", "Features"), ("fix", "Fixes"), ("other", "Other")]
SKIP = {"chore", "ci", "build", "style", "test"}
CONVENTIONAL = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?: (?P<desc>.+)$")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="tag or commit to start after (default: the latest tag)")
    since = ap.parse_args().since
    if since is None:
        try:
            since = git("describe", "--tags", "--abbrev=0").strip()
        except subprocess.CalledProcessError:
            since = None
    log = git("log", f"{since}..HEAD" if since else "HEAD", "--format=%s%x1f%b%x1e")
    groups = {key: [] for key, _ in SECTIONS}
    for record in log.split("\x1e"):
        if not record.strip():
            continue
        subject, _, body = record.strip("\n").partition("\x1f")
        m = CONVENTIONAL.match(subject.strip())
        if not m:
            groups["other"].append(subject.strip())
            continue
        desc = f"**{m['scope']}:** {m['desc'].strip()}" if m["scope"] else m["desc"].strip()
        if m["bang"] or "BREAKING CHANGE:" in body:
            groups["breaking"].append(desc)
        elif m["type"] in ("feat", "fix"):
            groups[m["type"]].append(desc)
        elif m["type"] not in SKIP:
            groups["other"].append(desc)
    version = (ROOT / "VERSION").read_text().strip() if (ROOT / "VERSION").exists() else "unreleased"
    lines = [f"## {version}", ""]
    for key, title in SECTIONS:
        if groups[key]:
            lines += [f"### {title}", *[f"- {d}" for d in reversed(groups[key])], ""]
    if len(lines) == 2:
        lines += ["No user-facing changes.", ""]
    out = ROOT / "release" / "out"
    out.mkdir(parents=True, exist_ok=True)
    (out / "CHANGELOG.md").write_text("\n".join(lines).rstrip() + "\n")
    print("\n".join(lines).rstrip())


if __name__ == "__main__":
    main()
EOF
chmod +x release/*.py release/*.sh .claude/hooks/*.py 2>/dev/null || true
git add -A && g commit -qm "chore: add release manager tooling"
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
git log --oneline | head -3
```

## What to build

1. Write two project agents, each with `tools: Read, Write` only.
   - `.claude/agents/triage.md` (`name: triage`): reads `release/out/verdict.json` and `test-output.txt`, and writes `release/out/triage.json` as `{"status", "failing", "summary"}`. Its body starts with "You are the release triage worker."
   - `.claude/agents/notes.md` (`name: notes`): reads `release/out/CHANGELOG.md` and writes customer-facing `release/out/notes-draft.md`, breaking changes first. Its body starts with "You are the release notes worker."
2. Write `release/merge_notes.py`. It writes `release/out/RELEASE_NOTES.md` containing:
   - `# Release <version>`.
   - `**Verdict: GO**` (or `NO-GO` / `ERROR`, taken from `verdict.json`) with the test counts and short commit.
   - A warning line if triage's status disagrees.
   - The notes draft.
   - `## Known issues`, listing triage's failing tests, or "None found by the release check."

   It exits 0 only for go with agreement.
3. Write `release/coordinate.sh`.
   - Clear the old outputs.
   - Run `check.py` (exit 2 means stop with 2) and `changelog.py`.
   - Run both workers in parallel: `claude -p ... --agent <name> --permission-mode acceptEdits --max-turns 6 --output-format json`, saving each envelope.
   - `wait`, then verify both artifacts (exit 2 if either is missing).
   - Merge.
4. Run `release/coordinate.sh`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `claude -p "Triage the release check." --agent triage` runs the session as that agent, using its body as the system prompt and its tools list.
- Take the verdict line from verdict.json, even when triage.json says otherwise.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/085-release-manager
cat > .claude/agents/triage.md <<'EOF'
---
name: triage
description: Read the release check output and say whether the release can go and what is failing.
tools: Read, Write
---
You are the release triage worker. Read release/out/verdict.json and release/out/test-output.txt.
Write release/out/triage.json as {"status": "go" | "no-go" | "error", "failing": ["test id", ...], "summary": "one sentence"}.
Use the verdict file's verdict as the status. List each failing or erroring test id from the output. Do not edit any other file.
EOF
cat > .claude/agents/notes.md <<'EOF'
---
name: notes
description: Turn the changelog into short customer-facing release notes.
tools: Read, Write
---
You are the release notes worker. Read release/out/CHANGELOG.md and write release/out/notes-draft.md:
a two-sentence summary for customers, then the changes as plain-language bullets, breaking changes first.
Only describe changes that are in the changelog. Do not edit any other file.
EOF
cat > release/coordinate.sh <<'EOF'
#!/usr/bin/env bash
# coordinate.sh - run the deterministic steps, fan out to the triage and notes workers, and merge into release/out/RELEASE_NOTES.md
# Exit 0 = go, 1 = no-go (notes still written), 2 = something in the pipeline broke.
set -uo pipefail
cd "$(dirname "$0")/.."
OUT=release/out
mkdir -p "$OUT" && rm -f "$OUT"/triage.json "$OUT"/notes-draft.md "$OUT"/RELEASE_NOTES.md

python3 release/check.py > /dev/null; rc=$?
[ "$rc" -le 1 ] || { echo "release check could not run (exit $rc)" >&2; exit 2; }
python3 release/changelog.py > /dev/null || { echo "changelog generator failed" >&2; exit 2; }

worker() {  # worker AGENT PROMPT
  claude -p "$2" --agent "$1" --permission-mode acceptEdits --max-turns 6 --output-format json \
    < /dev/null > "$OUT/$1.envelope.json" 2> "$OUT/$1.err"
}
worker triage "Triage the release check." & p_triage=$!
worker notes "Draft the release notes." & p_notes=$!

fail=0
wait "$p_triage" || { echo "triage worker failed" >&2; fail=1; }
wait "$p_notes" || { echo "notes worker failed" >&2; fail=1; }
jq -e '.status' "$OUT/triage.json" > /dev/null 2>&1 || { echo "triage worker left no valid triage.json" >&2; fail=1; }
[ -s "$OUT/notes-draft.md" ] || { echo "notes worker left no notes-draft.md" >&2; fail=1; }
[ "$fail" = 0 ] || exit 2

python3 release/merge_notes.py
EOF
cat > release/merge_notes.py <<'EOF'
#!/usr/bin/env python3
"""merge_notes.py - combine verdict.json, triage.json and notes-draft.md into release/out/RELEASE_NOTES.md.
Exit 0 = go, 1 = not go, or the triage worker disagrees with the release check."""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"
verdict = json.loads((OUT / "verdict.json").read_text())
triage = json.loads((OUT / "triage.json").read_text())
notes = (OUT / "notes-draft.md").read_text().strip()
t = verdict.get("tests") or {}
lines = [f"# Release {verdict.get('version')}", "",
         f"**Verdict: {verdict['verdict'].upper()}** (tests: {t.get('ran', 0)} ran, {t.get('failed', 0)} failed, "
         f"{t.get('errors', 0)} errors; commit {(verdict.get('commit') or 'unknown')[:7]})", ""]
agree = triage.get("status") == verdict["verdict"]
if not agree:
    lines += [f"> Warning: the triage worker reported `{triage.get('status')}`, but the release check says "
              f"`{verdict['verdict']}`. The release check wins.", ""]
lines += [notes, "", "## Known issues", ""]
lines += [f"- {f}" for f in triage.get("failing") or []] or ["- None found by the release check."]
(OUT / "RELEASE_NOTES.md").write_text("\n".join(lines) + "\n")
print(OUT / "RELEASE_NOTES.md")
sys.exit(0 if verdict["verdict"] == "go" and agree else 1)
EOF
chmod +x release/coordinate.sh release/merge_notes.py
release/coordinate.sh; echo "exit $?"
cat release/out/RELEASE_NOTES.md
```

</details>

## Check your work

```bash
D=/root/mastery/085-release-manager; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def stub(t, body):
    b = Path(t, "bin"); b.mkdir(exist_ok=True)
    p = b / "claude"; p.write_text("#!/usr/bin/env bash\n" + body + "\n"); p.chmod(0o755)
    return {"PATH": f"{b}:{os.environ['PATH']}"}
import shutil
def clone(t):
    dst = Path(t, "p")
    shutil.copytree(".", dst, ignore=shutil.ignore_patterns("out", "__pycache__"))
    return dst

notes = text("release/out/RELEASE_NOTES.md")
ok(notes.startswith("# Release 1.1.0") and "**Verdict: GO**" in notes and "6 ran, 0 failed, 0 errors" in notes,
   "RELEASE_NOTES.md: release 1.1.0, verdict GO with the test counts", f"run release/coordinate.sh - got {notes[:200]!r}")
draft = text("release/out/notes-draft.md").strip()
ok(draft and draft in notes and "## Known issues" in notes and "None found by the release check." in notes,
   "the notes worker's draft and an empty Known issues list are merged in", "merge notes-draft.md and a Known issues section")
tri = load("release/out/triage.json") or {}
ok(tri.get("status") == "go" and (load("release/out/triage.envelope.json") or {}).get("type") == "result" and (load("release/out/notes.envelope.json") or {}).get("type") == "result",
   "both workers ran headless and left their artifacts and envelopes", "save each worker's --output-format json envelope as release/out/<agent>.envelope.json")
def fm(p):
    s = text(p); return s.split("---")[1] if s.startswith("---") else ""
for a in ("triage", "notes"):
    f = fm(f".claude/agents/{a}.md")
    tools = set(re.findall(r"\w+", (re.search(r"^tools:(.*)$", f, re.M) or [None, ""])[1]))
    ok(re.search(rf"^name:\s*{a}\s*$", f, re.M) and tools == {"Read", "Write"}, f"the {a} agent is limited to Read and Write", f"give .claude/agents/{a}.md 'name: {a}' and 'tools: Read, Write'")
src = text("release/coordinate.sh")
ok("--agent" in src and src.count("&") >= 2 and "wait" in src, "coordinate.sh runs the workers with --agent, in parallel, and waits", "start both workers with & and wait for each")
with tempfile.TemporaryDirectory() as t:
    p = clone(t); o = p / "release/out"; o.mkdir(parents=True)
    (o / "verdict.json").write_text(json.dumps({"version": "9.9.9", "commit": "abcdef123456", "verdict": "no-go", "tests": {"ran": 6, "failed": 1, "errors": 0}}))
    (o / "triage.json").write_text(json.dumps({"status": "go", "failing": ["tests.test_pricing.PricingTest.test_tax"], "summary": "fine"}))
    (o / "notes-draft.md").write_text("Draft notes.")
    rc, so_, se = sh([sys.executable, "release/merge_notes.py"], cwd=p)
    n = text(o / "RELEASE_NOTES.md")
    ok(rc == 1 and "**Verdict: NO-GO**" in n and "abcdef1" in n and "test_tax" in n and re.search(r"warning", n, re.I),
       "hidden merge: when triage says go but the check says no-go, the check wins, a warning is added, and the exit is 1", f"got exit {rc}: {n[:300]!r}")
with tempfile.TemporaryDirectory() as t:
    p = clone(t)
    rc, so_, se = sh(["bash", "release/coordinate.sh"], cwd=p, env=stub(t, 'echo \'{"type":"result","subtype":"success","is_error":false}\''), timeout=300)
    ok(rc == 2 and not (p / "release/out/RELEASE_NOTES.md").exists(), "workers that leave no artifacts: the coordinator exits 2 and writes no notes", f"verify both artifacts before merging - exit {rc}")
PYEOF
```

## What you learned

- Define workers once in .claude/agents/ - run them headless with --agent, or delegate to them as subagents interactively.
- The coordinator verifies every worker artifact and merges with code; facts like the verdict come from scripts, never from a worker.
