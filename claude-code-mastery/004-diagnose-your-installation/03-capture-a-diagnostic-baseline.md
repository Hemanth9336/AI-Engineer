---
type: task
title: "Capture a diagnostic baseline"
minutes: 20
---

## Set up

```bash
mkdir -p /root/mastery/004-doctor
```

## What to build

In `/root/mastery/004-doctor`, record what a healthy installation looks like, in a form you can diff later.

1. Save `claude --version` to `version.txt` and the full `claude doctor` report to `doctor.txt`.
2. Write `baseline.sh`, an executable script that prints exactly these four lines, taking each value from `claude --version` and the matching `claude doctor` line:

```text
version: <version number from claude --version>
running: <value of the Running: line>
search: <value of the Search: line>
auto-updates: <value of the Auto-updates: line>
```

3. If the version in the `Running:` line is not the one `claude --version` printed, the script must print a line containing `MISMATCH` and exit `1`. Otherwise it exits `0`.
4. Save today's output: `./baseline.sh > baseline.txt`.

The checker runs your script on this machine, then again against fake `claude` binaries that agree and disagree.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `sed -n 's/^Search: //p'` prints just the value of the Search line.
- `claude --version` prints `2.1.310 (Claude Code)` - you only want the first word.

</details>

<details><summary>Solution</summary>

```bash
mkdir -p /root/mastery/004-doctor && cd /root/mastery/004-doctor
claude --version > version.txt
claude doctor > doctor.txt 2>&1
cat > baseline.sh <<'EOF'
#!/bin/bash
# Print a diffable diagnostic baseline. Exit 1 when the version flag and doctor disagree.
v=$(claude --version | awk '{print $1}')
d=$(claude doctor < /dev/null 2>&1)
field() { printf '%s\n' "$d" | sed -n "s/^$1: //p" | head -1; }
running=$(field Running)
echo "version: $v"
echo "running: $running"
echo "search: $(field Search)"
echo "auto-updates: $(field Auto-updates)"
case "$running" in
  *"($v)"*) ;;
  *) echo "MISMATCH: claude --version says $v but doctor is running $running" >&2; exit 1 ;;
esac
EOF
chmod +x baseline.sh
./baseline.sh > baseline.txt
cat baseline.txt
```

</details>

## Check your work

```bash
D=/root/mastery/004-doctor; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
rc, ver, _ = sh("claude --version")
ok(text("version.txt").strip() == ver.strip() != "", "version.txt matches claude --version", "save claude --version to version.txt")
doc = text("doctor.txt")
ok("Running:" in doc and "Search:" in doc, "doctor.txt holds claude doctor output", "save the output of claude doctor to doctor.txt")
ok(os.access("baseline.sh", os.X_OK), "baseline.sh is executable", "create baseline.sh and chmod +x it")
rc, out, err = sh("./baseline.sh", timeout=120)
lines = dict(l.split(": ", 1) for l in out.splitlines() if ": " in l)
real = sh("claude doctor < /dev/null", timeout=120)[1]
def field(name):
    m = re.search(rf"^{name}: (.*)$", real, re.M)
    return m.group(1).strip() if m else None
want = {"version": ver.split()[0] if ver.split() else "", "running": field("Running"), "search": field("Search"), "auto-updates": field("Auto-updates")}
ok(rc == 0 and all(lines.get(k, "").strip() == v for k, v in want.items()),
   "baseline.sh prints version, running, search, and auto-updates matching this machine",
   f"baseline.sh should print {want} and exit 0 - got exit {rc}: {lines}")
ok(text("baseline.txt").strip() == out.strip(), "baseline.txt is the saved output of baseline.sh", "save ./baseline.sh > baseline.txt")
stub = tempfile.mkdtemp()
def fake(version, running):
    Path(stub, "claude").write_text(
        "#!/bin/sh\n"
        f'if [ "$1" = --version ]; then echo "{version} (Claude Code)"; exit 0; fi\n'
        f'if [ "$1" = doctor ]; then printf "Claude Code doctor\\n\\nRunning: {running}\\nSearch: OK (bundled)\\nAuto-updates: enabled\\n"; exit 0; fi\n'
        "exit 1\n")
    os.chmod(Path(stub, "claude"), 0o755)
    return sh("./baseline.sh", env={"PATH": stub + ":" + os.environ["PATH"]})
rc2, o2, e2 = fake("9.9.9", "native (9.9.8)")
ok(rc2 == 1 and "MISMATCH" in o2 + e2, "baseline.sh exits 1 with MISMATCH when the two versions disagree",
   f"when claude --version says 9.9.9 but doctor runs 9.9.8, baseline.sh must print MISMATCH and exit 1 - got exit {rc2}")
rc3, o3, _ = fake("9.9.9", "native (9.9.9)")
ok(rc3 == 0 and "search: OK (bundled)" in o3, "baseline.sh exits 0 when they agree", f"with matching versions baseline.sh should exit 0 - got {rc3}")
PYEOF
```

## What you learned

- `claude doctor` prints install method, running version, search backend, and update status without starting a session.
- A scripted baseline in key: value lines can be diffed the day something breaks.
- When the version flag and the running build disagree, two installs are competing on your PATH.
