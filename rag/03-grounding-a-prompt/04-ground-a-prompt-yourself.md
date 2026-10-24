---
type: task
title: "Ground a prompt yourself"
minutes: 11
---

## Scenario

Northwind's finance team gets the same expense questions every week. You'll build a tool that answers them from the expense policy - and says so plainly when the policy doesn't cover something.

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/03-grounding /root/answers
cd /root/rag-lab/03-grounding
cat > policy.txt <<'EOF'
Northwind expense policy
Submit expenses within 30 days through the finance app, with a photo of every receipt.
Meals while travelling are covered up to $60 per day.
Taxis are covered when no public transport runs, or after 22:00.
Anything over $500 must be approved by the finance team before you pay.
Alcohol is never reimbursed.
EOF
```

## What to build

Write `/root/rag-lab/03-grounding/grounded.py`, used as `python grounded.py DOCUMENT_FILE QUESTION...`:

1. It puts the document in the **system** message inside `<document>` tags, with both rules: answer only from the document, and otherwise reply exactly `I don't know based on the document.`
2. It sends the question as the **user** message to `lab-fast` at `temperature=0`.
3. It prints the answer - or, if the reply is a refusal, exactly `I don't know based on the document.`

Save two answers:

```bash
python grounded.py policy.txt "What is the daily meal allowance when travelling?" > /root/answers/03-known.txt
python grounded.py policy.txt "How much is the mileage rate for using my own car?" > /root/answers/03-unknown.txt
```

The checker also asks your tool questions you haven't seen.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `document = open(sys.argv[1]).read()` and `question = " ".join(sys.argv[2:])`.
- Compare loosely: `if "don't know based on the document" in answer.lower(): answer = REFUSAL`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/03-grounding
cat > grounded.py <<'EOF'
import sys

from openai import OpenAI

REFUSAL = "I don't know based on the document."
client = OpenAI()


def grounded_answer(document, question):
    system = (
        "Answer the question using only the document inside <document> tags. "
        f"If the document does not contain the answer, reply exactly: {REFUSAL}\n\n"
        f"<document>\n{document}\n</document>"
    )
    resp = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": question}],
    )
    answer = resp.choices[0].message.content.strip()
    return REFUSAL if "don't know based on the document" in answer.lower() else answer


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: grounded.py DOCUMENT_FILE QUESTION", file=sys.stderr)
        sys.exit(2)
    print(grounded_answer(open(sys.argv[1]).read(), " ".join(sys.argv[2:])))
EOF
python grounded.py policy.txt "What is the daily meal allowance when travelling?" > /root/answers/03-known.txt
python grounded.py policy.txt "How much is the mileage rate for using my own car?" > /root/answers/03-unknown.txt
cat /root/answers/03-known.txt /root/answers/03-unknown.txt
```

</details>

## Check your work

```bash
D=/root/rag-lab/03-grounding; P=$D/grounded.py; R="I don't know based on the document."
grep -q '<document>' $P 2>/dev/null && grep -qF "$R" $P && echo "✅ grounded.py wraps the document in tags and has the exact refusal" || echo "❌ grounded.py needs <document> tags and the sentence: $R"
grep -q 'temperature' $P 2>/dev/null && echo "✅ grounded.py sets the temperature" || echo "❌ call lab-fast with temperature=0"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $P 2>/dev/null && [ -s $P ] && echo "✅ $P reads the key from the environment" || echo "❌ $P must not contain a key - let the SDK read it from the environment"
grep -q '60' /root/answers/03-known.txt 2>/dev/null && echo "✅ 03-known.txt gives the \$60 meal allowance" || echo "❌ /root/answers/03-known.txt should answer \$60 per day"
[ "$(cat /root/answers/03-unknown.txt 2>/dev/null)" = "$R" ] && echo "✅ 03-unknown.txt is exactly the refusal" || echo "❌ /root/answers/03-unknown.txt should be exactly: $R"
OUT=$(cd $D && python grounded.py policy.txt "Who must approve expenses over \$500?" 2>/dev/null); echo "$OUT" | grep -qi 'finance' && echo "✅ a new question is answered from the policy" || echo "❌ 'Who must approve expenses over \$500?' should be answered from the policy (finance team) - got: $OUT"
OUT=$(cd $D && python grounded.py policy.txt "Can I expense a new laptop bag?" 2>/dev/null); [ "$OUT" = "$R" ] && echo "✅ an uncovered question gets exactly the refusal" || echo "❌ 'Can I expense a new laptop bag?' isn't covered - expected exactly: $R (got: $OUT)"
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and .temperature == 0 and .system and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged a grounded lab-fast call at temperature 0" || echo "❌ the gateway has no lab-fast call at temperature 0 with a system message from your script"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Grounding = instructions + the document in tags + the question, in that order.
- Rule 1: answer only from the document. Rule 2: an exact sentence when it isn't there.
- An exact refusal is something your code can detect and test.
