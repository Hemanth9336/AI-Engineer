---
type: task
title: "Build a plugin layout"
minutes: 23
---

## Set up

Set up creates `/root/mastery/016-plugin` with a `CHANGELOG.md` that has a 2.4.0 section.

```bash
mkdir -p /root/mastery/016-plugin && cd /root/mastery/016-plugin
cat > CHANGELOG.md <<'EOF'
# Changelog

## 2.4.0
- Added CSV export
EOF
```

## What to build

Build a local marketplace with one plugin, by hand, under `/root/mastery/016-plugin/acme-market`.

**The plugin** at `acme-market/plugins/team-tools/`:

- `.claude-plugin/plugin.json`: name `team-tools`, a description, a semver version, and a license
- `skills/release-check/SKILL.md`: takes a version argument; its body includes `Release readiness for $ARGUMENTS` and replies with exactly `<version>: READY` or `<version>: NOT READY - <reason>`
- `agents/release-reviewer.md`: a subagent with `name` and `description` frontmatter
- `README.md` (at least 40 words) and `LICENSE`

**The marketplace** at `acme-market/.claude-plugin/marketplace.json`: name `acme-tools`, an owner, and an entry for `team-tools` with source `./plugins/team-tools`.

Then validate both with `claude plugin validate`, and from `/root/mastery/016-plugin` run the skill headlessly through `--plugin-dir`, saving the envelope as `run.json`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Plugin skills are namespaced: `/team-tools:release-check 2.4.0`.
- Relative marketplace sources resolve from the folder that contains `.claude-plugin/`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/016-plugin
mkdir -p /root/mastery/016-plugin/acme-market/plugins/team-tools/.claude-plugin /root/mastery/016-plugin/acme-market/plugins/team-tools/skills/release-check /root/mastery/016-plugin/acme-market/plugins/team-tools/agents /root/mastery/016-plugin/acme-market/.claude-plugin
cat > /root/mastery/016-plugin/acme-market/plugins/team-tools/.claude-plugin/plugin.json <<'EOF'
{
  "name": "team-tools",
  "description": "Release helpers for the platform team",
  "version": "1.0.0",
  "author": { "name": "Platform team" },
  "license": "MIT"
}
EOF
cat > /root/mastery/016-plugin/acme-market/plugins/team-tools/skills/release-check/SKILL.md <<'EOF'
---
description: Checks whether a version is ready to release. Use before tagging a release.
argument-hint: <version>
---

Release readiness for $ARGUMENTS: confirm CHANGELOG.md has a section for that version and reply
with exactly one line, `<version>: READY` or `<version>: NOT READY - <reason>`.
EOF
cat > /root/mastery/016-plugin/acme-market/plugins/team-tools/agents/release-reviewer.md <<'EOF'
---
name: release-reviewer
description: Reviews a release diff for risky changes. Use when preparing a release.
tools: Read, Grep, Glob
---

You review release diffs. List risky changes, one per line, with the file and the reason.
EOF
cat > /root/mastery/016-plugin/acme-market/plugins/team-tools/README.md <<'EOF'
# team-tools

Release helpers for the platform team. The release-check skill confirms that CHANGELOG.md has a section for the version you are about to tag, and the release-reviewer subagent lists risky changes in a release diff. Load it with claude --plugin-dir or install it from the acme-tools marketplace.
EOF
echo 'MIT License' > /root/mastery/016-plugin/acme-market/plugins/team-tools/LICENSE
cat > /root/mastery/016-plugin/acme-market/.claude-plugin/marketplace.json <<'EOF'
{
  "name": "acme-tools",
  "owner": { "name": "Acme platform team" },
  "description": "Internal Claude Code plugins",
  "plugins": [
    { "name": "team-tools", "source": "./plugins/team-tools", "description": "Release helpers" }
  ]
}
EOF
claude plugin validate /root/mastery/016-plugin/acme-market/plugins/team-tools
claude plugin validate /root/mastery/016-plugin/acme-market
claude -p "/team-tools:release-check 2.4.0" --plugin-dir /root/mastery/016-plugin/acme-market/plugins/team-tools --output-format json > run.json
jq -r .result run.json
```

</details>

## Check your work

```bash
D=/root/mastery/016-plugin; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

pl, mk = "/root/mastery/016-plugin/acme-market/plugins/team-tools", "/root/mastery/016-plugin/acme-market"
m = load(pl + "/.claude-plugin/plugin.json") or {}
ok(m.get("name") == "team-tools" and re.fullmatch(r"\d+\.\d+\.\d+", m.get("version", "")) and m.get("description"),
   "plugin.json names team-tools with a description and a semver version", "write acme-market/plugins/team-tools/.claude-plugin/plugin.json with name, description, version x.y.z")
extra = [p for p in os.listdir(pl + "/.claude-plugin") if p != "plugin.json"] if os.path.isdir(pl + "/.claude-plugin") else ["missing"]
ok(not extra, "only plugin.json sits inside .claude-plugin/", f"move {extra} out of .claude-plugin/ - components there never load")
ag = text(pl + "/agents/release-reviewer.md")
ok(os.path.isfile(pl + "/skills/release-check/SKILL.md") and re.match(r"---\n(?=.*name: release-reviewer)(?=.*description: ).*?\n---", ag, re.S),
   "the plugin has the release-check skill and a release-reviewer subagent with name and description",
   "add skills/release-check/SKILL.md and agents/release-reviewer.md (frontmatter needs name and description)")
ok(len(text(pl + "/README.md").split()) >= 40 and (os.path.isfile(pl + "/LICENSE") or m.get("license")),
   "the plugin ships a README and a license", "add a README.md (40+ words) and a LICENSE file or a license field")
rc, out, err = sh(["claude", "plugin", "validate", pl], timeout=120)
ok(rc == 0 and "Validation passed" in out + err, "claude plugin validate passes for the plugin", "claude plugin validate failed: " + (out + err).strip()[-300:])
mj = load(mk + "/.claude-plugin/marketplace.json") or {}
src = next((p.get("source") for p in mj.get("plugins") or [] if p.get("name") == "team-tools"), None)
rc2, out2, err2 = sh(["claude", "plugin", "validate", mk], timeout=120)
ok(mj.get("name") == "acme-tools" and (mj.get("owner") or {}).get("name") and src == "./plugins/team-tools" and rc2 == 0,
   "the acme-tools marketplace lists team-tools from ./plugins/team-tools and validates",
   "acme-market/.claude-plugin/marketplace.json needs name acme-tools, an owner, and team-tools with source ./plugins/team-tools: " + (out2 + err2).strip()[-200:])
env = load("run.json") or {}
f, rows = transcript(env.get("session_id") or "none")
body = "\n".join(b.get("text", "") for r in rows if r.get("type") == "user" for b in content(r) if b.get("type") == "text")
ok("Release readiness for 2.4.0" in body and (env.get("result") or "").strip() == "2.4.0: READY",
   "the namespaced skill /team-tools:release-check ran from --plugin-dir", f"run /team-tools:release-check 2.4.0 with --plugin-dir and save run.json - got {env.get('result')!r}")
PYEOF
```

## What you learned

- A plugin root holds .claude-plugin/plugin.json plus skills/, agents/, hooks/, and .mcp.json - never components inside .claude-plugin/.
- Plugin components are namespaced by the plugin name.
- A marketplace.json catalogs plugins; claude plugin validate checks both before anyone installs.
