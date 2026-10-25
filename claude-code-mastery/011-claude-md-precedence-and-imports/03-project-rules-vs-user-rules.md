---
type: task
title: "Project rules vs user rules"
minutes: 23
---

## Set up

Set up creates `/root/mastery/011-levels/CHANGELOG.md` and adds a personal rule to `~/.claude/CLAUDE.md`: sign changelog summaries with `-- summarized by hm`.

```bash
mkdir -p /root/mastery/011-levels/docs ~/.claude && cd /root/mastery/011-levels
cat > CHANGELOG.md <<'EOF'
# Changelog
## 2.4.0
- Added CSV export for invoices
- Fixed timezone bug in monthly reports
- Dropped Python 3.8 support
EOF
grep -qF -- '-- summarized by hm' ~/.claude/CLAUDE.md 2>/dev/null || cat >> ~/.claude/CLAUDE.md <<'EOF'
# My preferences
- When you summarize a changelog, sign it on a new line with `-- summarized by hm`.
EOF
```

## What to build

Your personal rule is fine for your own notes, but the release channel needs a team format. Override it from the project, without deleting it, and keep the style rule in its own file.

1. Create `docs/summary-style.md` with the rule that every summary starts with `SUMMARY:` followed by one sentence.
2. Create the project `CLAUDE.md` that **imports** that file and requires ending every summary with `Reviewed-by: release-bot` **instead of** any personal signature.
3. Run this headless and save the envelope as `run.json`:
   > Summarize CHANGELOG.md for the release channel.

The checker reads both instruction files, confirms your user rule is untouched, and inspects the run.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- An import is `@docs/summary-style.md` on its own line - not inside backticks.
- Say explicitly that the project signature replaces the personal one; conflicting rules with no tie-breaker can go either way.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/011-levels
cat > docs/summary-style.md <<'EOF'
# Summary style
- Every summary starts with `SUMMARY:` followed by one sentence.
EOF
cat > CLAUDE.md <<'EOF'
# release-notes

## Summaries
@docs/summary-style.md
- In this project, end every summary with the line `Reviewed-by: release-bot` instead of any personal signature.
EOF
claude -p "Summarize CHANGELOG.md for the release channel." --output-format json > run.json
jq -r .result run.json
```

</details>

## Check your work

```bash
D=/root/mastery/011-levels; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
ok("-- summarized by hm" in text(os.path.expanduser("~/.claude/CLAUDE.md")), "your user-level rule is still in ~/.claude/CLAUDE.md",
   "keep the personal signature rule in ~/.claude/CLAUDE.md - the point is to override it from the project, not delete it")
c, st = text("CLAUDE.md"), text("docs/summary-style.md")
ok("SUMMARY:" in st and re.search(r"(?m)^(?!\s*`).*@docs/summary-style\.md", c) and "SUMMARY:" not in c,
   "the project CLAUDE.md imports docs/summary-style.md instead of copying it",
   "put the SUMMARY: rule in docs/summary-style.md and import it from CLAUDE.md with @docs/summary-style.md (not inside backticks)")
ok("Reviewed-by: release-bot" in c and re.search(r"instead|override|rather than|not .*personal", c, re.I),
   "the project rule explicitly overrides personal signatures", "CLAUDE.md should require 'Reviewed-by: release-bot' and say it replaces any personal signature")
r = (load("run.json") or {}).get("result") or ""
lines = [l for l in r.strip().splitlines() if l.strip()]
ok(lines and lines[0].startswith("SUMMARY:") and lines[-1].strip() == "Reviewed-by: release-bot" and "-- summarized by hm" not in r,
   "the run followed the imported style and the project signature, not the personal one",
   f"run.json should start with SUMMARY:, end with Reviewed-by: release-bot, and not contain your personal signature - got {r!r}")
PYEOF
```

## What you learned

- Managed, user, project, and local instruction files all load; they are combined, not replaced.
- Conflicts have no guaranteed winner - write the specific rule so it explicitly overrides.
- @path imports keep one source of truth; they organize but do not reduce context.
