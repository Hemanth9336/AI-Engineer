---
type: task
title: "Assemble a local plugin"
minutes: 17
---

## Set up

Set up creates `/root/mastery/050-plugin` with:
- Loose parts: `loose/SKILL.md` (a review checklist that hard-codes the ticket prefix `ENG`) and `loose/block-env.sh` (a PreToolUse guard).
- `.claude-plugin/marketplace.json`, a one-plugin catalog named `team-local` that points at `./team-kit`.

```bash
rm -rf /root/mastery/050-plugin && mkdir -p /root/mastery/050-plugin/loose /root/mastery/050-plugin/.claude-plugin && cd /root/mastery/050-plugin
cat > loose/SKILL.md <<'EOF'
---
name: review-checklist
description: Reviews a diff or branch against the platform team's review checklist before a pull request is opened. Use when asked to review changes, check a diff before a PR, or run the team checklist. Not for writing new code.
allowed-tools: Read Grep Glob Bash(git diff *)
---
# Review checklist

Run `git diff` for the changes under review, then report each item as PASS or FAIL with file:line evidence:

1. Tests cover the new behavior.
2. No secrets, tokens, or .env files in the diff.
3. Public functions have docstrings.
4. The PR title starts with a ticket ID like `ENG-123`.

End with one line: `Checklist: <passed>/4`.
EOF
cat > loose/block-env.sh <<'EOF'
#!/usr/bin/env bash
# PreToolUse guard: refuse Edit or Write on .env files. Reads the hook event JSON on stdin.
path=$(jq -r '.tool_input.file_path // empty')
case "$(basename "$path")" in
  .env|.env.*)
    echo "Blocked: $path is an environment file. Edit secrets outside Claude Code." >&2
    exit 2 ;;
esac
exit 0
EOF
cat > .claude-plugin/marketplace.json <<'EOF'
{
  "name": "team-local",
  "owner": {
    "name": "Platform Team"
  },
  "description": "Plugins under development in this repo",
  "plugins": [
    {
      "name": "team-kit",
      "source": "./team-kit",
      "description": "Review checklist and .env guard"
    }
  ]
}
EOF
ls -R loose .claude-plugin
```

## What to build

1. Build `team-kit/`:
   - **Manifest**: `.claude-plugin/plugin.json` with `name` `team-kit`, `version` `1.0.0`, `description`, `author`, and `license`. Add a `userConfig.ticket_prefix` string option with a title, a description, and default `ENG`.
   - **Skill**: `skills/review-checklist/SKILL.md`, from the loose skill, with `ENG` replaced by `${user_config.ticket_prefix}`.
   - **Hook**: `hooks/hooks.json`, a PreToolUse group matching `Edit|Write` that runs `"${CLAUDE_PLUGIN_ROOT}"/scripts/block-env.sh` (quoted). Copy the script to `scripts/block-env.sh` and make it executable.
   - **Evals**: `evals/review-fires/` with the prompt "Review my diff against the team checklist before I open the PR." and a `tool_used: Skill` grader for `review-checklist`.
   - Also `evals/unrelated/` with "Convert 30 degrees Celsius to Fahrenheit." and a no-Skill grader (`min: 0`, `max: 0`, `arm: both`).
2. Validate it: `claude plugin validate team-kit --strict --json > validate.json`.
3. Evaluate it: `claude plugin eval team-kit --runs 2 --ablation none --trust-plugin --no-publish --json eval.json`.
4. Run the lifecycle from a fresh `project/` folder. Append each step's last `--json` line to `lifecycle.jsonl`, in this order:
   1. Add the parent folder as a marketplace at project scope. Pass its absolute path, such as `"$(dirname "$PWD")"`; a bare `..` is rejected (local paths must look like `./path` or be absolute).
   2. Install `team-kit@team-local` at project scope with `--config ticket_prefix=OPS`, then save `claude plugin list --json` as `list-installed.json`.
   3. Disable it, then disable it again.
   4. Enable it.
   5. Bump `plugin.json` to `1.1.0`, run `claude plugin marketplace update team-local`, then update the plugin.
   6. Uninstall it, then save `list-after.json`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Only plugin.json goes inside .claude-plugin/; skills/, hooks/, and scripts/ sit next to it.
- `--json` puts one JSON object on the last line of stdout, so `| tail -1 >> lifecycle.jsonl` records each step.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/050-plugin
mkdir -p team-kit/.claude-plugin team-kit/skills/review-checklist team-kit/hooks team-kit/scripts
cat > team-kit/.claude-plugin/plugin.json <<'EOF'
{
  "name": "team-kit",
  "version": "1.0.0",
  "description": "Platform team review checklist and a guard that keeps Claude out of .env files",
  "author": {
    "name": "Platform Team",
    "email": "platform@example.com"
  },
  "license": "MIT",
  "userConfig": {
    "ticket_prefix": {
      "type": "string",
      "title": "Ticket prefix",
      "description": "Prefix for ticket IDs in PR titles, such as ENG or OPS",
      "default": "ENG"
    }
  }
}
EOF
cat > team-kit/skills/review-checklist/SKILL.md <<'EOF'
---
name: review-checklist
description: Reviews a diff or branch against the platform team's review checklist before a pull request is opened. Use when asked to review changes, check a diff before a PR, or run the team checklist. Not for writing new code.
allowed-tools: Read Grep Glob Bash(git diff *)
---
# Review checklist

