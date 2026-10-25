---
type: task
title: "Review and harden the shop API"
minutes: 30
---

## Set up

Set up creates `/root/mastery/058-shop`, a small `shop` package with a product search, an invoice reader, and a config module. It contains three seeded vulnerabilities in code you own.

```bash
rm -rf /root/mastery/058-shop && mkdir -p /root/mastery/058-shop/shop/invoices /root/mastery/058-shop/tests && cd /root/mastery/058-shop
cat > shop/__init__.py <<'EOF'

EOF
cat > shop/db.py <<'EOF'
import sqlite3


def connect(path=":memory:"):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL)")
    return con


def find_products(con, name):
    query = f"SELECT id, name, price FROM products WHERE name LIKE '%{name}%' ORDER BY id"
    return con.execute(query).fetchall()
EOF
cat > shop/files.py <<'EOF'
from pathlib import Path

INVOICES = Path(__file__).resolve().parent / "invoices"


def read_invoice(invoice_id):
    return (INVOICES / f"{invoice_id}.txt").read_text()
EOF
cat > shop/config.py <<'EOF'
"""Shop settings."""
DB_PATH = "shop.db"
DB_USER = "shop"
DB_PASSWORD = "Winter2026!"
EOF
cat > shop/invoices/INV-1001.txt <<'EOF'
Invoice INV-1001
Teapot x1
Total 30.00 EUR
EOF
cat > tests/__init__.py <<'EOF'

EOF
ls -R shop
```

## What to build

1. Write `review.schema.json`: `findings` is a list of `{id, file, line, cwe, severity, title, fix}`, all required.
2. Run the review **read-only**, with `--tools Read,Grep,Glob --allowedTools Read,Grep,Glob` and `--json-schema`. Save `review.json`, then `jq .structured_output review.json > FINDINGS.json`:
   > Security review of the shop package (code we own): read every module under shop/ and report each vulnerability as a finding with file, line, CWE id, severity, title, and fix. Do not include secret values.
3. Write `tests/test_security.py` **before** fixing. It should exploit each issue:
   - `' OR '1'='1` must match nothing, and a name with an apostrophe must still be found;
   - `../config` and similar ids must raise `ValueError`, while `INV-1001` still reads;
   - `config.db_password()` must return `SHOP_DB_PASSWORD` and raise `RuntimeError` when it's unset.

   Watch the tests fail.
4. Fix all three, with Claude in acceptEdits mode (save `fix.json`) or by hand, until `python3 -m unittest` passes:
   > Fix every finding in FINDINGS.json: parameterized SQL in shop/db.py, a validated contained path in shop/files.py, and config.db_password() reading SHOP_DB_PASSWORD (raise RuntimeError when unset) in shop/config.py. Then run python3 -m unittest.

The checker tries payloads you didn't write: UNION injection, absolute paths, and nested `..`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `(INVOICES / name).resolve()` followed by `INVOICES in path.parents` is the containment check; validating the id format first makes it belt and braces.
- `mock.patch.dict(os.environ, {}, clear=True)` simulates a missing variable in a test.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/058-shop
cat > review.schema.json <<'EOF'
{
  "type": "object",
  "properties": {
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string"
          },
          "file": {
            "type": "string"
          },
          "line": {
            "type": "integer"
          },
          "cwe": {
            "type": "string"
          },
          "severity": {
            "type": "string",
            "enum": [
              "low",
              "medium",
              "high",
              "critical"
            ]
          },
          "title": {
            "type": "string"
          },
          "fix": {
            "type": "string"
          }
        },
        "required": [
          "id",
          "file",
          "line",
          "cwe",
          "severity",
          "title",
          "fix"
        ],
        "additionalProperties": false
      }
    }
  },
  "required": [
    "findings"
  ],
  "additionalProperties": false
}
EOF
claude -p 'Security review of the shop package (code we own): read every module under shop/ and report each vulnerability as a finding with file, line, CWE id, severity, title, and fix. Do not include secret values.' --tools Read,Grep,Glob --allowedTools Read,Grep,Glob --json-schema "$(cat review.schema.json)" --output-format json < /dev/null > review.json
jq .structured_output review.json > FINDINGS.json
jq -r '.findings[] | "\(.id) \(.cwe) \(.file):\(.line) \(.title)"' FINDINGS.json
cat > tests/test_security.py <<'EOF'
import os
import unittest
from unittest import mock

from shop import config
from shop.db import connect, find_products
from shop.files import read_invoice


