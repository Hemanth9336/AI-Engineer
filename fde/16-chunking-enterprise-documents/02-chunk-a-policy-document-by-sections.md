---
type: task
title: "Chunk a policy document by sections"
minutes: 9
---

## Set up

```bash
mkdir -p /root/fde-lab/16-chunking
cd /root/fde-lab/16-chunking
cat > shipping-policy.md <<'EOF'
# Meridian Logistics Shipping Policy

## Scope
This policy applies to all parcel and pallet shipments booked through a Meridian business account. Consumer shipments follow the consumer terms on the website.

## Delivery times
Domestic parcels are delivered in 1 to 2 working days. EU parcels take 2 to 4 working days. Pallets are delivered on the booked date in a 4-hour window agreed with the receiver.

## Packaging requirements
Parcels must be packed in a rigid outer box. Fragile items need at least 5 cm of padding on every side. Pallets must be shrink-wrapped and the load must not overhang the pallet edge.

## Damage and loss
Damage must be reported within 7 days of delivery with photos. Lost parcels are confirmed after 10 working days without a tracking update. Compensation is limited to 25 EUR per kilogram unless extra cover was purchased.

## Extra cover
Extra cover raises compensation to the declared value, up to 10,000 EUR per shipment. It costs 1.5 percent of the declared value and must be added when booking.

## Prohibited items
Cash, live animals, weapons and human remains are never accepted. Dangerous goods are accepted only with a declaration and travel by road.

## Complaints
Complaints are acknowledged within 1 working day and answered within 10 working days. Unresolved complaints can be escalated to the customer relations manager.
EOF
```

## What to build

Write `/root/fde-lab/16-chunking/chunk.py`, used as `python chunk.py DOC.md`, that prints a JSON list of chunks, one per `## ` section:

```json
{"id": "shipping-policy#damage-and-loss",
 "heading": "Damage and loss",
 "text": "Meridian Logistics Shipping Policy - Damage and loss\nDamage must be reported within 7 days..."}
```

- The document title is the `# ` line (use the file name without extension if there is none).
- `id` is the file name without extension, `#`, and the heading as a slug: lowercase, runs of anything other than a-z and 0-9 replaced by `-`, no leading or trailing `-`.
- `text` is `<title> - <heading>`, a newline, then the section body with leading and trailing whitespace removed.
- Skip sections with an empty body. Ignore text before the first `## ` heading.

```bash
cd /root/fde-lab/16-chunking
python chunk.py shipping-policy.md > chunks.json
```

Put the logic in a function `chunk(path)` that returns the list - later tasks reuse it.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Collect body lines until the next `## ` line, then flush the section.
- `re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")` makes the slug.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/16-chunking
cat > chunk.py <<'EOF'
import json
import re
import sys
from pathlib import Path


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def chunk(path):
    path = Path(path)
    title, chunks, heading, body = path.stem, [], None, []

    def flush():
        text = "\n".join(body).strip()
        if heading and text:
            chunks.append({"id": f"{path.stem}#{slug(heading)}", "heading": heading, "text": f"{title} - {heading}\n{text}"})

    for line in path.read_text().splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            flush()
            heading, body = line[3:].strip(), []
        else:
            body.append(line)
    flush()
    return chunks


if __name__ == "__main__":
    print(json.dumps(chunk(sys.argv[1]), indent=2))

EOF
python chunk.py shipping-policy.md > chunks.json
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
import re
def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def ref(path):
    path = Path(path)
    title, out, heading, body = path.stem, [], None, []
    def flush():
        t = "\n".join(body).strip()
        if heading and t:
            out.append({"id": f"{path.stem}#{slug(heading)}", "heading": heading, "text": f"{title} - {heading}\n{t}"})
    for line in path.read_text().splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            flush()
            heading, body = line[3:].strip(), []
        else:
            body.append(line)
    flush()
    return out
ok(load("chunks.json") == ref("shipping-policy.md"), "chunks.json has one correct chunk per section", "chunks.json should hold one chunk per ## section with the id, heading and text described")
Path("/tmp/kestrel-card-rules.md").write_text("Intro text before any heading is ignored.\n## Card limits & fees\n\n  Daily limit is 2,000 EUR.\nRaise it in the app.\n\n## Empty section\n\n## Lost cards (24/7)\nCall the hotline immediately.\n")
rc, out, err = run("chunk.py", "/tmp/kestrel-card-rules.md")
try:
    got = json.loads(out)
except ValueError:
    got = None
ok(got == ref("/tmp/kestrel-card-rules.md"), "a document without a title, an empty section and odd headings is chunked correctly", f"expected {ref('/tmp/kestrel-card-rules.md')} - got {out[:300]!r} {err[-150:]}")
PYEOF
```

## What you learned

- Chunk along the document's own sections, not at arbitrary character counts.
- Prepend the title and heading so each chunk makes sense alone.
- Build stable, readable ids from the source and section.
