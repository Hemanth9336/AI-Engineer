---
type: task
title: "Prove skill selection"
minutes: 17
---

## Set up

Set up creates `/root/mastery/049-skills`:
- `CHANGELOG.md`.
- A `changelog-entry` skill whose description is `Helps with docs.` and whose body is a long style guide pasted inline.
- `cases.json`: three requests that should fire the skill, and one nearby question that shouldn't.

```bash
rm -rf /root/mastery/049-skills && mkdir -p /root/mastery/049-skills/.claude/skills/changelog-entry && cd /root/mastery/049-skills
cat > CHANGELOG.md <<'EOF'
# Changelog

## [Unreleased]

### Added
- Export reports to CSV

## [1.4.0] - 2026-09-30

### Fixed
- Login no longer loops on expired sessions
EOF
cat > .claude/skills/changelog-entry/SKILL.md <<'EOF'
---
name: changelog-entry
description: Helps with docs.
---
# Changelog entries

When someone needs a changelog entry, follow this guide carefully and edit CHANGELOG.md by hand.

## Entry style

- One line per change, written for the person using the product, not the person who wrote the code.
- Start with what changed for them: "Uploads resume after a dropped connection", not "Refactor retry loop".
- Present tense, no trailing period, no ticket numbers in the text.
- Name the feature the user sees, not the module.

## Types

| Type | Use for |
|---|---|
| Added | New features |
| Changed | Changes to existing behavior |
| Fixed | Bug fixes |
| Removed | Features taken out |

Security fixes go under Fixed and start with "Security:".

## Examples

| Commit message | Entry |
|---|---|
| fix(upload): retry chunk on ECONNRESET | Fixed: Uploads resume after a dropped connection |
| feat(export): add CSV writer | Added: Export reports to CSV |
| chore: drop py3.8 | Removed: Support for Python 3.8 |
| fix(auth): constant-time token compare | Fixed: Security: Session tokens are compared in constant time |

## Placement

Entries go under `## [Unreleased]`, in a `### <Type>` subsection. Create the subsection if it doesn't exist yet. Never edit a released version's section.
EOF
cat > cases.json <<'EOF'
[
  {
    "prompt": "Add a changelog entry for the retry fix in the uploader.",
    "expect": "changelog-entry"
  },
  {
    "prompt": "Write a release note saying uploads now resume after a dropped connection.",
    "expect": "changelog-entry"
  },
  {
    "prompt": "Record the timeout bug fix under Unreleased.",
    "expect": "changelog-entry"
  },
  {
    "prompt": "What is the difference between a changelog and git log?",
    "expect": null
  }
]
EOF
wc -l .claude/skills/changelog-entry/SKILL.md
```

## What to build

1. Write `prove.sh` and make it executable.
   - For each case in `cases.json`, run `claude -p "<prompt>" --output-format stream-json --verbose < /dev/null` and save the stream as `runs/<i>.jsonl`.
   - Take the first `Skill` tool call's `input.skill`, stripping any `plugin:` prefix, or `null` if no skill was called.
   - Write `selection.json`: each case plus `got` and `pass` (`got == expect`).
   - Print `<passed>/<total> cases as expected`, and exit 1 unless every case passes.
2. Run it on the original skill and keep the evidence: `cp selection.json selection-before.json`.
3. Rewrite the skill in `.claude/skills/changelog-entry/`:
   - **Description**: lead with what it does, name the phrases users say (changelog entry, release note, Unreleased), and add a `Not for ...` boundary. Stay under the 1,536-character cap.
   - **Progressive disclosure**: move the guide into `style.md`, and keep `SKILL.md` to 40 lines or fewer with a link to `style.md`.
   - **Script**: add `scripts/add_entry.py <Added|Changed|Fixed|Removed> "<text>" [CHANGELOG.md]`.
     - It inserts `- <text>` (no trailing period) under `## [Unreleased]` / `### <Type>`, creating the subsection if needed.
     - It exits 2 on an unknown type and 1 when there is no Unreleased section.
     - Reference it in the body and in `allowed-tools` through `${CLAUDE_SKILL_DIR}`.
4. Run `./prove.sh` again: `4/4 cases as expected`. Then run `claude plugin validate .`.

