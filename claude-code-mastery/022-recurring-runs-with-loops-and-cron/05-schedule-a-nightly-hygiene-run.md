---
type: task
title: "Schedule a nightly hygiene run"
minutes: 14
---

## Set up

Set up creates `/root/mastery/022-hygiene/src/` with three modules carrying TODO and FIXME comments.

```bash
rm -rf /root/mastery/022-hygiene && mkdir -p /root/mastery/022-hygiene/src && cd /root/mastery/022-hygiene
cat > src/billing.py <<'EOF'
def charge(c):
    # TODO: retry on network errors
    return c
EOF
cat > src/auth.py <<'EOF'
def login(u):
    # FIXME: rate limit login attempts
    return u


def logout(u):
    return None
EOF
cat > src/report.py <<'EOF'
def monthly():
    # TODO: add CSV output
    return []
EOF
rmdir /tmp/hygiene-022.lock 2>/dev/null || true
```

## What to build

Build a nightly, read-only hygiene job that survives cron's empty environment.

1. `prompts/hygiene.md` - the fixed prompt:
   > List every TODO and FIXME comment under src/ as `path:line: text` lines, sorted by path. Reply with only those lines, or NONE if there are none.
2. `hygiene.sh` (executable) - a self-contained wrapper that:
   - sets its own `PATH` and loads the lab settings from `~/.config/ailab/env`;
   - `cd`s to `/root/mastery/022-hygiene` by absolute path;
   - takes a lock at `/tmp/hygiene-022.lock` and exits 0 without running if another copy holds it;
   - runs the prompt headless with a turn limit and writes `reports/hygiene-<YYYY-MM-DD>.json`.
3. `crontab.txt` - one line that runs the script at 02:00 every night and appends stdout and stderr to `logs/cron.log`. To install it for real, merge it into your crontab with `crontab -e` (`crontab crontab.txt` would replace any existing entries).
4. Rehearse the cron environment: `env -i HOME="$HOME" /bin/sh -c /root/mastery/022-hygiene/hygiene.sh`.

The checker runs your script under `env -i` from `/`, then again while the lock is held.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Under `env -i`, nothing from `~/.bashrc` exists - the script has to set up everything itself.
- `mkdir` of the lock directory is atomic: it fails if the directory already exists.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/022-hygiene
mkdir -p prompts logs
cat > prompts/hygiene.md <<'EOF'
List every TODO and FIXME comment under src/ as `path:line: text` lines, sorted by path. Reply with only those lines, or NONE if there are none.
EOF
cat > hygiene.sh <<'EOF'
#!/bin/bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
[ -f "$HOME/.config/ailab/env" ] && . "$HOME/.config/ailab/env"
cd /root/mastery/022-hygiene
mkdir -p reports logs
if ! mkdir /tmp/hygiene-022.lock 2>/dev/null; then echo "previous run still active"; exit 0; fi
trap 'rmdir /tmp/hygiene-022.lock' EXIT
claude -p "$(cat prompts/hygiene.md)" --max-turns 10 --output-format json > "reports/hygiene-$(date +%F).json"
echo "$(date -u +%FT%TZ) hygiene run finished"
EOF
chmod +x hygiene.sh
echo '0 2 * * * /root/mastery/022-hygiene/hygiene.sh >> /root/mastery/022-hygiene/logs/cron.log 2>&1' > crontab.txt
env -i HOME="$HOME" /bin/sh -c /root/mastery/022-hygiene/hygiene.sh
ls reports
```

</details>

## Check your work

```bash
D=/root/mastery/022-hygiene; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
D = "/root/mastery/022-hygiene"
c = text("crontab.txt").strip().splitlines()
line = next((l for l in c if l.strip() and not l.startswith("#")), "")
f = line.split()
ok(len(f) >= 6 and f[0].isdigit() and f[1].isdigit() and f[2:5] == ["*", "*", "*"] and f[5] == D + "/hygiene.sh" and ">>" in line and "2>&1" in line,
   "crontab.txt runs the absolute script nightly and logs stdout and stderr",
   f"crontab.txt should hold one nightly line like 'M H * * * {D}/hygiene.sh >> {D}/logs/cron.log 2>&1' - got {line!r}")
h = text("hygiene.sh")
ok(os.access("hygiene.sh", os.X_OK) and "PATH=" in h and ".config/ailab/env" in h and f"cd {D}" in h and ("flock" in h or "mkdir /tmp" in h),
   "hygiene.sh sets PATH, loads the lab settings, uses an absolute cd, and takes a lock",
   "hygiene.sh must be executable, export PATH, source ~/.config/ailab/env, cd to the absolute lab path, and use a lock (flock or mkdir)")
for p in glob.glob("reports/hygiene-*.json"):
    os.remove(p)
rc, out, err = sh(["env", "-i", "HOME=" + os.path.expanduser("~"), "/bin/sh", "-c", D + "/hygiene.sh"], cwd="/", timeout=300)
reps = glob.glob("reports/hygiene-*.json")
env = load(reps[0]) if reps else {}
want = sh("grep -rnE 'TODO|FIXME' src | sed -E 's/:[[:space:]]*#[[:space:]]*/: /' | sort")[1].strip()
ok(rc == 0 and env and env.get("subtype") == "success", "under an empty cron-like environment the script ran Claude and wrote a dated report",
   f"env -i HOME=$HOME /bin/sh -c {D}/hygiene.sh failed (rc {rc}): {(out + err).strip()[-300:]}")
ok((env.get("result") or "").strip() == want, "the report lists exactly the TODO and FIXME lines", f"the report should be:\n{want}\ngot:\n{(env.get('result') or '').strip()}")
os.makedirs("/tmp/hygiene-022.lock", exist_ok=True)
try:
    rc2, out2, _ = sh(["env", "-i", "HOME=" + os.path.expanduser("~"), "/bin/sh", "-c", D + "/hygiene.sh"], cwd="/", timeout=20)
finally:
    os.rmdir("/tmp/hygiene-022.lock")
ok(rc2 == 0 and "claude" not in out2.lower() and len(glob.glob("reports/hygiene-*.json")) == 1 and load(reps[0]) == env,
   "a second copy started while the lock is held exits without running", "while /tmp/hygiene-022.lock exists the script should exit 0 straight away")
PYEOF
```

## What you learned

- Shell loops, cron, /loop, and cloud tasks each repeat agent work with different lifetimes.
- Cron's empty environment breaks PATH, settings, and the working directory - a wrapper script fixes all three.
- Recurring jobs should be read-only, bounded, locked against overlap, and logged.