class SecurityTest(unittest.TestCase):
    def setUp(self):
        self.con = connect()
        self.con.executemany("INSERT INTO products (name, price) VALUES (?, ?)", [("Blue mug", 9.5), ("Red mug", 9.5), ("Teapot", 30.0)])

    def test_search_still_works(self):
        self.assertEqual([r[1] for r in find_products(self.con, "mug")], ["Blue mug", "Red mug"])

    def test_sql_injection_payload_matches_nothing(self):
        self.assertEqual(find_products(self.con, "' OR '1'='1"), [])

    def test_quotes_in_names_are_data(self):
        self.con.execute("INSERT INTO products (name, price) VALUES (?, ?)", ("O'Brien's mug", 12.0))
        self.assertEqual([r[1] for r in find_products(self.con, "O'Brien")], ["O'Brien's mug"])

    def test_invoice_ok(self):
        self.assertIn("Total", read_invoice("INV-1001"))

    def test_traversal_rejected(self):
        for bad in ("../config", "../../etc/passwd", "INV-1001/../../config", "", "a" * 65):
            with self.assertRaises(ValueError):
                read_invoice(bad)

    def test_password_from_env(self):
        with mock.patch.dict(os.environ, {"SHOP_DB_PASSWORD": "from-env"}):
            self.assertEqual(config.db_password(), "from-env")
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                config.db_password()
EOF
python3 -m unittest -q 2>&1 | tail -1 || true
claude -p 'Fix every finding in FINDINGS.json: parameterized SQL in shop/db.py, a validated contained path in shop/files.py, and config.db_password() reading SHOP_DB_PASSWORD (raise RuntimeError when unset) in shop/config.py. Then run python3 -m unittest.' --permission-mode acceptEdits --allowedTools "Bash(python3 -m unittest *)" --output-format json < /dev/null > fix.json
jq -r .result fix.json
python3 -m unittest -q
```

</details>

## Check your work

```bash
D=/root/mastery/058-shop; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
LN = {'db': 11, 'files': 7, 'config': 4}

import importlib, sqlite3
from unittest import mock
fd = (load("FINDINGS.json") or {}).get("findings") or []
want = {("shop/db.py", "CWE-89"): LN["db"], ("shop/files.py", "CWE-22"): LN["files"], ("shop/config.py", "CWE-798"): LN["config"]}
got = {(f.get("file"), f.get("cwe")): f.get("line") for f in fd}
ok(len(fd) == 3 and got == want and all(f.get("fix") and f.get("severity") for f in fd),
   "FINDINGS.json: the three issues with the right file, line, and CWE (89, 22, 798), each with a fix", f"FINDINGS.json should list {want} - got {got}")
ok("Winter2026!" not in text("FINDINGS.json") and "Winter2026!" not in text("review.json"), "the review never repeats the password value", "keep secret values out of findings")
rv = load("review.json") or {}
_, rrows = transcript(rv.get("session_id") or "none")
rt = {u.get("name") for u in uses(rrows)} - {"StructuredOutput"}
ok(rrows and rt <= {"Read", "Grep", "Glob"}, "the review run was read-only", f"run the review with only Read, Grep, and Glob - it used {sorted(rt)}")
sys.path.insert(0, os.getcwd())
for m in [k for k in sys.modules if k == "shop" or k.startswith("shop.")]:
    del sys.modules[m]
db = importlib.import_module("shop.db")
files = importlib.import_module("shop.files")
config = importlib.import_module("shop.config")
con = db.connect()
con.executemany("INSERT INTO products (name, price) VALUES (?, ?)", [("Green bowl", 7.0), ("Bowl set", 21.0), ("Spoon", 2.0)])
def q(s):
    try:
        return [r[1] for r in db.find_products(con, s)]
    except Exception as e:
        return f"error {type(e).__name__}"
ok(q("owl") == ["Green bowl", "Bowl set"] and q("%' UNION SELECT 1, sqlite_version(), 3 --") == [] and q("x' OR 1=1 --") == [],
   "find_products still searches, and injection payloads (OR, UNION) return nothing", f"find_products: search gave {q('owl')}, payloads gave {q('x%27 OR 1=1 --')}")
ok("f\"SELECT" not in text("shop/db.py") and "?" in text("shop/db.py"), "the query is parameterized (no f-string SQL)", "replace the f-string query with a ? placeholder and a parameter tuple")
def inv(s):
    try:
        return files.read_invoice(s)
    except ValueError:
        return "ValueError"
    except Exception as e:
        return f"other {type(e).__name__}"
bad = {s: inv(s) for s in ("../config", "../../../etc/hosts", "INV-1001/../../config", "..", "/etc/hosts", "INV 1001")}
ok("Total 30.00" in inv("INV-1001") and all(v == "ValueError" for v in bad.values()),
   "read_invoice serves a real invoice and raises ValueError for every traversal attempt", f"read_invoice should raise ValueError for traversal - got {bad}")
src = text("shop/config.py")
ok("Winter2026!" not in src, "the hard-coded password is gone from config.py", "remove the literal password from shop/config.py")
with mock.patch.dict(os.environ, {"SHOP_DB_PASSWORD": "hidden-test-value"}):
    v = config.db_password() if hasattr(config, "db_password") else None
with mock.patch.dict(os.environ, {}, clear=True):
    try:
        config.db_password()
        missing = "no error"
    except RuntimeError:
        missing = "RuntimeError"
    except Exception as e:
        missing = type(e).__name__
ok(v == "hidden-test-value" and missing == "RuntimeError", "config.db_password() reads SHOP_DB_PASSWORD and raises RuntimeError when it's unset",
   f"db_password() should return the env value and raise RuntimeError when unset - got {v!r}, {missing}")
t = text("tests/test_security.py")
rc, out, err = sh("python3 -m unittest -q")
ok(rc == 0 and "' OR '1'='1" in t and "../" in t and "SHOP_DB_PASSWORD" in t, "tests/test_security.py exploits all three issues and the suite passes",
   f"write exploit tests (an injection payload, a ../ path, the missing env var) and make them pass - rc {rc}")
PYEOF
```

## What you learned

- A read-only review with a findings schema (file, line, CWE, severity, fix) turns 'looks risky' into tracked, verifiable work.
- Write the exploit as a test first; the fix is done when that test passes and the feature still works.
- A leaked credential is fixed by moving it to the environment and rotating it, not by deleting the line.
