---
type: task
title: "Walk a dict shaped like an API reply"
minutes: 7
---

## Set up

```bash
mkdir -p /root/fde-lab/05-python
cd /root/fde-lab/05-python
cat > reply.json <<'EOF'
{
  "id": "chatcmpl-123",
  "model": "lab-mini",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Your parcel MER-88412 is at the Leeds hub."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 31,
    "completion_tokens": 12,
    "total_tokens": 43
  }
}
EOF
```

## What to build

`reply.json` has the shape of a chat API reply. Write `/root/fde-lab/05-python/walk.py`, used as `python walk.py FILE`, that prints exactly:

```text
model: lab-mini
choices: 1
choice 0 (stop): Your parcel MER-88412 is at the Leeds hub.
tokens: 31 in, 12 out, 43 total
```

- one `choice N (FINISH_REASON): CONTENT` line for **every** item in `choices`;
- if `usage` is missing, print `tokens: unknown` instead of the last line.

```bash
cd /root/fde-lab/05-python
python walk.py reply.json
```

The checker runs it on a reply with several choices and one without `usage`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `for i, c in enumerate(data["choices"]):`
- `u = data.get("usage")` then `if u:`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/05-python
cat > walk.py <<'EOF'
import json
import sys

data = json.load(open(sys.argv[1]))
print(f"model: {data['model']}")
print(f"choices: {len(data['choices'])}")
for i, c in enumerate(data["choices"]):
    print(f"choice {i} ({c['finish_reason']}): {c['message']['content']}")
u = data.get("usage")
if u:
    print(f"tokens: {u['prompt_tokens']} in, {u['completion_tokens']} out, {u['total_tokens']} total")
else:
    print("tokens: unknown")
EOF
python walk.py reply.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/05-python; cd $D 2>/dev/null || echo "❌ create $D"
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
def want(d):
    lines = [f"model: {d['model']}", f"choices: {len(d['choices'])}"]
    lines += [f"choice {i} ({c['finish_reason']}): {c['message']['content']}" for i, c in enumerate(d["choices"])]
    u = d.get("usage")
    lines.append(f"tokens: {u['prompt_tokens']} in, {u['completion_tokens']} out, {u['total_tokens']} total" if u else "tokens: unknown")
    return "\n".join(lines)
rc, out, err = run("walk.py", "reply.json")
ok(rc == 0 and out == want(load("reply.json")), "reply.json is printed correctly", f"for reply.json expected:\n{want(load('reply.json'))}\ngot:\n{out} {err[-200:]}")
d2 = {"model": "lab-smart", "choices": [{"index": i, "message": {"role": "assistant", "content": t}, "finish_reason": f} for i, (t, f) in enumerate([("Option one.", "stop"), ("Option two is longer and", "length"), ("Third.", "stop")])],
      "usage": {"prompt_tokens": 50, "completion_tokens": 18, "total_tokens": 68}}
d3 = {"model": "lab-open", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hi."}, "finish_reason": "stop"}]}
for name, d in (("three choices", d2), ("no usage", d3)):
    Path("/tmp/walk-in.json").write_text(json.dumps(d))
    rc, out, err = run("walk.py", "/tmp/walk-in.json")
    ok(rc == 0 and out == want(d), f"a reply with {name} is printed correctly", f"for a reply with {name} expected:\n{want(d)}\ngot:\n{out} {err[-200:]}")
PYEOF
```

## What you learned

- API replies are dicts holding lists of dicts; read paths like `data["choices"][0]["message"]["content"]`.
- `dict.get()` handles optional fields without crashing.
- Loop over every choice - never assume there is exactly one item.
