---
type: task
title: "Generate a verified README"
minutes: 30
---

## Set up

Set up creates `/root/mastery/044-docs/textstats.py`: three public functions and one private helper, no docstrings, no README.

```bash
rm -rf /root/mastery/044-docs && mkdir -p /root/mastery/044-docs && cd /root/mastery/044-docs
cat > textstats.py <<'EOF'
import math
import re
from collections import Counter


def _tokens(text):
    return re.findall(r"[a-z']+", text.lower())


def word_count(text):
    return len(_tokens(text))


def top_words(text, n=3):
    return [w for w, _ in Counter(_tokens(text)).most_common(n)]


def reading_time_min(text, wpm=200):
    return max(1, math.ceil(word_count(text) / wpm))
EOF
python3 -c 'import textstats'
```

## What to build

1. Write `verify_readme.py [README.md]` **first**. It exits 1 and prints each problem when:
   - a `` ### `name(params)` `` heading names a function that `textstats.py` doesn't define,
   - its parameters or defaults differ from the source (compare with `ast`),
   - a public function has no heading, or
   - an example fails (or there are none). Run them with `doctest.testfile(path, module_relative=False)`.

   Otherwise it prints `README verified` and exits 0.
2. Run Claude headless with `Read`, `Write`, `Edit`, and `Bash(python3 verify_readme.py)`, saving `docs.json`:
   > Write README.md for textstats.py. Under ## API, give each public function a heading in exactly the form ### `name(params)` with its real parameters and defaults, a one-line description, and a runnable >>> example indented by four spaces (not fenced). Then run python3 verify_readme.py and fix the README until it passes.
3. Don't edit `textstats.py`.

The checker feeds your verifier four broken READMEs: a ghost function, a renamed parameter, a missing section, and a wrong example output. It must reject every one.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `ast.unparse(default)` turns a default value node back into source text such as `3` or `200`.
- `doctest.testfile` returns (failed, attempted) - zero attempted is a problem too.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/044-docs
cat > verify_readme.py <<'EOF'
#!/usr/bin/env python3
"""verify_readme.py [README.md] - every documented signature must match textstats.py, every public function
must be documented, and every example must run. Exit 1 and list the problems otherwise."""
import ast
import doctest
import re
import sys

readme = sys.argv[1] if len(sys.argv) > 1 else "README.md"
doc = open(readme).read()
real = {}
for n in ast.parse(open("textstats.py").read()).body:
    if isinstance(n, ast.FunctionDef) and not n.name.startswith("_"):
        a = n.args
        defaults = [None] * (len(a.args) - len(a.defaults)) + [ast.unparse(d) for d in a.defaults]
        real[n.name] = ", ".join(x.arg + ("" if d is None else "=" + d) for x, d in zip(a.args, defaults))

said = dict(re.findall(r"^### `(\w+)\(([^)]*)\)`", doc, re.M))
problems = [f"{k}({v}) is documented but not defined in textstats.py" for k, v in said.items() if k not in real]
problems += [f"{k}({v}) is documented, but textstats.py has {k}({real[k]})" for k, v in said.items() if k in real and v != real[k]]
problems += [f"{k}({real[k]}) is public but not documented" for k in real if k not in said]
failed, tried = doctest.testfile(readme, module_relative=False, report=True)
if tried == 0:
    problems.append("no >>> examples to run")
elif failed:
    problems.append(f"{failed} of {tried} examples failed")
for p in problems:
    print(f"README: {p}")
print("README verified" if not problems else f"{len(problems)} problem(s)")
sys.exit(1 if problems else 0)
EOF
chmod +x verify_readme.py
claude -p 'Write README.md for textstats.py. Under ## API, give each public function a heading in exactly the form ### `name(params)` with its real parameters and defaults, a one-line description, and a runnable >>> example indented by four spaces (not fenced). Then run python3 verify_readme.py and fix the README until it passes.' --allowedTools Read Write Edit "Bash(python3 verify_readme.py)" --output-format json < /dev/null > docs.json
jq -r .result docs.json
python3 verify_readme.py
```

</details>

## Check your work

```bash
D=/root/mastery/044-docs; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
STATS = 'import math\nimport re\nfrom collections import Counter\n\n\ndef _tokens(text):\n    return re.findall(r"[a-z\']+", text.lower())\n\n\ndef word_count(text):\n    return len(_tokens(text))\n\n\ndef top_words(text, n=3):\n    return [w for w, _ in Counter(_tokens(text)).most_common(n)]\n\n\ndef reading_time_min(text, wpm=200):\n    return max(1, math.ceil(word_count(text) / wpm))'

ok(text("textstats.py").rstrip() == STATS.rstrip(), "textstats.py is unchanged - the docs follow the code", "don't edit textstats.py: document it as it is")
rc, out, err = sh("python3 verify_readme.py")
ok(rc == 0, "verify_readme.py passes on your README", f"verify_readme.py fails:\n{out[-400:]}")
rc, out, err = sh("python3 -m doctest README.md")
ok(rc == 0 and ">>>" in text("README.md"), "python3 -m doctest README.md runs every example", "README.md examples should run cleanly under python3 -m doctest")
doc = text("README.md")
heads = re.findall(r"^### `(\w+)\(", doc, re.M)
ok(sorted(heads) == ["reading_time_min", "top_words", "word_count"], "exactly the three public functions are documented", f"document word_count, top_words, reading_time_min (and not _tokens) - found {heads}")
def try_readme(body):
    with tempfile.TemporaryDirectory() as t:
        Path(t, "R.md").write_text(body)
        return sh([sys.executable, os.path.abspath("verify_readme.py"), str(Path(t, "R.md"))])
ghost = doc + "\n\n### `sentence_count(text)`\n\nNumber of sentences.\n"
rc, out, _ = try_readme(ghost)
ok(rc == 1 and "sentence_count" in out, "the verifier flags a documented function that doesn't exist", f"verify_readme.py should exit 1 and name sentence_count - rc {rc}")
wrongsig = doc.replace("### `top_words(text, n=3)`", "### `top_words(text, limit=3)`")
rc, out, _ = try_readme(wrongsig) if wrongsig != doc else (0, "", "")
ok(wrongsig != doc and rc == 1 and "top_words" in out, "the verifier flags a wrong parameter name", "verify_readme.py should exit 1 when top_words is documented as top_words(text, limit=3)")
missing = re.sub(r"### `reading_time_min\(.*?(?=\n### |\Z)", "", doc, flags=re.S)
rc, out, _ = try_readme(missing)
ok(missing != doc and rc == 1 and "reading_time_min" in out, "the verifier flags an undocumented public function", "verify_readme.py should exit 1 when reading_time_min has no section")
badex = doc.replace("['b', 'a']", "['a', 'b']")
rc, out, _ = try_readme(badex) if badex != doc else (0, "", "")
ok(badex != doc and rc == 1, "the verifier fails when an example's output is wrong", "verify_readme.py should run the examples and exit 1 when one fails (keep the top_words example)")
rows = run_rows("docs.json")
ran = result_for(rows, lambda u: u.get("name") == "Bash" and "verify_readme.py" in (u.get("input") or {}).get("command", ""))
ok(ran, "Claude ran the verifier itself during the job", "let Claude run python3 verify_readme.py in the same run (allow Bash(python3 verify_readme.py))")
PYEOF
```

## What you learned

- Generated documentation is only trustworthy when every claim is mechanically checked.
- Signatures via ast, coverage via set comparison, examples via doctest.
- Write the verifier first and let the agent iterate against it.
