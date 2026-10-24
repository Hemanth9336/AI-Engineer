---
type: task
title: "Clean and chunk an ugly export"
minutes: 9
---

## Set up

`wiki-export.txt` is a raw intranet dump with Windows line endings, HTML, breadcrumbs, edit stamps and empty template pages.

```bash
mkdir -p /root/fde-lab/16-chunking
cd /root/fde-lab/16-chunking
python - <<'PYEOF'
open('wiki-export.txt', 'w', newline='').write('==== PAGE: Damage claims ====\r\nHome > Policies > Damage claims\r\n<h2>Damage claims</h2>\r\n<p>Report damage within <b>7&nbsp;days</b> of delivery.</p>\r\n\r\n   Attach photos   of the item and the packaging.  \r\nLast edited by j.smith on 2025-11-02\r\n==== PAGE: New page template ====\r\nHome > Templates\r\nTODO: fill in this page\r\nLast edited by admin on 2024-01-15\r\n==== PAGE: Cold chain ====\r\nHome > Operations > Cold chain\r\n<div class="note">Chilled goods travel between 2 and 8 &deg;C.</div>\r\nTemperature logs &amp; reports are available on request.\r\n==== PAGE: Archive ====\r\nHome > Archive\r\n\r\n   \r\n')
PYEOF
```

## What to build

Write `/root/fde-lab/16-chunking/clean.py`, used as `python clean.py EXPORT_FILE`, that prints a JSON object:

```json
{"pages": [{"page": "Damage claims", "text": "Damage claims\nReport damage within 7 days of delivery.\nAttach photos of the item and the packaging."}],
 "dropped": ["New page template", "Archive"]}
```

Rules, in order:

1. Split the file into pages at lines like `==== PAGE: Title ====`.
2. Strip HTML tags (`<...>`), then decode entities with `html.unescape` (so `&nbsp;` becomes a non-breaking space - treat it as a space).
3. Drop lines that start with `Home >` or `Last edited by`.
4. In each remaining line, collapse runs of whitespace to one space and strip the ends; drop empty lines.
5. The page text is the remaining lines joined with `\n`.
6. Drop the page if its text is empty or starts with `TODO`.

`dropped` lists the titles of dropped pages, in file order.

```bash
cd /root/fde-lab/16-chunking
cat -A wiki-export.txt | head -12      # see the mess, including ^M (Windows line endings)
python clean.py wiki-export.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `re.split(r"^==== PAGE: (.+?) ====$", text, flags=re.M)` gives `['', title1, body1, title2, body2, ...]`.
- Read with `open(path, newline=None)` or `.replace("\r\n", "\n")` to normalise line endings first.
- `" ".join(line.split())` collapses all whitespace, including non-breaking spaces.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/16-chunking
cat > clean.py <<'EOF'
import html
import json
import re
import sys

text = open(sys.argv[1], encoding="utf-8").read().replace("\r\n", "\n")
parts = re.split(r"^==== PAGE: (.+?) ====$", text, flags=re.M)
pages, dropped = [], []
for title, body in zip(parts[1::2], parts[2::2]):
    lines = []
    for line in html.unescape(re.sub(r"<[^>]+>", "", body)).split("\n"):
        if line.startswith(("Home >", "Last edited by")):
            continue
        line = " ".join(line.split())
        if line:
            lines.append(line)
    clean = "\n".join(lines)
    if not clean or clean.startswith("TODO"):
        dropped.append(title)
    else:
        pages.append({"page": title, "text": clean})
print(json.dumps({"pages": pages, "dropped": dropped}, indent=2, ensure_ascii=False))
EOF
python clean.py wiki-export.txt
```

</details>

## Check your work

```bash
D=/root/fde-lab/16-chunking; cd $D 2>/dev/null || echo "❌ create $D"
python - <<'PYEOF'
import json, math, os, subprocess, sys
from pathlib import Path
from openai import OpenAI
_C = OpenAI()
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def E(xs):
    return [d.embedding for d in _C.embeddings.create(model="lab-embed", input=xs).data]
def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def run(*args, cwd=None):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()
import html, re
def ref(path):
    text = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    parts = re.split(r"^==== PAGE: (.+?) ====$", text, flags=re.M)
    pages, dropped = [], []
    for title, body in zip(parts[1::2], parts[2::2]):
        lines = [" ".join(l.split()) for l in html.unescape(re.sub(r"<[^>]+>", "", body)).split("\n") if not l.startswith(("Home >", "Last edited by"))]
        clean = "\n".join(l for l in lines if l)
        (dropped.append(title) if not clean or clean.startswith("TODO") else pages.append({"page": title, "text": clean}))
    return {"pages": pages, "dropped": dropped}
rc, out, err = run("clean.py", "wiki-export.txt")
try:
    got = json.loads(out)
except ValueError:
    got = None
ok(got == ref("wiki-export.txt"), "wiki-export.txt is cleaned: 2 pages kept, the template and empty page dropped", f"expected {ref('wiki-export.txt')} - got {out[:300]!r} {err[-150:]}")

open("/tmp/export2.txt", "w", newline="").write('==== PAGE: Returns ====\r\nHome > Policies > Returns\r\n<p>Business customers can book a return <i>collection</i> up to 30 days after delivery.</p>\r\nLast edited by p.shah on 2026-01-09\r\n==== PAGE: Draft ====\r\nHome > Drafts\r\nTODO: write this\r\n==== PAGE: Weights ====\r\nHome > Operations > Weights\r\n<ul><li>Standard pallets: up to 800&nbsp;kg</li><li>Height: 1.8 m</li></ul>\r\n\r\nHeavier pallets need a freight booking.\r\n')

rc, out, err = run("clean.py", "/tmp/export2.txt")
try:
    got = json.loads(out)
except ValueError:
    got = None
ok(got == ref("/tmp/export2.txt"), "a different export with lists and entities is cleaned correctly", f"expected {ref('/tmp/export2.txt')} - got {out[:300]!r} {err[-150:]}")
PYEOF
```

## What you learned

- Real exports carry boilerplate, markup, entities and empty pages - clean before you chunk.
- Write cleaning as explicit rules you can explain to the customer.
- Count what you dropped - it's often a finding in itself.
