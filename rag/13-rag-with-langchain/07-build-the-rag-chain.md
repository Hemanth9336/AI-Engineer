---
type: task
title: "Build the RAG chain"
minutes: 10
---

## Set up

```bash
ailab status
mkdir -p /root/answers
cd /root/rag-lab/13-langchain
[ -f retriever.py ] || { echo "retriever.py is missing - finish the previous task first"; false; }
```

## What to build

Write `/root/rag-lab/13-langchain/rag_chain.py`:

1. Import `get_retriever` from your `retriever.py`.
2. Build an LCEL chain: `{"context": retriever (k=3) | format_docs, "question": RunnablePassthrough()} | prompt | ChatOpenAI(model="lab-fast", temperature=0) | StrOutputParser()`. The prompt holds the grounding rules with the refusal `I don't know based on the handbook.` and the excerpts in `<document source="...">` tags.
3. `ask(question)` invokes the chain and returns the answer - or exactly `I don't know based on the handbook.` when the model refuses.
4. `python rag_chain.py QUESTION...` prints `ask(...)`.

```bash
python rag_chain.py "How many vacation days do new employees get?" > /root/answers/13-vacation.txt
```

The checker imports `ask` and tries questions you haven't seen.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Keep `chain` at module level so the checker can find it.
- `ChatPromptTemplate.from_messages([("system", ...), ("human", "{question}")])`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/13-langchain
cat > rag_chain.py <<'EOF'
import sys

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from retriever import get_retriever

REFUSAL = "I don't know based on the handbook."

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the question using only the handbook excerpts below. "
               "If they do not contain the answer, reply exactly: " + REFUSAL + "\n\n{context}"),
    ("human", "{question}"),
])


def format_docs(docs):
    return "\n\n".join(f'<document source="{d.metadata["source"]}">\n{d.page_content}\n</document>' for d in docs)


llm = ChatOpenAI(model="lab-fast", temperature=0)
chain = {"context": get_retriever(k=3) | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()


def ask(question):
    answer = chain.invoke(question).strip()
    return REFUSAL if "don't know based on the handbook" in answer.lower() else answer


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: rag_chain.py QUESTION", file=sys.stderr)
        sys.exit(2)
    print(ask(" ".join(sys.argv[1:])))
EOF
python rag_chain.py "How many vacation days do new employees get?" > /root/answers/13-vacation.txt
cat /root/answers/13-vacation.txt
```

</details>

## Check your work

```bash
D=/root/rag-lab/13-langchain; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/rag_chain.py 2>/dev/null && [ -s $D/rag_chain.py ] && echo "✅ rag_chain.py reads the key from the environment" || echo "❌ rag_chain.py must not contain a key - let the SDK read it from the environment"
grep -q 'ChatPromptTemplate' rag_chain.py 2>/dev/null && grep -q 'RunnablePassthrough' rag_chain.py && grep -q 'StrOutputParser' rag_chain.py && echo "✅ rag_chain.py builds an LCEL chain" || echo "❌ build the chain from ChatPromptTemplate, RunnablePassthrough, ChatOpenAI and StrOutputParser"
grep -q '20' /root/answers/13-vacation.txt 2>/dev/null && echo "✅ 13-vacation.txt says 20 days" || echo "❌ /root/answers/13-vacation.txt should answer 20 vacation days"
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
import importlib
REFUSAL = "I don't know based on the handbook."
os.chdir("/tmp")
sys.path.insert(0, "/root/rag-lab/13-langchain")
m = importlib.import_module("rag_chain")
ok(hasattr(getattr(m, "chain", None), "invoke"), "rag_chain.chain is a Runnable", "define the chain at module level as chain = ...")
for q, want in [("What should I do if my laptop is stolen?", "one hour"), ("How much is the learning budget?", "1,000")]:
    a = m.ask(q)
    ok(want in a, f"ask('{q}') answers from the handbook", f"ask('{q}') should mention {want} - got {a!r}")
a = m.ask("Does the office have a gym?")
ok(a == REFUSAL, "an uncovered question returns exactly the refusal", f"ask('Does the office have a gym?') should return exactly {REFUSAL} - got {a!r}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and .temperature == 0 and .system and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged a grounded lab-fast call at temperature 0" || echo "❌ the gateway has no lab-fast call at temperature 0 with a system message from your script"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- LCEL chains connect Runnables with `|`; a dict runs branches on the same input.
- retriever | format_docs -> prompt -> ChatOpenAI -> StrOutputParser is the standard RAG chain.
- Same grounded prompt and refusal as before - just built from components.
