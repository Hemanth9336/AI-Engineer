---
type: task
title: "Map a seeded repo into a notes file"
minutes: 23
---

## Set up

Set up creates `/root/mastery/003-ledgerly`, a small Python bookkeeping app called **ledgerly** spread over 23 files.

```bash
mkdir -p /root/mastery/003-ledgerly && cd /root/mastery/003-ledgerly
mkdir -p config docs src/ledgerly/tax src/ledgerly/export tests scripts
cat > pyproject.toml <<'EOF'
[project]
name = "ledgerly"
version = "0.4.2"

[project.scripts]
ledgerly = "ledgerly.cli:main"
EOF
cat > README.md <<'EOF'
# ledgerly

Small-business bookkeeping. See docs/.
EOF
cat > config/settings.toml <<'EOF'
[server]
host = "0.0.0.0"
port = 8742

[export]
format = "csv"
EOF
cat > config/logging.toml <<'EOF'
[logging]
level = "INFO"
EOF
cat > docs/architecture.md <<'EOF'
# Architecture

The CLI calls services in src/ledgerly.
EOF
cat > src/ledgerly/__init__.py <<'EOF'
__version__ = "0.4.2"
EOF
cat > src/ledgerly/__main__.py <<'EOF'
from ledgerly.cli import main

main()
EOF
cat > src/ledgerly/cli.py <<'EOF'
import argparse

from ledgerly import reports


def main(argv=None):
    p = argparse.ArgumentParser(prog="ledgerly")
    p.add_argument("command", choices=["report", "export"])
    args = p.parse_args(argv)
    print(reports.run(args.command))
EOF
cat > src/ledgerly/db.py <<'EOF'
import os


def connect():
    url = os.environ["LEDGERLY_DB_URL"]
    return url
EOF
cat > src/ledgerly/money.py <<'EOF'
def cents(amount):
    return round(amount * 100)
EOF
cat > src/ledgerly/reports.py <<'EOF'
from ledgerly.tax.vat import compute_vat


def run(kind):
    return f"{kind}: vat={compute_vat(100)}"
EOF
cat > src/ledgerly/tax/__init__.py <<'EOF'

EOF
cat > src/ledgerly/tax/vat.py <<'EOF'
RATE = 0.2


def compute_vat(net):
    return round(net * RATE, 2)
EOF
cat > src/ledgerly/tax/rates.py <<'EOF'
RATES = {"standard": 0.2, "reduced": 0.05}
EOF
cat > src/ledgerly/export/__init__.py <<'EOF'

EOF
cat > src/ledgerly/export/csv_out.py <<'EOF'
def write(rows):
    return '\n'.join(','.join(map(str, r)) for r in rows)
EOF
cat > src/ledgerly/export/pdf_out.py <<'EOF'
def write(rows):
    raise NotImplementedError
EOF
cat > tests/test_cli.py <<'EOF'
def test_cli():
    pass
EOF
cat > tests/test_vat.py <<'EOF'
from ledgerly.tax.vat import compute_vat


def test_vat():
    assert compute_vat(100) == 20
EOF
cat > tests/test_db.py <<'EOF'
def test_db():
    pass
EOF
cat > tests/test_reports.py <<'EOF'
def test_reports():
    pass
EOF
cat > tests/conftest.py <<'EOF'

EOF
cat > scripts/release.sh <<'EOF'
#!/bin/sh
echo release
EOF
```

## What to build

Map ledgerly without changing it, and save the facts to `/root/mastery/003-ledgerly/NOTES.md`.

1. From inside the folder, run one headless prompt that restores the dedicated search tools and pre-approves only the read-only trio: `--allowedTools "Read Grep Glob"`.
2. Ask for exactly these five `key: value` lines and redirect the reply into `NOTES.md`:

```text
entrypoint: <path of the file that defines main()>
port: <the server port in the config>
vat_function: <file path>:<name of the function that computes VAT>
db_env_var: <the environment variable the database code reads>
test_files: <how many tests/test_*.py files exist>
```

3. Spot-check two of the facts yourself with `grep` or `ls` before you submit. The checker verifies every line against the source.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Paths are relative to the repo folder, for example `src/ledgerly/cli.py`.
- `conftest.py` is not a `test_*.py` file.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/003-ledgerly
claude -p "Map this repo using only read-only tools. Reply with exactly these five lines and nothing else:
entrypoint: <path of the file that defines main()>
port: <the server port in the config>
vat_function: <file path>:<name of the function that computes VAT>
db_env_var: <the environment variable the database code reads>
test_files: <how many tests/test_*.py files exist>" --allowedTools "Read Grep Glob" > NOTES.md
cat NOTES.md
```

</details>

## Check your work

```bash
D=/root/mastery/003-ledgerly; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
notes = {}
for line in text("NOTES.md").splitlines():
    k, _, v = line.partition(":")
    if v:
        notes[k.strip()] = v.strip()
src = {p: text(p) for p in glob.glob("src/**/*.py", recursive=True)}
main_file = next((p for p, s in src.items() if re.search(r"^def main\(", s, re.M)), None)
ok(main_file and notes.get("entrypoint") == main_file, f"entrypoint is {main_file}", f"entrypoint should be the file that defines main() - NOTES.md says {notes.get('entrypoint')!r}")
port = (re.search(r"^port\s*=\s*(\d+)", text("config/settings.toml"), re.M) or [None, None])[1]
ok(port and notes.get("port") == port, f"port is {port}", f"port should come from config/settings.toml - NOTES.md says {notes.get('port')!r}")
vat = next((f"{p}:{m}" for p, s in src.items() for m in re.findall(r"^def (\w*vat\w*)\(", s, re.M)), None)
got_vat = notes.get("vat_function", "").replace(" ", "")
ok(vat and got_vat == vat, f"vat_function is {vat}", f"vat_function should be <file>:<function> - NOTES.md says {notes.get('vat_function')!r}")
env = sorted({v for s in src.values() for v in re.findall(r"os\.environ\[[\"'](\w+)", s)})
ok(env and notes.get("db_env_var") == env[0], f"db_env_var is {env[0] if env else '?'}", f"db_env_var should be the variable db.py reads - NOTES.md says {notes.get('db_env_var')!r}")
n = len(glob.glob("tests/test_*.py"))
ok(notes.get("test_files") == str(n), f"test_files is {n}", f"test_files should count tests/test_*.py - NOTES.md says {notes.get('test_files')!r}")
used = set()
changed = False
for rows in sessions("."):
    if any("read-only tools" in p for p in prompts(rows)):
        failed = {b.get("tool_use_id") for b in results(rows) if b.get("is_error")}
        names = {u.get("name") for u in uses(rows) if u.get("id") not in failed}
        used |= names
        changed |= bool(names & {"Edit", "Write", "NotebookEdit"})
ok(bool(used & {"Grep", "Glob"}) and not changed, "the mapping run searched with Grep or Glob and changed nothing",
   f"run the mapping with --allowedTools \"Read Grep Glob\" so it can search - tools seen: {sorted(used) or 'no mapping run in this folder'}")
PYEOF
```

## What you learned

- Read, Grep, and Glob inspect without changing anything; on Linux and macOS, Grep and Glob come back when you name them in --allowedTools.
- Ask for facts in a fixed format - each one is then checkable with a single command.
- Exploration runs should leave the repo exactly as they found it.
