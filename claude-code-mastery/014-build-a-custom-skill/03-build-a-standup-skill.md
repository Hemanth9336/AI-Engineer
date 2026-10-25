---
type: task
title: "Build a standup skill"
minutes: 23
---

## Set up

Set up creates a git repo at `/root/mastery/014-standup` with three commits from the last few hours and one from two weeks ago.

```bash
rm -rf /root/mastery/014-standup && mkdir -p /root/mastery/014-standup && cd /root/mastery/014-standup
git init -q && git symbolic-ref HEAD refs/heads/main
git config user.email dev@example.com && git config user.name 'Dev Lab'
echo "0" >> log.txt && git add log.txt && T="@$(( $(date +%s) - 1209600 )) +0000" && GIT_AUTHOR_DATE="$T" GIT_COMMITTER_DATE="$T" git commit -q -m "chore: bump lockfile"
echo "1" >> log.txt && git add log.txt && T="@$(( $(date +%s) - 10800 )) +0000" && GIT_AUTHOR_DATE="$T" GIT_COMMITTER_DATE="$T" git commit -q -m "feat: add CSV export for invoices"
echo "2" >> log.txt && git add log.txt && T="@$(( $(date +%s) - 7200 )) +0000" && GIT_AUTHOR_DATE="$T" GIT_COMMITTER_DATE="$T" git commit -q -m "fix: correct VAT rounding on credit notes"
echo "3" >> log.txt && git add log.txt && T="@$(( $(date +%s) - 3600 )) +0000" && GIT_AUTHOR_DATE="$T" GIT_COMMITTER_DATE="$T" git commit -q -m "docs: describe the export endpoint"
```

## What to build

Write a project skill at `/root/mastery/014-standup/.claude/skills/standup/SKILL.md` that turns the last day of git history into a standup.

- Frontmatter with a description that says what it writes and when to use it.
- The commits arrive through **dynamic context**: a `` !`git log --since=... ` `` line, not an instruction to go look.
- Output exactly three sections: `Yesterday:` (one bullet per commit), `Today:`, `Blockers:`.

Run it headless as `/standup` and save the envelope as `standup.json`. The two-week-old commit must not appear.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `--pretty=format:"- %s"` prints one subject per line, ready to use as bullets.
- If the run aborts with a permission error, pre-approve the command: `allowed-tools: Bash(git log *)`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/014-standup
mkdir -p .claude/skills/standup
cat > .claude/skills/standup/SKILL.md <<'EOF'
---
description: Writes a standup report from the last day of git commits. Use when the user asks for a standup, a daily update, or what they did yesterday.
allowed-tools: Bash(git log *)
---

## Commits from the last day

!`git log --since="1 day ago" --pretty=format:"- %s"`

## Instructions

Write a standup report from the commits above in exactly this format:

Yesterday:
- one line per commit, in plain words
Today:
- one line: the most likely next step
Blockers:
- none, unless a commit message mentions one
EOF
claude -p "/standup" --output-format json > standup.json
jq -r .result standup.json
```

</details>

## Check your work

```bash
D=/root/mastery/014-standup; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

s = text(".claude/skills/standup/SKILL.md")
fm = re.match(r"---\n(.*?)\n---\n", s, re.S)
ok(fm and re.search(r"(?m)^description: .*standup", fm.group(1), re.I), "SKILL.md starts with frontmatter whose description names standups",
   "create .claude/skills/standup/SKILL.md starting with --- frontmatter and a description that mentions standups")
ok(re.search(r"!`git log [^`]*--since", s), "the skill injects real git history with !`git log --since ...`",
   "inline the commits with a !`git log --since=...` line so the data arrives with the instructions")
env = load("standup.json") or {}
f, rows = transcript(env.get("session_id") or "none")
body = "\n".join(b.get("text", "") for r in rows if r.get("type") == "user" for b in content(r) if b.get("type") == "text")
ok("/standup" in body and "fix: correct VAT rounding on credit notes" in body and "chore: bump lockfile" not in body,
   "the run invoked /standup and the injected log held only the last day's commits",
   "run claude -p \"/standup\" - the transcript should show the last day's commit subjects injected, not the 2-week-old one")
r = env.get("result") or ""
secs = [l for l in r.splitlines() if l.rstrip(":") in ("Yesterday", "Today", "Blockers")]
yest = r.split("Yesterday:")[-1].split("Today:")[0] if "Yesterday:" in r else ""
ok(secs == ["Yesterday:", "Today:", "Blockers:"] and yest.count("\n- ") + yest.startswith("- ") >= 3 and "lockfile" not in r.lower(),
   "the report has Yesterday, Today, Blockers and covers the three recent commits",
   f"the result should have Yesterday:/Today:/Blockers: with three Yesterday bullets - got {r!r}")
PYEOF
```

## What you learned

- SKILL.md = frontmatter (description is the trigger) + procedural instructions.
- !`command` injects live data before Claude reads the skill; allowed-tools pre-approves it.
- Test a skill by name, by description, and on edge cases.
