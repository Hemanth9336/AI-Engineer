---
type: task
title: "Build a simple chain"
minutes: 13
---

## Scenario

New team members keep asking what common Linux commands do. Build a reusable chain that explains any command in one beginner-friendly sentence.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/20-chain
python -c "import langchain, langchain_openai; print('langchain', langchain.__version__)"
```

## What to build

Write `/root/ai-lab/20-chain/chain.py` that:

1. Builds a `ChatPromptTemplate` with a **system** message (explain Linux commands to beginners in one sentence) and a **human** message containing a `{command}` placeholder.
2. Uses `ChatOpenAI(model="lab-fast", ...)` pointed at the gateway with `base_url=os.environ["OPENAI_BASE_URL"]` - no key in the code.
3. Joins them as `prompt | llm | StrOutputParser()`.
4. Explains the command given on the command line: `python chain.py "df -h"` prints only the explanation.

Save two explanations:

```bash
python chain.py "df -h" > df.txt
python chain.py "tail -f /var/log/syslog" > tail.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Imports: `ChatPromptTemplate` from `langchain_core.prompts`, `StrOutputParser` from `langchain_core.output_parsers`, `ChatOpenAI` from `langchain_openai`.
- `chain.invoke({"command": sys.argv[1]})` returns a string.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/20-chain
cat > chain.py <<'EOF'
import os
import sys

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "You explain Linux commands to beginners in one sentence."),
    ("human", "Explain: {command}"),
])
llm = ChatOpenAI(model="lab-fast", base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"])
chain = prompt | llm | StrOutputParser()

print(chain.invoke({"command": " ".join(sys.argv[1:])}))
EOF
python chain.py "df -h" > df.txt
python chain.py "tail -f /var/log/syslog" > tail.txt
cat df.txt tail.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/20-chain; P=$D/chain.py
grep -q 'ChatPromptTemplate' $P 2>/dev/null && grep -q '{command}' $P && echo "✅ chain.py uses a ChatPromptTemplate with {command}" || echo "❌ build a ChatPromptTemplate with a {command} placeholder"
grep -q 'ChatOpenAI' $P 2>/dev/null && grep -q 'lab-fast' $P && grep -q 'OPENAI_BASE_URL' $P && echo "✅ ChatOpenAI targets lab-fast through the gateway" || echo "❌ use ChatOpenAI(model=\"lab-fast\", base_url=os.environ[\"OPENAI_BASE_URL\"], ...)"
grep -Eq 'prompt *\| *llm *\| *StrOutputParser\(\)' $P 2>/dev/null && echo "✅ the chain is prompt | llm | StrOutputParser()" || echo "❌ join the steps as prompt | llm | StrOutputParser()"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $P 2>/dev/null && [ -s $P ] && echo "✅ $P reads the key from the environment" || echo "❌ $P must not contain a key - let the SDK read it from the environment"
[ "$(wc -w < $D/df.txt 2>/dev/null || echo 0)" -ge 3 ] && [ "$(wc -w < $D/tail.txt 2>/dev/null || echo 0)" -ge 3 ] && echo "✅ df.txt and tail.txt hold explanations" || echo "❌ save the explanations for df -h and tail -f to df.txt and tail.txt"
cd $D && OUT=$(python $P "ls -la" 2>/dev/null); [ -n "$OUT" ] && ! echo "$OUT" | grep -q 'AIMessage\|content=' && echo "✅ it explains a new command as plain text" || echo "❌ python chain.py \"ls -la\" should print just the explanation"
jq -se 'any(.[]; .ok and .model == "lab-fast" and .roles == ["system", "user"] and (.client | test("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged the chain's system + user request" || echo "❌ the gateway has no chain request with a system and a user message"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A chain is `prompt | llm | parser`: template in, string out.
- Prompt templates make one prompt reusable across many inputs.
- Point `ChatOpenAI` at any OpenAI-compatible gateway with `base_url`.
