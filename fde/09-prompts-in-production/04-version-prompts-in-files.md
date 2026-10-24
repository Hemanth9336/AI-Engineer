---
type: task
title: "Version prompts in files"
minutes: 9
---

## Set up

```bash
mkdir -p /root/fde-lab/09-prompts
```

## What to build

Set up versioned prompts under `/root/fde-lab/09-prompts/prompts/support/`:

- `v1.txt` - a short support prompt (anything sensible);
- `v2.txt` - v1 plus one extra rule of your choice;
- `current` - one line: `v2`.

Write `/root/fde-lab/09-prompts/prompts.py` with `load_prompt(name, version=None)` that returns `(version, text)`, using `current` when no version is given and raising `FileNotFoundError` for a version that doesn't exist. Paths must be relative to `prompts.py`'s folder, not the current directory.

Then `versioned_bot.py`, used as `python versioned_bot.py QUESTION [VERSION]`, loads the prompt, calls `lab-fast`, and prints one JSON line: `{"prompt_version": "...", "reply": "..."}`.

```bash
cd /root/fde-lab/09-prompts
python versioned_bot.py "Where is my parcel?"
python versioned_bot.py "Where is my parcel?" v1
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `Path(__file__).parent / "prompts" / name`.
- `(folder / f"{version}.txt").read_text()` already raises FileNotFoundError.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/09-prompts
mkdir -p prompts/support
cat > prompts/support/v1.txt <<'EOF'
You are the support assistant for Meridian Logistics. Answer questions about deliveries, tracking, claims and invoices in plain sentences.
EOF
cp prompts/support/v1.txt prompts/support/v2.txt
echo "If you are not sure of an answer, say so and offer to connect the customer with a human agent." >> prompts/support/v2.txt
echo v2 > prompts/support/current
cat > prompts.py <<'EOF'
from pathlib import Path

PROMPTS = Path(__file__).parent / "prompts"


def load_prompt(name, version=None):
    folder = PROMPTS / name
    version = version or (folder / "current").read_text().strip()
    return version, (folder / f"{version}.txt").read_text()
EOF
cat > versioned_bot.py <<'EOF'
import json
import sys

from openai import OpenAI

from prompts import load_prompt

version, system = load_prompt("support", sys.argv[2] if len(sys.argv) > 2 else None)
resp = OpenAI().chat.completions.create(
    model="lab-fast",
    messages=[{"role": "system", "content": system}, {"role": "user", "content": sys.argv[1]}],
)
print(json.dumps({"prompt_version": version, "reply": resp.choices[0].message.content}))
EOF
python versioned_bot.py "Where is my parcel?"
python versioned_bot.py "Where is my parcel?" v1
```

</details>

## Check your work

```bash
D=/root/fde-lab/09-prompts; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/versioned_bot.py 2>/dev/null && [ -s $D/versioned_bot.py ] && echo "✅ versioned_bot.py reads the key from the environment" || echo "❌ versioned_bot.py must not contain a key - let the SDK read it from the environment"
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
S = Path("prompts/support")
v1 = (S / "v1.txt").read_text() if (S / "v1.txt").exists() else ""
v2 = (S / "v2.txt").read_text() if (S / "v2.txt").exists() else ""
ok(v1.strip() and v2.strip() and v1 != v2 and (S / "current").exists() and (S / "current").read_text().strip() == "v2", "v1, v2 and current (v2) are in place", "create prompts/support/v1.txt, a different v2.txt and current containing v2")
r = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); from prompts import load_prompt; import json; print(json.dumps([load_prompt('support'), load_prompt('support', 'v1')]))", str(Path.cwd())], capture_output=True, text=True, cwd="/tmp")
try:
    a, b = json.loads(r.stdout)
except ValueError:
    a = b = None
ok(a == ["v2", v2] and b == ["v1", v1], "load_prompt returns (version, text) from any working directory", f"load_prompt('support') should return ('v2', v2 text) even when run from another folder - got {r.stdout[:200]!r} {r.stderr[-200:]}")
r = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); from prompts import load_prompt\ntry:\n    load_prompt('support', 'v99')\nexcept FileNotFoundError:\n    print('raised')", str(Path.cwd())], capture_output=True, text=True)
ok(r.stdout.strip() == "raised", "an unknown version raises FileNotFoundError", "load_prompt('support', 'v99') should raise FileNotFoundError")
outs = []
for args in (["Do you deliver on Sundays?"], ["Do you deliver on Sundays?", "v1"]):
    rc, out, err = run("versioned_bot.py", *args)
    try:
        outs.append(json.loads(out))
    except ValueError:
        outs.append({"error": out[:100] + err[-100:]})
ok([o.get("prompt_version") for o in outs] == ["v2", "v1"] and all(o.get("reply") for o in outs), "versioned_bot.py reports the prompt version it used", f"expected prompt_version v2 then v1 with a reply - got {outs}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Never edit a released prompt - add a version and point `current` at it.
- Return and log the prompt version with every request.
- Rollback becomes a one-word change.