The checker deletes your boundary sentence in a copy of the project and expects `prove.sh` to catch the over-trigger. It also tests `add_entry.py` on changelogs you haven't seen.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq -r '... | select(.type == "tool_use" and .name == "Skill") | .input.skill'` pulls the decision out of the stream.
- The listing line is `- name: description` - only that line decides selection, so the body's wording doesn't help triggering.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/049-skills
cat > prove.sh <<'EOF'
#!/usr/bin/env bash
# prove.sh - run every case in cases.json headless, record which skill Claude invoked, exit 1 on any mismatch.
set -u
cd "$(dirname "$0")"
mkdir -p runs
n=$(jq length cases.json)
echo '[]' > selection.json
for i in $(seq 0 $((n - 1))); do
  prompt=$(jq -r ".[$i].prompt" cases.json)
  claude -p "$prompt" --output-format stream-json --verbose < /dev/null > "runs/$i.jsonl" || true
  got=$(jq -r 'select(.type == "assistant") | .message.content[]? | select(.type == "tool_use" and .name == "Skill") | .input.skill' "runs/$i.jsonl" | head -1)
  jq --slurpfile cases cases.json --argjson i "$i" --arg got "$got" \
    '. + [$cases[0][$i] + {got: (if $got == "" then null else ($got | sub("^.*:"; "")) end)} | . + {pass: (.got == .expect)}]' \
    selection.json > selection.tmp && mv selection.tmp selection.json
done
passed=$(jq '[.[] | select(.pass)] | length' selection.json)
echo "$passed/$n cases as expected"
[ "$passed" -eq "$n" ]
EOF
chmod +x prove.sh
./prove.sh || true
cp selection.json selection-before.json
mkdir -p .claude/skills/changelog-entry/scripts
cat > .claude/skills/changelog-entry/SKILL.md <<'EOF'
---
name: changelog-entry
description: Adds a changelog entry or release note to CHANGELOG.md under the Unreleased section (Added, Changed, Fixed, Removed). Use when asked to add a changelog entry, write a release note, or record a change under Unreleased. Not for general questions about changelogs or git history.
allowed-tools: Read Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/add_entry.py *)
---
# Changelog entry

1. Pick the type: Added, Changed, Fixed, or Removed. The rules and examples are in [style.md](style.md); read it when the type or wording is unclear.
2. Write one line for the user of the product: what changed for them, not how.
3. Insert it with the script, never by hand:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/add_entry.py <Type> "<entry text>"`
4. Show the user the line you added and the section it went into.
EOF
cat > .claude/skills/changelog-entry/style.md <<'EOF'
## Entry style

- One line per change, written for the person using the product, not the person who wrote the code.
- Start with what changed for them: "Uploads resume after a dropped connection", not "Refactor retry loop".
- Present tense, no trailing period, no ticket numbers in the text.
- Name the feature the user sees, not the module.

## Types

| Type | Use for |
|---|---|
| Added | New features |
| Changed | Changes to existing behavior |
| Fixed | Bug fixes |
| Removed | Features taken out |

Security fixes go under Fixed and start with "Security:".

## Examples

| Commit message | Entry |
|---|---|
| fix(upload): retry chunk on ECONNRESET | Fixed: Uploads resume after a dropped connection |
| feat(export): add CSV writer | Added: Export reports to CSV |
| chore: drop py3.8 | Removed: Support for Python 3.8 |
| fix(auth): constant-time token compare | Fixed: Security: Session tokens are compared in constant time |

## Placement

Entries go under `## [Unreleased]`, in a `### <Type>` subsection. Create the subsection if it doesn't exist yet. Never edit a released version's section.
EOF
cat > .claude/skills/changelog-entry/scripts/add_entry.py <<'EOF'
#!/usr/bin/env python3
"""add_entry.py <Added|Changed|Fixed|Removed> "<text>" [CHANGELOG.md] - add one bullet under ## [Unreleased] / ### <Type>."""
import sys

TYPES = ("Added", "Changed", "Fixed", "Removed")