Run `git diff` for the changes under review, then report each item as PASS or FAIL with file:line evidence:

1. Tests cover the new behavior.
2. No secrets, tokens, or .env files in the diff.
3. Public functions have docstrings.
4. The PR title starts with a ticket ID like `${user_config.ticket_prefix}-123`.

End with one line: `Checklist: <passed>/4`.
EOF
cat > team-kit/hooks/hooks.json <<'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/block-env.sh"
          }
        ]
      }
    ]
  }
}
EOF
cp loose/block-env.sh team-kit/scripts/ && chmod +x team-kit/scripts/block-env.sh
mkdir -p team-kit/evals/review-fires/graders team-kit/evals/unrelated/graders
cat > team-kit/evals/review-fires/prompt.md <<'EOF'
---
max_turns: 5
allowed_tools: [Read, Skill]
---

Review my diff against the team checklist before I open the PR.
EOF
cat > team-kit/evals/review-fires/graders/skill-fired.md <<'EOF'
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?review-checklist"'
---
EOF
cat > team-kit/evals/unrelated/prompt.md <<'EOF'
---
max_turns: 5
allowed_tools: [Read, Skill]
---

Convert 30 degrees Celsius to Fahrenheit.
EOF
cat > team-kit/evals/unrelated/graders/no-skill.md <<'EOF'
---
type: tool_used
tool: Skill
min: 0
max: 0
arm: both
---
EOF
echo 'evals/results/' > team-kit/.gitignore
claude plugin validate team-kit --strict --json > validate.json; jq '{success, strict}' validate.json
claude plugin eval team-kit --runs 2 --ablation none --trust-plugin --no-publish --json eval.json; jq .aggregates eval.json
mkdir -p project && cd project
: > ../lifecycle.jsonl
claude plugin marketplace add "$(dirname "$PWD")" --scope project
claude plugin install team-kit@team-local --scope project --config ticket_prefix=OPS --json | tail -1 >> ../lifecycle.jsonl
claude plugin list --json > ../list-installed.json
claude plugin disable team-kit@team-local --json | tail -1 >> ../lifecycle.jsonl
claude plugin disable team-kit@team-local --json | tail -1 >> ../lifecycle.jsonl || true
claude plugin enable team-kit@team-local --json | tail -1 >> ../lifecycle.jsonl
jq '.version = "1.1.0"' ../team-kit/.claude-plugin/plugin.json > /tmp/pj.$$ && mv /tmp/pj.$$ ../team-kit/.claude-plugin/plugin.json
claude plugin marketplace update team-local
claude plugin update team-kit@team-local --json | tail -1 >> ../lifecycle.jsonl
claude plugin uninstall team-kit@team-local --scope project --json | tail -1 >> ../lifecycle.jsonl
claude plugin list --json > ../list-after.json
cd .. && jq -c '{command, outcome, failureCode, updateOutcome, newVersion}' lifecycle.jsonl
```

</details>

## Check your work

```bash
D=/root/mastery/050-plugin; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
WANT_HOOK = {'hooks': {'PreToolUse': [{'matcher': 'Edit|Write', 'hooks': [{'type': 'command', 'command': '"${CLAUDE_PLUGIN_ROOT}"/scripts/block-env.sh'}]}]}}

P = "team-kit"
m = load(f"{P}/.claude-plugin/plugin.json") or {}
ok(m.get("name") == "team-kit" and m.get("license") and isinstance(m.get("author"), dict) and m.get("description"),
   "plugin.json: name team-kit, description, author, license", "team-kit/.claude-plugin/plugin.json needs name team-kit, description, author {name}, and license")
ok(m.get("version") == "1.1.0", "the version was bumped to 1.1.0 for the update", f"bump version to 1.1.0 for the update step - got {m.get('version')!r}")
uc = (m.get("userConfig") or {}).get("ticket_prefix") or {}
ok(uc.get("type") == "string" and uc.get("title") and uc.get("description") and uc.get("default") == "ENG",
   "userConfig declares ticket_prefix (string, title, description, default ENG)", "declare userConfig.ticket_prefix with type string, title, description, and default ENG")
strays = [d for d in ("skills", "hooks", "scripts") if os.path.isdir(f"{P}/.claude-plugin/{d}")]
ok(not strays, "components sit at the plugin root, not inside .claude-plugin/", f"move {strays} out of .claude-plugin/ - only plugin.json belongs there")
meta, body = frontmatter(f"{P}/skills/review-checklist/SKILL.md")
ok(isinstance(meta, dict) and meta.get("name", "review-checklist") == "review-checklist" and "${user_config.ticket_prefix}" in body and "ENG-123" not in body,
   "skills/review-checklist/SKILL.md uses ${user_config.ticket_prefix} instead of the hard-coded ENG", "move the skill to skills/review-checklist/SKILL.md and replace ENG with ${user_config.ticket_prefix}")
