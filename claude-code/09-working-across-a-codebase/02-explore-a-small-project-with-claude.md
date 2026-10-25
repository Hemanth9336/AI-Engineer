---
type: task
title: "Explore a small project with Claude"
minutes: 12
---

## Set up

Set up creates a small `shop` package with tests in `/root/cc-lab/09-codebase`. A badly named function, `get_usr`, is used across several files - some through `from shop.users import get_usr`, some through `users.get_usr(...)`.

```bash
mkdir -p /root/cc-lab/09-codebase && cd /root/cc-lab/09-codebase
if [ ! -d shop ]; then
mkdir -p shop tests
cat > shop/__init__.py <<'EOF'

EOF
cat > shop/users.py <<'EOF'
USERS = {
    1: {"name": "Ada", "email": "ada@example.com"},
    2: {"name": "Linus", "email": "linus@example.com"},
}


def get_usr(uid):
    """Return the user dict for uid, or raise KeyError."""
    return USERS[uid]
EOF
cat > shop/orders.py <<'EOF'
from shop.users import get_usr


def order_summary(order):
    user = get_usr(order["user_id"])
    return f"{user['name']}: {len(order['items'])} item(s)"
EOF
cat > shop/emails.py <<'EOF'
from shop import users


def recipient(uid):
    return users.get_usr(uid)["email"]


def greeting(uid):
    return f"Hi {users.get_usr(uid)['name']},"
EOF
cat > shop/reports.py <<'EOF'
def total_items(orders):
    return sum(len(o["items"]) for o in orders)
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_shop.py <<'EOF'
import unittest

from shop.emails import greeting, recipient
from shop.orders import order_summary
from shop.users import get_usr


class ShopTest(unittest.TestCase):
    def test_user(self):
        self.assertEqual(get_usr(1)["name"], "Ada")

    def test_summary(self):
        self.assertEqual(order_summary({"user_id": 2, "items": [1, 2]}), "Linus: 2 item(s)")

    def test_email(self):
        self.assertEqual(recipient(1), "ada@example.com")
        self.assertEqual(greeting(2), "Hi Linus,")


if __name__ == "__main__":
    unittest.main()
EOF
git init -q && git symbolic-ref HEAD refs/heads/main
git config user.name "Lab Learner"
git config user.email "learner@example.com"
git add . && git commit -qm "initial: shop package"
fi
python3 -m unittest discover -s tests -q
claude --version
```

## What to build

1. **Explore:** ask Claude which files mention `get_usr` and save the list to `callers.txt`.
2. **Change:** have it rename `get_usr` to `get_user` everywhere, and run the tests.
3. **Review:** make sure nothing was left behind.

```bash
cd /root/cc-lab/09-codebase
claude -p "Which files in this project mention get_usr? List their paths relative to this folder, one per line, sorted, nothing else." --allowedTools "Bash(grep:*)" > callers.txt
cat callers.txt
claude -p "Rename the function get_usr to get_user everywhere in this project - the definition, imports, calls and tests. Then run python3 -m unittest discover -s tests -q to confirm." \
  --permission-mode acceptEdits --allowedTools "Bash(grep:*)" "Bash(python3 -m unittest:*)" --max-turns 20
grep -rn get_usr --include='*.py' . || echo "no get_usr left"
git diff --stat
python3 -m unittest discover -s tests -q
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `users.get_usr(uid)` is a use too - a rename that only fixes `from ... import get_usr` leaves it broken.
- Read access is allowed by default; Bash commands like grep must be allowed with `--allowedTools` in `-p` mode.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/09-codebase
claude -p "Which files in this project mention get_usr? List their paths relative to this folder, one per line, sorted, nothing else." --allowedTools "Bash(grep:*)" > callers.txt
cat callers.txt
claude -p "Rename the function get_usr to get_user everywhere in this project - the definition, imports, calls and tests. Then run python3 -m unittest discover -s tests -q to confirm." \
  --permission-mode acceptEdits --allowedTools "Bash(grep:*)" "Bash(python3 -m unittest:*)" --max-turns 20
grep -rn get_usr --include='*.py' . || echo "no get_usr left"
git diff --stat
python3 -m unittest discover -s tests -q
```

</details>

## Check your work

```bash
D=/root/cc-lab/09-codebase; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
got = sorted(l.strip().removeprefix("./") for l in text("callers.txt").splitlines() if l.strip())
want = ["shop/emails.py", "shop/orders.py", "shop/users.py", "tests/test_shop.py"]
ok(got == want, "callers.txt lists exactly the four files that used get_usr", f"callers.txt should list {want} - got {got}")
left = [str(p) for p in Path(".").rglob("*.py") if "get_usr" in text(p)]
ok(not left, "no Python file mentions get_usr any more", f"get_usr is still in {left}")
ok(re.search(r"^def get_user\(", text("shop/users.py"), re.M), "shop/users.py defines get_user", "shop/users.py should define get_user")
rc, out, err = sh([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"])
ok(rc == 0, "the tests pass after the rename", "tests fail after the rename: " + err[-300:])
rc, out, err = sh([sys.executable, "-c", "from shop.emails import greeting, recipient; from shop.orders import order_summary; print(greeting(1), recipient(2), order_summary({'user_id': 1, 'items': [1]}))"])
ok(rc == 0 and out.strip() == "Hi Ada, linus@example.com Ada: 1 item(s)", "every caller works through the new name (including users.get_user)", f"calling the shop functions failed: {(out + err)[-200:]}")
hits = [rows for rows in ran(r"Rename the function get_usr to get_user") if len({json.dumps(u["input"].get("file_path")) for u in uses(rows) if u.get("name") in ("Edit", "Write")}) >= 3]
ok(hits, "Claude Code made the coordinated edits across several files", "no session here where Claude renamed get_usr across at least three files")
PYEOF
```

## What you learned

- Claude explores a repo with searches and selective reads, not by loading everything.
- Ask questions first - answers come with paths you can check.
- Review a multi-file change with `git diff --stat`, a leftover search and the tests.
