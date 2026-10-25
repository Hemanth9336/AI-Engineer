---
type: task
title: "Build and document a word-count CLI"
minutes: 45
---

## Scenario

Your team wants a tiny, dependable word-count tool for the docs pipeline - and wants it documented so the next person (or the next Claude session) can work on it without asking. You'll build it with Claude Code from a written spec, verify it, and have Claude write the project memory.

## Set up

Set up creates `/root/cc-lab/18-wordcount` with `SPEC.md` - the full specification of the tool - and two sample text files.

```bash
mkdir -p /root/cc-lab/18-wordcount/samples && cd /root/cc-lab/18-wordcount
cat > SPEC.md <<'EOF'
# wordcount spec

Build `wc.py`, a word-count command-line tool, in this folder. Python 3 standard library only.

Usage: `python3 wc.py [--top N] FILE...`

- For each FILE print one line: `<lines> <words> <chars> <FILE>`
  - lines = number of newline characters, words = whitespace-separated words, chars = characters of the file read as UTF-8 (not bytes)
- With more than one FILE, finish with `<lines> <words> <chars> total`
- `--top N` (always given first): after the counts print `top N words:` and then the N most frequent words across all files as `<word> <count>`, most frequent first, ties in alphabetical order. A word is a match of the regex `[a-z0-9']+` in the lowercased text. If there are fewer than N distinct words, print them all.
- If any FILE can't be read: print `wc.py: cannot read FILE` to stderr and exit 1, before printing anything else.
- With no FILE: print `usage: wc.py [--top N] FILE...` to stderr and exit 2.
- Tests in `test_wc.py` (at least three test methods), run with `python3 -m unittest -q`.
EOF
cat > samples/poem.txt <<'EOF'
The cat sat.
The cat ran!
A dog sat, too.
EOF
cat > samples/notes.txt <<'EOF'
Café opens at nine.
The café's wifi is slow.
EOF
claude --version
```

## What to build

Using Claude Code, deliver in `/root/cc-lab/18-wordcount`:

1. `wc.py`, exactly as specified in `SPEC.md` (counts per file, a `total` line, `--top N`, error handling with the right exit codes);
2. `test_wc.py` with at least three test methods, passing with `python3 -m unittest -q`;
3. `CLAUDE.md` with a `## Commands` section (the test command and an example `wc.py` command) and a `## Behaviour` section (output format, `--top`, errors).

Use everything from this skill: a precise brief (the spec is one), a permission mode that lets Claude edit but only run what's needed, running the result yourself, and a memory file at the end. The checker compares your tool with a reference implementation on files it has never seen.

```bash
cd /root/cc-lab/18-wordcount
claude -p "$(cat SPEC.md)" --permission-mode acceptEdits --allowedTools "Bash(python3:*)" --max-turns 20
python3 -m unittest -q
python3 wc.py --top 3 samples/poem.txt samples/notes.txt
claude -p "Write CLAUDE.md for this project with two sections: ## Commands (how to run the tests and an example wc.py command) and ## Behaviour (output format, --top, error handling). Keep it under 30 lines." --permission-mode acceptEdits --max-turns 6
cat CLAUDE.md
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Read the file with `open(name, encoding="utf-8", newline="")` so characters (not bytes) are counted and line endings aren't changed.
- Expected for `python3 wc.py samples/poem.txt`: `2 10 40 samples/poem.txt`.
- If a detail is off, send a precise correction in a new `claude -p` run rather than starting over.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/18-wordcount
claude -p "$(cat SPEC.md)" --permission-mode acceptEdits --allowedTools "Bash(python3:*)" --max-turns 20
python3 -m unittest -q
python3 wc.py --top 3 samples/poem.txt samples/notes.txt
claude -p "Write CLAUDE.md for this project with two sections: ## Commands (how to run the tests and an example wc.py command) and ## Behaviour (output format, --top, error handling). Keep it under 30 lines." --permission-mode acceptEdits --max-turns 6
cat CLAUDE.md
```

</details>

## Check your work

```bash
D=/root/cc-lab/18-wordcount; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
from collections import Counter
def reference(args, files):
    top = None
    if args[:1] == ["--top"]:
        top, args = int(args[1]), args[2:]
    texts = [(n, files[n]) for n in args]
    out, total = [], [0, 0, 0]
    for n, t in texts:
        c = (t.count("\n"), len(t.split()), len(t))
        total = [a + b for a, b in zip(total, c)]
        out.append(f"{c[0]} {c[1]} {c[2]} {n}")
    if len(texts) > 1:
        out.append(f"{total[0]} {total[1]} {total[2]} total")
    if top is not None:
        w = Counter(x for _, t in texts for x in re.findall(r"[a-z0-9']+", t.lower()))
        out.append(f"top {top} words:")
        out += [f"{k} {v}" for k, v in sorted(w.items(), key=lambda kv: (-kv[1], kv[0]))[:top]]
    return "\n".join(out) + "\n"
ok(Path("wc.py").exists(), "wc.py exists", "no wc.py in /root/cc-lab/18-wordcount")
with tempfile.TemporaryDirectory() as t:
    files = {"alpha.txt": "Zebra zebra apple.\nApple pie, apple tart\nend", "beta.txt": "Ünïcode café — naïve\nit's it's IT'S\n\n", "empty.txt": ""}
    for n, body in files.items():
        Path(t, n).write_text(body, encoding="utf-8")
    for args in (["alpha.txt"], ["alpha.txt", "beta.txt", "empty.txt"], ["--top", "3", "alpha.txt", "beta.txt"], ["--top", "50", "beta.txt"]):
        rc, out, err = sh([sys.executable, os.path.abspath("wc.py"), *args], cwd=t)
        want = reference(args, files)
        ok(rc == 0 and out == want, f"python3 wc.py {' '.join(args)} matches the spec", f"python3 wc.py {' '.join(args)} - expected {want!r}, got {(out + err)[:300]!r}")
    rc, out, err = sh([sys.executable, os.path.abspath("wc.py"), "alpha.txt", "missing.txt"], cwd=t)
    ok(rc == 1 and "wc.py: cannot read missing.txt" in err and not out, "an unreadable file: message on stderr, exit 1, nothing on stdout", f"with a missing file: exit {rc}, stdout {out[:80]!r}, stderr {err[:120]!r}")
    rc, out, err = sh([sys.executable, os.path.abspath("wc.py")], cwd=t)
    ok(rc == 2 and "usage: wc.py [--top N] FILE..." in err, "no files: usage on stderr, exit 2", f"with no files: exit {rc}, stderr {err[:120]!r}")
tests = re.findall(r"^\s+def (test_\w+)", text("test_wc.py"), re.M)
rc, out, err = sh([sys.executable, "-m", "unittest", "-q"])
ok(len(tests) >= 3 and rc == 0, f"test_wc.py has {len(tests)} tests and they pass", f"test_wc.py needs at least 3 passing test methods - found {len(tests)}, unittest: {err[-200:]}")
md = text("CLAUDE.md")
secs = {m.group(1).strip().lower(): m.end() for m in re.finditer(r"^##\s+(.+)$", md, re.M)}
cmd_part = md[secs.get("commands", len(md)):]
ok("commands" in secs and "unittest" in cmd_part and "wc.py" in cmd_part, "CLAUDE.md ## Commands has the test command and a wc.py example", "CLAUDE.md needs '## Commands' with python3 -m unittest and an example wc.py command")
ok(any(k.startswith("behavio") for k in secs) and "--top" in md, "CLAUDE.md ## Behaviour documents --top", "CLAUDE.md needs '## Behaviour' describing the output and --top")
hits = [rows for rows in sessions(os.getcwd()) if any(u.get("name") in ("Write", "Edit") and "wc.py" in json.dumps(u.get("input", {}).get("file_path", "")) for u in uses(rows))]
ok(hits, "Claude Code wrote wc.py in a session here", "no session in this folder where Claude wrote wc.py - build it with Claude Code")
PYEOF
```

## What you learned

- A written spec is the best brief: it's precise, reviewable and testable.
- Verify agent-built code against cases it has never seen - including error paths.
- Finish a project by recording commands and behavior in CLAUDE.md.