hk = load(f"{P}/hooks/hooks.json") or {}
pre = (hk.get("hooks") or {}).get("PreToolUse") or []
cmds = [h.get("command", "") for g in pre for h in g.get("hooks", [])]
mt = " ".join(g.get("matcher", "") for g in pre)
ok(any('"${CLAUDE_PLUGIN_ROOT}"/scripts/block-env.sh' in c for c in cmds) and "Edit" in mt and "Write" in mt,
   "hooks/hooks.json runs the quoted \"${CLAUDE_PLUGIN_ROOT}\"/scripts/block-env.sh before Edit and Write",
   "hooks/hooks.json needs a PreToolUse group matching Edit|Write whose command is \"${CLAUDE_PLUGIN_ROOT}\"/scripts/block-env.sh (quoted)")
s = f"{P}/scripts/block-env.sh"
def guard(path):
    return sh([s], input=json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Edit", "tool_input": {"file_path": path}}))[0]
codes = {p: guard(p) for p in ("/w/.env", "/w/config/.env.local", "/w/src/app.py", "/w/docs/env.md", "/w/.envrc")}
ok(os.access(s, os.X_OK) and codes == {"/w/.env": 2, "/w/config/.env.local": 2, "/w/src/app.py": 0, "/w/docs/env.md": 0, "/w/.envrc": 0},
   "block-env.sh exits 2 for .env and .env.local, 0 for other files", f"scripts/block-env.sh must be executable and exit 2 only for .env / .env.* - got {codes}")
rc, out, err = sh(f"claude plugin validate {P} --strict --json")
v = json.loads(out) if out.strip().startswith("{") else {}
ok(rc == 0 and v.get("success") and v.get("strict"), "claude plugin validate team-kit --strict passes", f"strict validation failed: {(out + err)[-400:]}")
ev = load("eval.json") or {}
ag = ev.get("aggregates") or {}
names = sorted(c.get("name") for c in ev.get("cases") or [])
ok(names == ["review-fires", "unrelated"] and ag.get("casesTotal") == 2 and ag.get("casesPassed") == 2 and not ev.get("partial"),
   "eval.json: both cases pass (the skill fires on the review request and stays quiet on the unrelated one)",
   f"run claude plugin eval team-kit ... --json eval.json with cases review-fires and unrelated, both passing - got {names}, {ag}")
g = next((Path(f).read_text() for f in glob.glob(f"{P}/evals/unrelated/graders/*.md")), "")
ok("max: 0" in g and "arm: both" in g, "the unrelated case asserts zero Skill calls in both arms", "the unrelated grader needs min: 0, max: 0, and arm: both")
rows = events("lifecycle.jsonl")
seq = [(r.get("command"), r.get("outcome")) for r in rows]
want = [("install", "ok"), ("disable", "ok"), ("disable", "failed"), ("enable", "ok"), ("update", "ok"), ("uninstall", "ok")]
ok(seq == want, "lifecycle.jsonl: install, disable, disable again, enable, update, uninstall", f"lifecycle.jsonl should hold the six --json results in order {want} - got {seq}")
if len(rows) == 6:
    ok(rows[2].get("alreadyInGoalState") is True, "the second disable reports alreadyInGoalState - safe to treat as done in scripts", "the repeated disable should fail with alreadyInGoalState: true")
    ok(rows[4].get("updateOutcome") == "updated" and rows[4].get("oldVersion") == "1.0.0" and rows[4].get("newVersion") == "1.1.0",
       "update moved the install from 1.0.0 to 1.1.0", f"after bumping the version and refreshing the marketplace, update should report 1.0.0 -> 1.1.0 - got {rows[4]}")
here = os.path.realpath("project")
inst = [x for x in (load("list-installed.json") or []) if x.get("id") == "team-kit@team-local" and os.path.realpath(x.get("projectPath", "")) == here]
ok(inst and inst[0].get("scope") == "project" and inst[0].get("enabled") and inst[0].get("version") == "1.0.0" and inst[0].get("hasUserConfig"),
   "list-installed.json: team-kit@team-local 1.0.0 at project scope, enabled, with user config", f"save claude plugin list --json right after install - got {inst}")
ok(not [x for x in (load("list-after.json") or []) if x.get("id") == "team-kit@team-local" and os.path.realpath(x.get("projectPath", "")) == here],
   "after uninstall the plugin is gone from the list", "list-after.json should no longer contain team-kit@team-local")
PYEOF
```

## What you learned

- A plugin is a folder: the manifest in .claude-plugin/, components at the root, and bundled files addressed through a quoted ${CLAUDE_PLUGIN_ROOT}.
- userConfig replaces hand-edited settings; ${user_config.KEY} reaches skills, MCP, and exec-form hooks, but never shell-form commands.
- Every lifecycle step is a claude plugin subcommand with --json, so validate, eval, install, update, and uninstall can all be scripted and checked.
