---
type: task
title: "Build a marketplace of one"
minutes: 23
---

## Set up

Set up creates `/root/mastery/051-market` with:
- `upstream/lint-kit`, a plugin repo with two tags. `v1.0.0` is the version your team reviewed. `v1.1.0` (now `main`) adds a SessionStart hook that sends usage stats.
- `dist/fmt-kit-1.0.0.zip`, a release archive that will be served from `https://artifacts.acme.example/`.

```bash
rm -rf /root/mastery/051-market && mkdir -p /root/mastery/051-market/upstream/lint-kit/.claude-plugin /root/mastery/051-market/upstream/lint-kit/skills/lint /root/mastery/051-market/dist && cd /root/mastery/051-market/upstream/lint-kit
git init -q -b main && git config user.name 'Lab Learner' && git config user.email learner@example.com
cat > .claude-plugin/plugin.json <<'EOF'
{"name": "lint-kit", "version": "1.0.0", "description": "Lint helpers", "license": "MIT"}
EOF
cat > skills/lint/SKILL.md <<'EOF'
---
name: lint
description: Runs the team linter and explains findings. Use when asked to lint or check style.
---
Run `ruff check .` and summarize each finding with file:line.
EOF
git add -A && git commit -qm 'lint-kit 1.0.0' && git tag v1.0.0
mkdir -p hooks
cat > hooks/hooks.json <<'EOF'
{"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo 'lint-kit: sending usage stats to stats.example.com'"}]}]}}
EOF
sed -i.bak 's/1.0.0/1.1.0/' .claude-plugin/plugin.json && rm -f .claude-plugin/plugin.json.bak
git add -A && git commit -qm 'lint-kit 1.1.0: usage stats hook' && git tag v1.1.0
cd /root/mastery/051-market
cat > mkzip.py <<'EOF'
import io, json, zipfile
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for name, data in [("fmt-kit/.claude-plugin/plugin.json", json.dumps({"name": "fmt-kit", "version": "1.0.0", "description": "Formatter helpers", "license": "MIT"})),
                       ("fmt-kit/skills/fmt/SKILL.md", "---\nname: fmt\ndescription: Formats Python files with the team settings. Use when asked to format code.\n---\nRun the formatter.\n")]:
        info = zipfile.ZipInfo(name, (2026, 10, 1, 0, 0, 0))
        info.external_attr = 0o644 << 16
        z.writestr(info, data)
open("dist/fmt-kit-1.0.0.zip", "wb").write(buf.getvalue())
EOF
python3 mkzip.py && rm mkzip.py
git -C upstream/lint-kit log --oneline --decorate
```

## What to build

1. Write `market/.claude-plugin/marketplace.json` named `acme-tools`, with an `owner`, a `description`, and two entries:
   - **`lint-kit`**: a `url` source, `file://<absolute path>/upstream/lint-kit`, with `ref` `v1.0.0` and `sha` set to the full commit of `v1.0.0` (`git rev-parse 'v1.0.0^{commit}'`).
   - **`fmt-kit`**: an `archive` source, `https://artifacts.acme.example/fmt-kit-1.0.0.zip`, with `sha256` set to the zip's digest.
2. Validate it: `claude plugin validate market --strict`.
3. From a new `project/` folder:
   - Add the marketplace at project scope.
   - Install `lint-kit@acme-tools` at project scope, and save the `--json` line as `install.json`.
   - Run `claude plugin update lint-kit@acme-tools --json`, and save it as `update.json`.
   - Save `claude plugin list --json` as `list.json`.

The pin is the point: `main` already has the stats hook, and your users must not get it until someone reviews it and moves the pin.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq -n --arg sha "$SHA" '{...}'` builds the JSON without quoting mistakes.
- Relative plugin paths resolve from the marketplace root (the folder holding .claude-plugin/), but lint-kit lives in another repo, so it needs a git source.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/051-market
LINT_SHA=$(git -C upstream/lint-kit rev-parse 'v1.0.0^{commit}')
ZIP_SHA=$(shasum -a 256 dist/fmt-kit-1.0.0.zip | cut -d' ' -f1)
mkdir -p market/.claude-plugin
jq -n --arg url "file://$PWD/upstream/lint-kit" --arg sha "$LINT_SHA" --arg zsha "$ZIP_SHA" '{
  name: "acme-tools",
  owner: {name: "Acme Platform Team", email: "platform@acme.example"},
  description: "Plugins reviewed and pinned by the platform team",
  plugins: [
    {name: "lint-kit", description: "Lint helpers (reviewed at v1.0.0)", category: "quality",
     source: {source: "url", url: $url, ref: "v1.0.0", sha: $sha}},
    {name: "fmt-kit", description: "Formatter helpers", version: "1.0.0", category: "quality",
     source: {source: "archive", url: "https://artifacts.acme.example/fmt-kit-1.0.0.zip", sha256: $zsha}}
  ]}' > market/.claude-plugin/marketplace.json
cat market/.claude-plugin/marketplace.json
claude plugin validate market --strict
mkdir -p project && cd project
claude plugin marketplace add ../market --scope project
claude plugin install lint-kit@acme-tools --scope project --json | tail -1 > ../install.json
claude plugin update lint-kit@acme-tools --json | tail -1 > ../update.json
claude plugin list --json > ../list.json
cd .. && jq -c '{updateOutcome, newVersion}' update.json
```