def main(argv):
    if len(argv) not in (3, 4) or argv[1] not in TYPES or not argv[2].strip():
        print(f"usage: add_entry.py <{'|'.join(TYPES)}> \"<text>\" [CHANGELOG.md]", file=sys.stderr)
        return 2
    kind, entry = argv[1], argv[2].strip().rstrip(".")
    path = argv[3] if len(argv) == 4 else "CHANGELOG.md"
    lines = open(path).read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip().lower() == "## [unreleased]")
    except StopIteration:
        print(f"{path} has no ## [Unreleased] section", file=sys.stderr)
        return 1
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    head = next((i for i in range(start + 1, end) if lines[i].strip() == f"### {kind}"), None)
    if head is None:
        block = [f"### {kind}", f"- {entry}", ""]
        at = end
        while at > start + 1 and not lines[at - 1].strip():
            at -= 1
        lines[at:at] = [""] + block if lines[at - 1].strip() else block
    else:
        at = head + 1
        while at < end and lines[at].startswith("- "):
            at += 1
        lines.insert(at, f"- {entry}")
    open(path, "w").write("\n".join(lines).rstrip("\n") + "\n")
    print(f"{kind}: {entry}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
EOF
chmod +x .claude/skills/changelog-entry/scripts/add_entry.py
./prove.sh
claude plugin validate .
```

</details>

## Check your work

```bash
D=/root/mastery/049-skills; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def frontmatter(p):
    s = text(p)
    if not s.startswith("---\n"):
        return None, s
    end = s.find("\n---", 4)
    if end < 0:
        return None, s
    try:
        import yaml
        meta = yaml.safe_load(s[4:end]) or {}
    except Exception:
        meta = None
    return meta, s[end + 4:].lstrip("\n")
CASES = [{'prompt': 'Add a changelog entry for the retry fix in the uploader.', 'expect': 'changelog-entry'}, {'prompt': 'Write a release note saying uploads now resume after a dropped connection.', 'expect': 'changelog-entry'}, {'prompt': 'Record the timeout bug fix under Unreleased.', 'expect': 'changelog-entry'}, {'prompt': 'What is the difference between a changelog and git log?', 'expect': None}]
CHANGELOG = '# Changelog\n\n## [Unreleased]\n\n### Added\n- Export reports to CSV\n\n## [1.4.0] - 2026-09-30\n\n### Fixed\n- Login no longer loops on expired sessions\n'
STYLE_HEADS = ['## Entry style', '## Types', '## Examples', '## Placement']

import shutil
SK = ".claude/skills/changelog-entry"
meta, body = frontmatter(f"{SK}/SKILL.md")
ok(isinstance(meta, dict), "SKILL.md frontmatter parses as YAML", "SKILL.md needs YAML frontmatter starting on line 1 that parses (claude plugin validate . shows the error)")
meta = meta if isinstance(meta, dict) else {}
desc = " ".join(str(meta.get(k) or "") for k in ("description", "when_to_use")).strip()
low = desc.lower()
ok(meta.get("name", "changelog-entry") == "changelog-entry", "the skill is still named changelog-entry", "keep name: changelog-entry (cases.json expects it)")
ok(40 <= len(desc) <= 1536, f"description + when_to_use is {len(desc)} characters, inside the 1,536 cap",
   f"description + when_to_use should be a real sentence or two and at most 1,536 characters - got {len(desc)}")
miss = [k for k in ("changelog", "release note", "unreleased") if k not in low]
ok(not miss, "the description names the phrases users say: changelog, release note, Unreleased", f"the description never mentions {miss}")
ok("not for" in low, "the description states its boundary ('Not for ...')", "add a 'Not for ...' boundary so related questions don't fire the skill")
lines = text(f"{SK}/SKILL.md").splitlines()
ok(len(lines) <= 40 and "## Examples" not in body, f"SKILL.md is {len(lines)} lines - the style guide moved out", f"keep SKILL.md to 40 lines or fewer; move the style guide to style.md (now {len(lines)} lines)")
st = text(f"{SK}/style.md")
ok(all(h in st for h in STYLE_HEADS) and "style.md" in body, "style.md holds the full guide and SKILL.md points to it",
   "move the guide (all four sections) into style.md next to SKILL.md and link it from the body")
ok("${CLAUDE_SKILL_DIR}/scripts/add_entry.py" in body and "${CLAUDE_SKILL_DIR}/scripts/add_entry.py" in str(meta.get("allowed-tools", "")),
   "the body and allowed-tools both reference ${CLAUDE_SKILL_DIR}/scripts/add_entry.py", "point to the script with ${CLAUDE_SKILL_DIR} in the body, and pre-approve the same command in allowed-tools")
script = os.path.abspath(f"{SK}/scripts/add_entry.py")
def run_add(log, *args):
    with tempfile.TemporaryDirectory() as t:
        Path(t, "CHANGELOG.md").write_text(log)
        rc, out, err = sh([sys.executable, script, *args], cwd=t)
        return rc, Path(t, "CHANGELOG.md").read_text()
def section(log, kind):
    ls = log.splitlines()
    s = next((i for i, l in enumerate(ls) if l.strip().lower() == "## [unreleased]"), None)
    if s is None:
        return None
    e = next((i for i in range(s + 1, len(ls)) if ls[i].startswith("## ")), len(ls))
    h = next((i for i in range(s + 1, e) if ls[i].strip() == f"### {kind}"), None)
    if h is None:
        return None
    out = []
    for l in ls[h + 1:e]:
        if not l.startswith("- "):
            break
        out.append(l[2:])
    return out
rc, log = run_add(CHANGELOG, "Added", "Dark mode")
ok(rc == 0 and section(log, "Added") == ["Export reports to CSV", "Dark mode"] and "## [1.4.0]" in log,
   "add_entry.py appends to an existing subsection", f"add_entry.py Added 'Dark mode' should append under ### Added in Unreleased - rc {rc}")
rc, log = run_add(CHANGELOG, "Fixed", "Uploads resume after a dropped connection.")
rel = log.split("## [1.4.0]")[1] if "## [1.4.0]" in log else ""
ok(rc == 0 and section(log, "Fixed") == ["Uploads resume after a dropped connection"] and sum(l.startswith("- ") for l in rel.splitlines()) == 1,
   "it creates a missing ### Fixed inside Unreleased (never in a released section) and drops the trailing period",
   f"add_entry.py Fixed should create ### Fixed under Unreleased, leave 1.4.0 alone, and strip the trailing period - rc {rc}")
rc, log = run_add(CHANGELOG, "Deprecated", "x")
rc2, _ = run_add("# Changelog\n\n## [1.0.0]\n", "Added", "x")
ok(rc == 2 and log == CHANGELOG and rc2 == 1, "it refuses an unknown type (exit 2) and a file with no Unreleased section (exit 1)",
   f"unknown type should exit 2 without writing, and a changelog without ## [Unreleased] should exit 1 - got {rc}, {rc2}")
before = load("selection-before.json") or []
ok(len(before) == 4 and not any(r.get("pass") for r in before[:3]) and before[3].get("pass"),
   "selection-before.json shows the old description fired on none of the three requests",
   "save the first prove.sh run (old description) as selection-before.json")
sel = load("selection.json") or []
ok([r.get("prompt") for r in sel] == [c["prompt"] for c in CASES] and all(r.get("pass") for r in sel),
   "selection.json: all four cases behave as expected", f"selection.json should record all four cases passing - got {[(r.get('got'), r.get('pass')) for r in sel]}")
runs = sorted(glob.glob("runs/*.jsonl"))
fired = [f for f in runs if any(u.get("name") == "Skill" for u in uses(events(f)))]
ok(len(runs) == 4 and len(fired) == 3, "runs/ keeps the four stream-json transcripts; three contain a Skill call", f"prove.sh should save runs/<i>.jsonl per case - found {len(runs)} runs, {len(fired)} with a Skill call")
with tempfile.TemporaryDirectory() as t:
    shutil.copytree(".", t, dirs_exist_ok=True, ignore=shutil.ignore_patterns("runs", "selection*.json"))
    p = Path(t, SK, "SKILL.md")
    p.write_text(re.sub(r"Not for[^\n]*", "", p.read_text()))
    rc, out, err = sh("./prove.sh", cwd=t, timeout=300)
    s2 = load(os.path.join(t, "selection.json")) or []
ok(rc == 1 and "3/4" in out and s2 and s2[3].get("got") == "changelog-entry",
   "without the boundary sentence prove.sh catches the over-trigger and exits 1", f"prove.sh should exit 1 when the 'not for' case fires the skill - rc {rc}, {out.strip()[-80:]!r}")
rc, out, err = sh("claude plugin validate . --json")
v = json.loads(out) if out.strip().startswith("{") else {}
ok(rc == 0 and v.get("success"), "claude plugin validate . passes for the project's skills", f"claude plugin validate . failed: {(out + err)[-300:]}")
PYEOF
```

## What you learned

- Selection reads one line: the name and description. Lead with the action, use the user's words, and say what the skill is not for.
- Keep SKILL.md short and procedural; push reference into files and deterministic work into scripts addressed through ${CLAUDE_SKILL_DIR}.
- Triggering is testable: headless stream-json runs plus a should and should-not case matrix catch regressions in both directions.
