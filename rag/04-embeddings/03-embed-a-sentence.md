---
type: task
title: "Embed a sentence"
minutes: 14
---

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/04-embeddings /root/answers
```

## What to build

Write `/root/rag-lab/04-embeddings/embed.py`, used as `python embed.py SENTENCE OUTFILE`:

1. It embeds SENTENCE with `lab-embed`.
2. It writes OUTFILE as JSON with four keys: `text` (the sentence), `model` (`"lab-embed"`), `dimensions` (the vector length), and `embedding` (the list of numbers).
3. It prints the dimensions and the first 3 numbers.

Then:

```bash
cd /root/rag-lab/04-embeddings
python embed.py "Our backups run every night at 02:00." backup.json
```

and write the vector length - just the number - to `/root/answers/04-dimensions.txt`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `text, out = sys.argv[1], sys.argv[2]`.
- `json.dump({...}, open(out, "w"))` - `dimensions` is `len(vector)`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/04-embeddings
cat > embed.py <<'EOF'
import json
import sys

from openai import OpenAI

client = OpenAI()

if len(sys.argv) != 3:
    print("usage: embed.py SENTENCE OUTFILE", file=sys.stderr)
    sys.exit(2)
text, out = sys.argv[1], sys.argv[2]
vector = client.embeddings.create(model="lab-embed", input=text).data[0].embedding
json.dump({"text": text, "model": "lab-embed", "dimensions": len(vector), "embedding": vector}, open(out, "w"))
print(len(vector), [round(x, 4) for x in vector[:3]])
EOF
python embed.py "Our backups run every night at 02:00." backup.json
python -c "import json; print(json.load(open('backup.json'))['dimensions'])" > /root/answers/04-dimensions.txt
cat /root/answers/04-dimensions.txt
```

</details>

## Check your work

```bash
D=/root/rag-lab/04-embeddings; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/embed.py 2>/dev/null && [ -s $D/embed.py ] && echo "✅ embed.py reads the key from the environment" || echo "❌ embed.py must not contain a key - let the SDK read it from the environment"
[ "$(tr -d '[:space:]' < /root/answers/04-dimensions.txt 2>/dev/null)" = 384 ] && echo "✅ 04-dimensions.txt says 384" || echo "❌ /root/answers/04-dimensions.txt should hold the vector length, 384"
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
d = load("backup.json") or {}
ok(d.get("text") == "Our backups run every night at 02:00." and d.get("model") == "lab-embed", "backup.json has the text and the model", "backup.json needs text = the sentence and model = lab-embed")
v = d.get("embedding") or []
ok(d.get("dimensions") == 384 == len(v), "backup.json holds a 384-number embedding", "backup.json needs dimensions: 384 and a 384-number embedding")
ok(len(v) == 384 and cos(v, E([d.get("text", "")])[0]) > 0.999, "the stored vector is the real lab-embed vector for the sentence", "the embedding in backup.json doesn't match lab-embed's vector for the sentence")
s = "Disk usage on the build server is above ninety percent."
rc, out, err = run("embed.py", s, "unseen.json")
u = load("unseen.json") or {}
ok(rc == 0 and len(u.get("embedding") or []) == 384 and cos(u["embedding"], E([s])[0]) > 0.999, "a new sentence is embedded and saved correctly", f"python embed.py '<new sentence>' unseen.json failed or saved the wrong vector {err[-200:]}")
ok("384" in out, "embed.py prints the dimensions", "embed.py should print the dimensions")
Path("unseen.json").unlink(missing_ok=True)
PYEOF
jq -se 'any(.[]; .ok and .api == "embeddings" and .model == "lab-embed" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-embed calls" || echo "❌ the gateway has no lab-embed call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- An embedding is a fixed-length list of numbers that encodes meaning.
- `client.embeddings.create(model=..., input=...)` - a string or a batch list.
- Store the model name with every vector; only compare vectors from the same model.