</details>

## Check your work

```bash
D=/root/mastery/051-market; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
ZIPSHA = '34b33f697ea502021a2070fe43bc1e6253edeb58f8c7a270e01bec1982e5a49b'

mk = load("market/.claude-plugin/marketplace.json") or {}
ok(mk.get("name") == "acme-tools" and (mk.get("owner") or {}).get("name") and mk.get("description"),
   "marketplace.json: name acme-tools, owner, description", "market/.claude-plugin/marketplace.json needs name acme-tools, owner.name, and description")
ents = {e.get("name"): e for e in mk.get("plugins") or []}
ok(sorted(ents) == ["fmt-kit", "lint-kit"], "it lists lint-kit and fmt-kit", f"list exactly lint-kit and fmt-kit - got {sorted(ents)}")
lsrc = (ents.get("lint-kit") or {}).get("source") or {}
rc, v1, _ = sh("git -C upstream/lint-kit rev-parse 'v1.0.0^{commit}'")
rc2, head, _ = sh("git -C upstream/lint-kit rev-parse HEAD")
ok(lsrc.get("source") in ("url", "git-subdir") and os.path.realpath(str(lsrc.get("url", "")).replace("file://", "")) == os.path.realpath("upstream/lint-kit"),
   "lint-kit comes from the upstream repo through a git source", f"lint-kit's source should be {{source: url, url: file://{os.path.realpath('upstream/lint-kit')}}} - got {lsrc}")
ok(lsrc.get("sha") == v1.strip() and v1.strip() != head.strip(), "lint-kit is pinned to the reviewed v1.0.0 commit, not the newer main",
   f"set sha to the full commit of v1.0.0 ({v1.strip()[:12]}...) - got {str(lsrc.get('sha'))[:12]!r}")
asrc = (ents.get("fmt-kit") or {}).get("source") or {}
ok(asrc.get("source") == "archive" and str(asrc.get("url", "")).startswith("https://"), "fmt-kit is an https archive source", f"fmt-kit needs source {{source: archive, url: https://...}} - got {asrc}")
ok(str(asrc.get("sha256", "")).lower() == ZIPSHA == sha("dist/fmt-kit-1.0.0.zip"), "fmt-kit's sha256 matches the bytes of dist/fmt-kit-1.0.0.zip",
   f"sha256 must be the zip's digest (shasum -a 256 dist/fmt-kit-1.0.0.zip) - got {str(asrc.get('sha256'))[:16]!r}")
rc, out, err = sh("claude plugin validate market --strict")
ok(rc == 0, "claude plugin validate market --strict passes", f"strict validation failed: {(out + err)[-400:]}")
with tempfile.TemporaryDirectory() as t:
    bad = json.loads(json.dumps(mk))
    for e in bad.get("plugins") or []:
        if e.get("name") == "lint-kit":
            e["source"]["sha"] = str(e["source"].get("sha", ""))[:12]
    Path(t, ".claude-plugin").mkdir()
    Path(t, ".claude-plugin", "marketplace.json").write_text(json.dumps(bad))
    rc, out, err = sh(["claude", "plugin", "validate", t])
ok(rc == 1 and "40" in out + err, "(a short sha in a copy fails validation - pins must be full commits)", f"a 12-character sha should fail validation - rc {rc}")
ins = load("install.json") or {}
ok(ins.get("command") == "install" and ins.get("outcome") == "ok" and ins.get("scope") == "project",
   "install.json: lint-kit@acme-tools installed at project scope", f"save the --json line of the install as install.json - got {ins}")
here = os.path.realpath("project")
lst = [x for x in (load("list.json") or []) if x.get("id") == "lint-kit@acme-tools" and os.path.realpath(x.get("projectPath", "")) == here]
ip = lst[0].get("installPath", "") if lst else ""
ok(lst and lst[0].get("version") == "1.0.0" and os.path.isdir(ip) and not os.path.exists(os.path.join(ip, "hooks", "hooks.json")),
   "the installed copy is 1.0.0 and has no usage-stats hook", f"list.json should show lint-kit 1.0.0, installed without hooks/hooks.json - got {lst}")
up = load("update.json") or {}
ok(up.get("updateOutcome") == "up_to_date" and up.get("newVersion") == "1.0.0", "update.json: up_to_date - the new upstream commit didn't reach users",
   f"with the sha pin, claude plugin update should report up_to_date at 1.0.0 - got {up}")
st = load("project/.claude/settings.json") or {}
ok("acme-tools" in (st.get("extraKnownMarketplaces") or {}) and (st.get("enabledPlugins") or {}).get("lint-kit@acme-tools"),
   "project/.claude/settings.json declares the marketplace and enables lint-kit for the team", "add the marketplace and install at --scope project from project/")
PYEOF
```

## What you learned

- marketplace.json is a catalog: name, owner, and plugin entries whose source says where each plugin comes from.
- A tag can move; a 40-character commit sha or an archive sha256 pins exact content, and updates can't move past it.
- A digest proves the bytes are the ones you reviewed - the review is still the part that makes them safe.
