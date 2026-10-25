---
type: task
title: "Migrate markdownlite from v1 to v2"
minutes: 30
---

## Set up

Set up creates `/root/mastery/042-migrate`: an app that renders Markdown with the vendored `markdownlite` 1.4.2, tests, a `sample.md`, and `snapshot.py`. The 2.0.0 copy and its release notes wait in `vendor-next/`.

```bash
rm -rf /root/mastery/042-migrate && mkdir -p /root/mastery/042-migrate/app /root/mastery/042-migrate/tests /root/mastery/042-migrate/vendor/markdownlite /root/mastery/042-migrate/vendor-next/markdownlite && cd /root/mastery/042-migrate
cat > vendor/markdownlite/__init__.py <<'EOF'
"""markdownlite 1.4.2 - a tiny Markdown subset: headings, paragraphs, **bold**, `code`."""
import html
import re

__version__ = "1.4.2"


def _inline(text, safe):
    if safe:
        text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", text)


def _slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def render(text, safe=True):
    out = []
    for block in [b.strip() for b in text.split("\n\n") if b.strip()]:
        m = re.match(r"(#{1,6}) (.*)", block)
        if m:
            n = len(m.group(1))
            out.append(f'<h{n} id="{_slug(m.group(2))}">{_inline(m.group(2), safe)}</h{n}>')
        else:
            out.append(f"<p>{_inline(' '.join(block.split()), safe)}</p>")
    return "\n".join(out)


def render_inline(text, safe=True):
    return _inline(text, safe)


def toc(text):
    return [{"level": len(m.group(1)), "title": m.group(2), "anchor": _slug(m.group(2))}
            for m in re.finditer(r"^(#{1,6}) (.*)$", text, re.M)]
EOF
cat > vendor-next/markdownlite/__init__.py <<'EOF'
"""markdownlite 2.0.0 - see RELEASE_NOTES.md for the breaking changes from 1.x."""
import html
import re
from collections import namedtuple

__version__ = "2.0.0"
Heading = namedtuple("Heading", "level title slug")


def _inline(text, escape_html):
    if escape_html:
        text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", text)


def _slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def render(text, *, escape_html=True, inline=False):
    if inline:
        return _inline(text, escape_html)
    out = []
    for block in [b.strip() for b in text.split("\n\n") if b.strip()]:
        m = re.match(r"(#{1,6}) (.*)", block)
        if m:
            n = len(m.group(1))
            out.append(f'<h{n} id="{_slug(m.group(2))}">{_inline(m.group(2), escape_html)}</h{n}>')
        else:
            out.append(f"<p>{_inline(' '.join(block.split()), escape_html)}</p>")
    return "\n".join(out)


def toc(text):
    return [Heading(len(m.group(1)), m.group(2), _slug(m.group(2))) for m in re.finditer(r"^(#{1,6}) (.*)$", text, re.M)]
EOF
cat > vendor-next/markdownlite/RELEASE_NOTES.md <<'EOF'
# markdownlite 2.0.0 release notes

## Breaking changes

1. `render(text, safe=...)`: the `safe` argument is renamed `escape_html` and is keyword-only. Passing `safe` raises `TypeError`.
2. `render_inline(text)` is removed. Use `render(text, inline=True)`.
3. `toc(text)` returns `Heading(level, title, slug)` named tuples instead of dicts. The `anchor` key is now the `slug` attribute (same value).

## Unchanged

Block and inline HTML output, and the slug algorithm, are byte-for-byte identical to 1.4.2.
EOF
echo 'markdownlite==1.4.2' > vendor/VERSIONS.txt
cat > app/__init__.py <<'EOF'
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vendor"))
EOF
cat > app/docs.py <<'EOF'
import markdownlite


def page(md):
    return markdownlite.render(md, safe=True)


def teaser(md_line):
    return markdownlite.render_inline(md_line, safe=True)


def nav(md):
    return [f'<a href="#{h["anchor"]}">{h["title"]}</a>' for h in markdownlite.toc(md) if h["level"] <= 2]
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_docs.py <<'EOF'
import unittest

from app.docs import nav, page, teaser


class DocsTest(unittest.TestCase):
    def test_page_escapes_html(self):
        self.assertEqual(page("# Hi <b>\n\nUse **bold**."), '<h1 id="hi-b">Hi &lt;b&gt;</h1>\n<p>Use <strong>bold</strong>.</p>')

    def test_teaser(self):
        self.assertEqual(teaser("Run `make` **now**"), "Run <code>make</code> <strong>now</strong>")

    def test_nav_skips_deep_headings(self):
        self.assertEqual(nav("# A\n\n## B c\n\n### D"), ['<a href="#a">A</a>', '<a href="#b-c">B c</a>'])
EOF
cat > sample.md <<'EOF'
# Release guide

Ship with `make release` and **never** on Fridays <please>.

## Before you start

Check the changelog & the CI status.

### Deep detail

Ignored by the nav.
EOF
cat > snapshot.py <<'EOF'
"""snapshot.py - print the app's rendering of sample.md: the golden output for the migration."""
from app.docs import nav, page, teaser

md = open("sample.md").read()
print(page(md))
print(teaser(md.splitlines()[2]))
print("\n".join(nav(md)))
EOF
python3 -m unittest -q
```

