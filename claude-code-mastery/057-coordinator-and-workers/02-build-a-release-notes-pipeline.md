---
type: task
title: "Build a release notes pipeline"
minutes: 30
---

## Set up

Set up creates `/root/mastery/057-relnotes`, a git repo tagged `v2.3.0` followed by eight commits: features, fixes, a breaking change, and the usual noise (WIP, CI chores, a typo fix, a merge).

```bash
rm -rf /root/mastery/057-relnotes && mkdir -p /root/mastery/057-relnotes && cd /root/mastery/057-relnotes
git init -q -b main && git config user.name 'Lab Learner' && git config user.email learner@example.com
echo '# reports' > README.md && git add -A && git commit -qm 'release 2.3.0' && git tag v2.3.0
git commit -q --allow-empty -m "feat(export): add CSV export for reports"
git commit -q --allow-empty -m "fix(upload): resume uploads after a dropped connection"
git commit -q --allow-empty -m "WIP"
git commit -q --allow-empty -m "chore(ci): bump runner image"
git commit -q --allow-empty -m "feat!: drop support for Python 3.8"
git commit -q --allow-empty -m "fix: typo in README"
git commit -q --allow-empty -m "Merge branch 'feature/export'"
git commit -q --allow-empty -m "fix(auth): compare session tokens in constant time"
git log --oneline v2.3.0..HEAD
```

## What to build

1. Write `notes.schema.json`.
   - Required: `version`, `internal_count` (integer), and `breaking`, `features`, `fixes`.
   - Each of the three lists holds `{n, text}` items, where `n` is the commit number.
2. Write `render.py notes.json`, which prints Markdown:
   - `# Release <version>`, then `## Breaking changes`, `## Features`, and `## Fixes` as `- text` bullets ordered by `n`, skipping empty sections;
   - then `_<n> internal change(s) not listed._` when `internal_count` is above 0.
3. Write `relnotes.sh <from> <to> <version>`. Steps:
   1. Validate the arguments and both refs, and require a non-empty range. Exit 2 otherwise, without calling Claude.
   2. Write the numbered subjects, oldest first, to `commits.txt` (`1. <subject>`).
   3. Define the workers **inline**: `AGENTS='{...}'`, with `commit-classifier` and `notes-writer`, each with `"tools": []` and `"model": "haiku"`.
   4. Run the coordinator: `claude -p "$PROMPT" --agents "$AGENTS" --json-schema ... --output-format json`, saving `run.json`. The prompt sends all commits to the classifier and only user-facing ones to the writer.
   5. Exit 3 unless there is a valid `structured_output`. Otherwise save it as `notes.json` and render `RELEASE_NOTES.md`.
4. Run `./relnotes.sh v2.3.0 HEAD 2.4.0`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `git log --reverse --format=%s A..B | awk '{print NR ". " $0}'` numbers the subjects oldest first.
- Workers refer to commits by number; the coordinator joins classifier and writer output on it.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/057-relnotes
cat > notes.schema.json <<'EOF'
{
  "type": "object",
  "properties": {
    "version": {
      "type": "string"
    },
    "breaking": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "n": {
            "type": "integer"
          },
          "text": {
            "type": "string"
          }
        },
        "required": [
          "n",
          "text"
        ],
        "additionalProperties": false
      }
    },
    "features": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "n": {
            "type": "integer"
          },
          "text": {
            "type": "string"
          }
        },
        "required": [
          "n",
          "text"
        ],
        "additionalProperties": false
      }
    },
    "fixes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "n": {
            "type": "integer"
          },
          "text": {
            "type": "string"
          }
        },
        "required": [
          "n",
          "text"
        ],
        "additionalProperties": false
      }
    },
    "internal_count": {
      "type": "integer"
    }
  },
  "required": [
    "version",
    "breaking",
    "features",
    "fixes",
    "internal_count"
  ],
  "additionalProperties": false
}
EOF
cat > render.py <<'EOF'
#!/usr/bin/env python3
"""render.py notes.json - Markdown release notes from the coordinator's structured output. Empty sections are left out."""
import json
import sys

SECTIONS = [("breaking", "Breaking changes"), ("features", "Features"), ("fixes", "Fixes")]


def render(notes):
    out = [f"# Release {notes['version']}", ""]
    for key, title in SECTIONS:
        items = sorted(notes.get(key) or [], key=lambda i: i["n"])
        if items:
            out += [f"## {title}", ""] + [f"- {i['text']}" for i in items] + [""]
    n = notes.get("internal_count", 0)
    if n:
        out.append(f"_{n} internal change{'s' if n != 1 else ''} not listed._")
    return "\n".join(out).rstrip("\n") + "\n"


