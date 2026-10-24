---
type: task
title: "Write your ask script"
minutes: 13
---

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/02-tools
python -c "import openai; print('openai', openai.__version__)"
```

## What to build

Write `/root/rag-lab/02-tools/ask.py`:

1. A function `ask(question, system=None, model="lab-fast")` that sends the question (and the system message, if given) to the gateway with `temperature=0` and **returns** the reply as a stripped string.
2. When run as a command, `python ask.py QUESTION...` prints the reply. With no arguments it prints `usage: ask.py QUESTION` to stderr and exits with code 2.
3. No key or URL in the code.

Then save one answer:

```bash
python ask.py "In one sentence, what is retrieval-augmented generation?" > /root/rag-lab/02-tools/rag.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Create the client once at the top: `client = OpenAI()`.
- Put the command-line part under `if __name__ == "__main__":` so importing the file doesn't run it.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/02-tools
cat > ask.py <<'EOF'
import sys

from openai import OpenAI

client = OpenAI()


def ask(question, system=None, model="lab-fast"):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": question})
    resp = client.chat.completions.create(model=model, messages=messages, temperature=0)
    return resp.choices[0].message.content.strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: ask.py QUESTION", file=sys.stderr)
        sys.exit(2)
    print(ask(" ".join(sys.argv[1:])))
EOF
python ask.py "In one sentence, what is retrieval-augmented generation?" > rag.txt
cat rag.txt
```

</details>

## Check your work

```bash
D=/root/rag-lab/02-tools; P=$D/ask.py
grep -q 'def ask(' $P 2>/dev/null && echo "✅ ask.py defines ask()" || echo "❌ define a function ask(question, system=None, model=\"lab-fast\") in $P"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $P 2>/dev/null && [ -s $P ] && echo "✅ $P reads the key from the environment" || echo "❌ $P must not contain a key - let the SDK read it from the environment"
[ "$(wc -w < $D/rag.txt 2>/dev/null || echo 0)" -ge 3 ] && echo "✅ rag.txt holds an answer" || echo "❌ save the answer about retrieval-augmented generation to $D/rag.txt"
OUT=$(cd $D && python -c "from ask import ask; r = ask('Reply with the single word: ready'); print(type(r).__name__, r == r.strip(), r)" 2>/dev/null)
echo "$OUT" | grep -q '^str True .' && echo "✅ ask() returns the reply as a stripped string, and importing it runs nothing else" || echo "❌ importing ask and calling ask('...') should return the reply as a stripped string"
(cd $D && python -c "from ask import ask; ask('Say hello', system='You are terse.')" >/dev/null 2>&1) && jq -se 'any(.[]; .ok and .system and .temperature == 0 and .model == "lab-fast" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ ask() sends the system message to lab-fast at temperature 0" || echo "❌ ask(q, system=...) should send a system message to lab-fast with temperature=0"
[ -n "$(cd $D && python ask.py What is DNS 2>/dev/null)" ] && echo "✅ python ask.py QUESTION prints an answer" || echo "❌ python ask.py What is DNS should print the reply"
(cd $D && python ask.py >/dev/null 2>$D/.err); rc=$?; [ $rc = 2 ] && grep -q 'usage' $D/.err && echo "✅ no arguments: usage on stderr, exit 2" || echo "❌ with no arguments print usage to stderr and exit 2 (exit was $rc)"
rm -f $D/.err
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- `OpenAI()` reads the gateway URL and lab key from the environment.
- One `ask()` function with an optional system message covers every later topic.
- `if __name__ == "__main__":` makes a file both an importable module and a command.