## What to build

Upgrade `markdownlite` to 2.0.0 in the order from the lesson.

1. Confirm the tests are green, then capture `python3 snapshot.py > golden-v1.html`.
2. Read `vendor-next/markdownlite/RELEASE_NOTES.md`, and grep `app/` for each affected API.
3. Replace `vendor/markdownlite` with the 2.0.0 copy and update `vendor/VERSIONS.txt`. Run the tests and save the failures.
4. Run Claude headless with `Read`, `Edit`, and the test command, saving `migrate.json`. (The notes are in `vendor/markdownlite/` after the swap.)
   > We upgraded markdownlite from 1.4.2 to 2.0.0. vendor/markdownlite/RELEASE_NOTES.md lists the breaking changes. Update app/docs.py to the 2.x API. Change only what the release notes require, then run the tests.
5. Prove it: tests green, `diff golden-v1.html <(python3 snapshot.py)` empty. Remove `vendor-next/`, and write `MIGRATION.md` mapping each breaking change to where it was handled.

The checker scans `app/docs.py` for removed APIs and renders a hidden input through your migrated app and through the original 1.4.2 code: the outputs must match.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Capture the golden file before the swap; after it, the old behavior is gone.
- All three breaking changes touch app/docs.py; nothing else in the app needs to change.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/042-migrate
python3 -m unittest -q                         # 1. green on 1.4.2
python3 snapshot.py > golden-v1.html           # 2. capture behavior
cat vendor-next/markdownlite/RELEASE_NOTES.md  # 3. read the notes
grep -n "safe=\|render_inline\|anchor" app/*.py
rm -rf vendor/markdownlite && cp -R vendor-next/markdownlite vendor/markdownlite   # 4. swap the pin
echo 'markdownlite==2.0.0' > vendor/VERSIONS.txt
python3 -m unittest -q 2> failures-after-swap.txt || tail -3 failures-after-swap.txt   # expected: errors
claude -p 'We upgraded markdownlite from 1.4.2 to 2.0.0. vendor/markdownlite/RELEASE_NOTES.md lists the breaking changes. Update app/docs.py to the 2.x API. Change only what the release notes require, then run the tests.' --allowedTools Read Edit "Bash(python3 -m unittest *)" --output-format json < /dev/null > migrate.json
jq -r .result migrate.json
python3 -m unittest -q && diff golden-v1.html <(python3 snapshot.py) && echo "golden output identical"
rm -rf vendor-next
cat > MIGRATION.md <<'EOF'
# Migration: markdownlite 1.4.2 -> 2.0.0

| Breaking change | Where handled |
|---|---|
| `safe=` renamed `escape_html=` (keyword-only) | `app/docs.py` `page()` and `teaser()` |
| `render_inline()` removed, use `render(..., inline=True)` | `app/docs.py` `teaser()` |
| `toc()` returns `Heading` tuples; `anchor` is now `slug` | `app/docs.py` `nav()` |

Proof: tests green, and `python3 snapshot.py` is byte-identical to `golden-v1.html`.
EOF
```

</details>

## Check your work

```bash
D=/root/mastery/042-migrate; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def rtext(b):
    c = b.get("content")
    return c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))
def result_for(rows, pred):
    ids = [u["id"] for u in uses(rows) if pred(u)]
    return [b for b in results(rows) if b.get("tool_use_id") in ids]
def run_rows(p):
    env = load(p) or {}
    return transcript(env.get("session_id") or "none")[1]
V1 = '"""markdownlite 1.4.2 - a tiny Markdown subset: headings, paragraphs, **bold**, `code`."""\nimport html\nimport re\n\n__version__ = "1.4.2"\n\n\ndef _inline(text, safe):\n    if safe:\n        text = html.escape(text, quote=False)\n    text = re.sub(r"\\*\\*(.+?)\\*\\*", r"<strong>\\1</strong>", text)\n    return re.sub(r"`(.+?)`", r"<code>\\1</code>", text)\n\n\ndef _slug(title):\n    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")\n\n\ndef render(text, safe=True):\n    out = []\n    for block in [b.strip() for b in text.split("\\n\\n") if b.strip()]:\n        m = re.match(r"(#{1,6}) (.*)", block)\n        if m:\n            n = len(m.group(1))\n            out.append(f\'<h{n} id="{_slug(m.group(2))}">{_inline(m.group(2), safe)}</h{n}>\')\n        else:\n            out.append(f"<p>{_inline(\' \'.join(block.split()), safe)}</p>")\n    return "\\n".join(out)\n\n\ndef render_inline(text, safe=True):\n    return _inline(text, safe)\n\n\ndef toc(text):\n    return [{"level": len(m.group(1)), "title": m.group(2), "anchor": _slug(m.group(2))}\n            for m in re.finditer(r"^(#{1,6}) (.*)$", text, re.M)]'
DOCS1 = 'import markdownlite\n\n\ndef page(md):\n    return markdownlite.render(md, safe=True)\n\n\ndef teaser(md_line):\n    return markdownlite.render_inline(md_line, safe=True)\n\n\ndef nav(md):\n    return [f\'<a href="#{h["anchor"]}">{h["title"]}</a>\' for h in markdownlite.toc(md) if h["level"] <= 2]'
SAMPLE = '# Release guide\n\nShip with `make release` and **never** on Fridays <please>.\n\n## Before you start\n\nCheck the changelog & the CI status.\n\n### Deep detail\n\nIgnored by the nav.'

import ast, types
v = re.search(r'__version__ = "([^"]+)"', text("vendor/markdownlite/__init__.py"))
ok(v and v.group(1) == "2.0.0", "vendor/markdownlite is 2.0.0", f"swap vendor/markdownlite for the 2.0.0 copy - found {v.group(1) if v else 'nothing'}")
ok(text("vendor/VERSIONS.txt").strip() == "markdownlite==2.0.0", "the pin in vendor/VERSIONS.txt says 2.0.0", "update vendor/VERSIONS.txt to markdownlite==2.0.0")
ok(not os.path.exists("vendor-next"), "the staging copy vendor-next/ is removed", "remove vendor-next/ once the swap is done - two copies invite confusion")
src = text("app/docs.py")
try:
    tree = ast.parse(src)
except SyntaxError:
    tree = ast.parse("")
kws = {k.arg for n in ast.walk(tree) if isinstance(n, ast.Call) for k in n.keywords}
attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
subs = {n.slice.value for n in ast.walk(tree) if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)}
left = [x for x, bad in (("safe=", "safe" in kws), ("render_inline", "render_inline" in attrs), ("['anchor']", "anchor" in subs)) if bad]
ok(src and not left, "app/docs.py uses no removed 1.x API", f"app/docs.py still uses {left}")
rc, out, err = sh("python3 -m unittest -q")
ok(rc == 0, "the tests pass on 2.0.0", "tests fail on 2.0.0:\n" + err[-300:])
old = types.ModuleType("markdownlite")
exec(V1, old.__dict__)
sys.modules["markdownlite"] = old
ref = {}
exec(DOCS1, ref)
del sys.modules["markdownlite"]
probe = SAMPLE + "\n\n## Edge & <case>\n\nA `x<y>` and **b** <i>"
want = [ref["page"](probe), ref["teaser"]("**Hi** <you> `c`"), ref["nav"](probe)]
code = "import json, sys; from app.docs import page, teaser, nav; p = sys.argv[1]; print(json.dumps([page(p), teaser('**Hi** <you> `c`'), nav(p)]))"
rc, out, err = sh([sys.executable, "-c", code, probe])
ok(rc == 0 and out.strip() and json.loads(out) == want, "page, teaser, and nav render exactly as on 1.4.2 (hidden input)", f"output changed after the migration: {(out.strip() or err.strip())[-300:]}")
g = text("golden-v1.html")
rc, now, _ = sh("python3 snapshot.py")
ok(g and g == now, "golden-v1.html exists and matches today's snapshot byte for byte", "capture python3 snapshot.py > golden-v1.html before the swap; it must match after")
old2 = types.ModuleType("markdownlite")
exec(V1, old2.__dict__)
sys.modules["markdownlite"] = old2
ref2 = {}
exec(DOCS1, ref2)
md = SAMPLE
golden_v1 = "\n".join([ref2["page"](md), ref2["teaser"](md.splitlines()[2]), "\n".join(ref2["nav"](md))]) + "\n"
del sys.modules["markdownlite"]
ok(g == golden_v1, "the golden file was captured from 1.4.2", "golden-v1.html should be the 1.4.2 output - capture it before swapping")
mg = text("MIGRATION.md").lower()
need = ["escape_html", "render_inline", "slug"]
ok(mg and all(n in mg for n in need), "MIGRATION.md maps each breaking change to where it was handled", f"MIGRATION.md should mention {[n for n in need if n not in mg]}")
rows = run_rows("migrate.json")
rd = {os.path.basename((u.get("input") or {}).get("file_path", "")) for u in uses(rows) if u.get("name") == "Read"}
ok("RELEASE_NOTES.md" in rd, "Claude read the release notes before migrating", "migrate.json should come from a run that read the release notes - point the prompt at them")
PYEOF
```

## What you learned

- Upgrade in order: green, capture, read notes, swap, migrate, prove, document.
- Point the agent at the release notes; its memory of a library is often a version behind.
- Golden output catches behavior changes tests never thought to assert.