if __name__ == "__main__":
    sys.stdout.write(render(json.load(open(sys.argv[1]))))
EOF
cat > relnotes.sh <<'EOF'
#!/usr/bin/env bash
# relnotes.sh <from> <to> <version> - coordinator plus two inline workers turn a commit range into RELEASE_NOTES.md.
# Exit: 0 ok, 2 bad arguments or range, 3 the agent run failed.
set -uo pipefail
cd "$(dirname "$0")"
[ $# -eq 3 ] || { echo "usage: relnotes.sh <from> <to> <version>" >&2; exit 2; }
from=$1 to=$2 version=$3
for ref in "$from" "$to"; do
  git rev-parse --verify -q "$ref^{commit}" > /dev/null || { echo "unknown ref: $ref" >&2; exit 2; }
done
git log --reverse --format=%s "$from..$to" | awk '{print NR ". " $0}' > commits.txt
[ -s commits.txt ] || { echo "no commits in $from..$to" >&2; exit 2; }

AGENTS='{
  "commit-classifier": {
    "description": "Classifies numbered commit subjects as breaking, feature, fix, or internal.",
    "prompt": "You classify commit subjects. breaking: incompatible changes (a ! after the type). feature: new user-facing capability. fix: user-facing bug fix. internal: everything else (chores, CI, docs typos, WIP, merges). Reply with only a JSON object mapping each commit number to its category.",
    "tools": [], "model": "haiku"},
  "notes-writer": {
    "description": "Rewrites commit subjects as one-line, user-facing release notes.",
    "prompt": "Rewrite each commit as one short line a user understands: what changed for them, present tense, no ticket ids. Reply with only lines of the form <number>: <note>.",
    "tools": [], "model": "haiku"}
}'
PROMPT="Release notes for version $version. commits.txt lists the commits since the last release, numbered. Send the whole numbered list to the commit-classifier worker. Then send only the breaking, feature, and fix commits to the notes-writer worker. Merge both replies into the structured output; count the internal commits instead of listing them."

claude -p "$PROMPT" --agents "$AGENTS" --allowedTools Read --json-schema "$(cat notes.schema.json)" \
  --output-format json < /dev/null > run.json
if [ $? -ne 0 ] || ! jq -e '.is_error == false and .structured_output.version != null' run.json > /dev/null 2>&1; then
  echo "agent run failed" >&2
  exit 3
fi
jq .structured_output run.json > notes.json
python3 render.py notes.json > RELEASE_NOTES.md
cat RELEASE_NOTES.md
EOF
chmod +x relnotes.sh render.py
./relnotes.sh v2.3.0 HEAD 2.4.0
```

</details>

## Check your work

```bash
D=/root/mastery/057-relnotes; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def subagent_runs(f):
    """(agentType, rows) for each subagent transcript saved beside a main session transcript."""
    out = []
    for m in sorted(glob.glob(os.path.join(f[:-6], "subagents", "*.meta.json"))) if f else []:
        rows = events(m.replace(".meta.json", ".jsonl"))
        out.append(((load(m) or {}).get("agentType"), rows))
    return out
def final_text(rows):
    t = [b.get("text", "") for r in rows if r.get("type") == "assistant" for b in content(r) if b.get("type") == "text"]
    return t[-1] if t else ""
OUT = {'version': '2.4.0', 'breaking': [{'n': 5, 'text': 'Python 3.8 is no longer supported'}], 'features': [{'n': 1, 'text': 'Export reports to CSV'}], 'fixes': [{'n': 2, 'text': 'Uploads resume after a dropped connection'}, {'n': 8, 'text': 'Session tokens are compared in constant time'}], 'internal_count': 4}
LIST = "1. feat(export): add CSV export for reports\n2. fix(upload): resume uploads after a dropped connection\n3. WIP\n4. chore(ci): bump runner image\n5. feat!: drop support for Python 3.8\n6. fix: typo in README\n7. Merge branch 'feature/export'\n8. fix(auth): compare session tokens in constant time"

sc = load("notes.schema.json") or {}
ok(set(sc.get("required") or []) >= {"version", "breaking", "features", "fixes", "internal_count"},
   "notes.schema.json requires version, breaking, features, fixes, and internal_count", "notes.schema.json must require version, breaking, features, fixes, internal_count")
src = text("relnotes.sh")
m = re.search(r"AGENTS='(\{.*?\})'", src, re.S)
try:
    ag = json.loads(m.group(1)) if m else {}
except ValueError:
    ag = {}
ok(sorted(ag) == ["commit-classifier", "notes-writer"] and all(v.get("tools") == [] and v.get("model") == "haiku" and v.get("description") and v.get("prompt") for v in ag.values()),
   "relnotes.sh defines both workers inline (AGENTS='...') with tools [] on haiku", f"define AGENTS='{{...}}' in relnotes.sh with commit-classifier and notes-writer, each with description, prompt, tools [], model haiku - got {sorted(ag)}")
ok("--agents" in src and "--json-schema" in src, "the coordinator run uses --agents and --json-schema", "pass --agents \"$AGENTS\" and --json-schema to the coordinator run")
ok(text("commits.txt").strip() == LIST, "commits.txt numbers the 8 commits of v2.3.0..HEAD oldest first", f"commits.txt should be:\n{LIST}")
env = load("run.json") or {}
f, rows = transcript(env.get("session_id") or "none")
subs = subagent_runs(f)
types = sorted({t for t, _ in subs})
ok(types == ["commit-classifier", "notes-writer"], "the coordinator delegated to both workers", f"subagents seen: {types}")
big = {t: len(final_text(r)) for t, r in subs if len(final_text(r)) > 1200}
ok(subs and not big, "every worker reply stayed small (under 1,200 characters)", f"worker replies too large for the coordinator: {big}")
wr = [u for u in uses(rows) if u.get("name") == "Agent" and (u.get("input") or {}).get("subagent_type") == "notes-writer"]
ok(wr and not any(s in json.dumps(wr) for s in ("WIP", "bump runner image", "Merge branch")), "the writer received only user-facing commits",
   "send the notes-writer only breaking, feature, and fix commits")
so = env.get("structured_output") or {}
def ns(k):
    return sorted(i.get("n") for i in so.get(k) or [])
ok(so.get("version") == "2.4.0" and all(ns(k) == sorted(i["n"] for i in OUT[k]) for k in ("breaking", "features", "fixes")) and so.get("internal_count") == OUT["internal_count"],
   "structured_output classifies 1 breaking, 1 feature, 2 fixes, and 4 internal commits", f"structured_output should be {OUT} - got {so}")
sys.path.insert(0, os.getcwd())
import importlib
rend = importlib.import_module("render")
ok(text("RELEASE_NOTES.md") == rend.render(so) and text("RELEASE_NOTES.md").startswith("# Release 2.4.0\n\n## Breaking changes\n"),
   "RELEASE_NOTES.md is render.py's output, breaking changes first", "RELEASE_NOTES.md should come from python3 render.py notes.json")
r1 = rend.render({"version": "9.9", "breaking": [], "features": [{"n": 3, "text": "B"}, {"n": 1, "text": "A"}], "fixes": [], "internal_count": 1})
ok(r1 == "# Release 9.9\n\n## Features\n\n- A\n- B\n\n_1 internal change not listed._\n", "render.py drops empty sections, orders by number, and says 'change' for one",
   f"render on hidden notes gave {r1!r}")
r2 = rend.render({"version": "1.0", "breaking": [], "features": [], "fixes": [{"n": 1, "text": "X"}], "internal_count": 0})
ok(r2 == "# Release 1.0\n\n## Fixes\n\n- X\n", "with no internal commits there's no footer", f"render with internal_count 0 gave {r2!r}")
with tempfile.TemporaryDirectory() as t:
    stub = Path(t, "claude")
    stub.write_text("#!/usr/bin/env bash\ntouch \"$STUB_MARK\"\nexit 0\n")
    stub.chmod(0o755)
    mark = Path(t, "called")
    envx = {"PATH": f"{t}:" + os.environ["PATH"], "STUB_MARK": str(mark)}
    rc1, _, e1 = sh("./relnotes.sh v9.9.9 HEAD 3.0.0", env=envx)
    rc2, _, _ = sh("./relnotes.sh HEAD HEAD 3.0.0", env=envx)
    rc3, _, _ = sh("./relnotes.sh v2.3.0", env=envx)
    called = mark.exists()
    import shutil
    cp = Path(t, "copy")
    shutil.copytree(".", cp)
    rc4, _, _ = sh("./relnotes.sh v2.3.0 HEAD 3.0.0", cwd=cp, env=envx)
ok((rc1, rc2, rc3) == (2, 2, 2) and not called, "a bad ref, an empty range, or missing arguments exit 2 before any agent call",
   f"validate inputs first and exit 2 without calling claude - got {(rc1, rc2, rc3)}, claude called: {called}")
ok(rc4 == 3, "a run without a structured result exits 3", f"when claude returns nothing usable, relnotes.sh should exit 3 - got {rc4}")
PYEOF
```

## What you learned

- A coordinator splits a deliverable into stages, gives each worker the minimum input, and joins replies on identifiers.
- Inline --agents workers with tools [] and an exact reply format keep the coordinator's context small.
- Validate inputs before any agent call, constrain the result with --json-schema, and render with code.
