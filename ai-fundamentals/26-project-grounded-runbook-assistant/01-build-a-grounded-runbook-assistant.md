---
type: task
title: "Build a grounded runbook assistant"
minutes: 60
---

## Scenario

**Project.** The payments runbook has grown to many sections, and on-call wants to ask it questions in plain English. Build a small **RAG** assistant: it retrieves the relevant sections, answers only from them, cites them, and says plainly when the runbook doesn't cover the question.

This project brings together grounding and retrieval (topic 23), prompt design (topics 06-11), the SDK (topic 19), and the safety habits of topic 22.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/26-runbook
cd /root/ai-lab/26-runbook
cat > runbook.md <<'EOF'
# Payments platform runbook

## Service overview
The payments API listens on port 8443 behind the load balancer lb-pay-01.
It is owned by the payments-core team and runs on hosts pay-01 to pay-04.

## Deploying
Deploys go through the pipeline only. To roll back, run: deployctl rollback payments-api --to previous
Never deploy on Fridays after 15:00 UTC.

## Restarting
Restart one host at a time with: sudo systemctl restart payments-api
Wait for the health check at /healthz to return 200 before moving to the next host.

## TLS certificates
Certificates expire every 90 days. To rotate the certificate, run: certctl rotate --service payments
Then reload the proxy with: sudo systemctl reload nginx

## Database
The primary database is db-01; the replica is db-02. Replication lag above 30 seconds pages the database on-call.

## Logs
Application logs: journalctl -u payments-api --since "15 min ago"
Proxy logs are in /var/log/nginx/payments.log

## Escalation
Page the payments-core on-call first. If there is no answer in 15 minutes, page the engineering manager.
EOF
```

## What to build

Write `/root/ai-lab/26-runbook/ask_runbook.py`:

```bash
python ask_runbook.py "How do I rotate the TLS certificate?"
```

**Retrieval**: split `runbook.md` into sections at each `## ` heading. Score each section by how many of the question's words (lower-cased, longer than 3 letters) it contains, and keep the **top 2** sections with a score above zero.

**Answer**: send only those sections to `lab-fast` at `temperature: 0`, inside `<runbook>` tags in the system message, with instructions to answer only from them, to quote commands exactly, and to reply exactly `I don't know based on the runbook.` if they don't contain the answer.

**Output**:

- When answered: the answer, then a last line `Sources: <heading>, <heading>` naming the sections that were sent.
- When the runbook doesn't cover it - no section matches, or the model says it doesn't know - print exactly `I don't know based on the runbook.` and nothing else.

No key or URL in the code. Save the answer to the TLS question in `/root/ai-lab/26-runbook/tls.txt`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `re.split(r"^## ", text, flags=re.M)[1:]` gives you the sections; the first line of each is its heading.
- `set(re.findall(r"[a-z0-9]+", s.lower()))` turns text into a set of words; `&` intersects two sets.
- Python's `sorted` is stable, so ties keep the runbook's order.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/26-runbook
cat > ask_runbook.py <<'EOF'
import re
import sys
from pathlib import Path

from openai import OpenAI

RUNBOOK = Path("/root/ai-lab/26-runbook/runbook.md")
DONT_KNOW = "I don't know based on the runbook."
TOP_K = 2


def words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 3}


def sections(text):
    for part in re.split(r"^## ", text, flags=re.M)[1:]:
        yield part.splitlines()[0].strip(), "## " + part.strip()


def retrieve(question):
    q = words(question)
    scored = sorted(((len(q & words(body)), title, body) for title, body in sections(RUNBOOK.read_text())),
                    key=lambda s: -s[0])
    return [(title, body) for score, title, body in scored[:TOP_K] if score > 0]


def main():
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("usage: ask_runbook.py QUESTION", file=sys.stderr)
        sys.exit(2)
    hits = retrieve(question)
    if not hits:
        print(DONT_KNOW)
        return
    context = "\n\n".join(body for _, body in hits)
    system = ("Answer the on-call engineer's question using only the runbook sections inside <runbook> tags. "
              "Quote commands exactly. If the sections do not contain the answer, reply exactly: "
              f"{DONT_KNOW}\n\n<runbook>\n{context}\n</runbook>")
    resp = OpenAI().chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": question}],
    )
    answer = (resp.choices[0].message.content or "").strip()
    if not answer or "don't know based on the runbook" in answer.lower():
        print(DONT_KNOW)
        return
    print(answer)
    print("Sources: " + ", ".join(title for title, _ in hits))


if __name__ == "__main__":
    main()
EOF
python ask_runbook.py "How do I rotate the TLS certificate?" > tls.txt
cat tls.txt
python ask_runbook.py "What is the CEO's phone number?"
```

</details>

## Check your work

```bash
D=/root/ai-lab/26-runbook; P=$D/ask_runbook.py; DK="I don't know based on the runbook."
grep -q 'from openai import OpenAI' $P 2>/dev/null && grep -q '<runbook>' $P && echo "✅ ask_runbook.py uses the SDK and <runbook> tags" || echo "❌ use the OpenAI SDK and put the sections inside <runbook> tags"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $P 2>/dev/null && [ -s $P ] && echo "✅ $P reads the key from the environment" || echo "❌ $P must not contain a key - let the SDK read it from the environment"
grep -qF 'certctl rotate --service payments' $D/tls.txt 2>/dev/null && echo "✅ tls.txt quotes the rotate command exactly" || echo "❌ tls.txt should contain the exact command: certctl rotate --service payments"
tail -1 $D/tls.txt 2>/dev/null | grep -q '^Sources: .*TLS certificates' && echo "✅ tls.txt cites the TLS certificates section" || echo "❌ the last line of tls.txt should be 'Sources: ...' including TLS certificates"
cd $D
OUT=$(python $P "Which port does the payments API listen on?" 2>/dev/null); echo "$OUT" | grep -q '8443' && echo "$OUT" | tail -1 | grep -q '^Sources: .*Service overview' && echo "✅ the port question is answered from Service overview" || echo "❌ 'Which port does the payments API listen on?' should answer 8443 and cite Service overview"
S=$(echo "$OUT" | tail -1 | sed 's/^Sources: //'); [ -n "$S" ] && [ "$(echo "$S" | tr ',' '\n' | grep -c .)" -le 2 ] && echo "✅ at most 2 sections were sent" || echo "❌ send and cite at most the top 2 sections"
OUT=$(python $P "What is the CEO's phone number?" 2>/dev/null); [ "$OUT" = "$DK" ] && echo "✅ an unrelated question gets exactly the don't-know line" || echo "❌ for the CEO's phone number, print exactly: $DK"
OUT=$(python $P "How do I rotate the database password?" 2>/dev/null); [ "$OUT" = "$DK" ] && echo "✅ a related but uncovered question also gets the don't-know line" || echo "❌ 'How do I rotate the database password?' is not covered - print exactly: $DK (got: $(echo "$OUT" | head -1))"
jq -se 'any(.[]; .ok and .model == "lab-fast" and .temperature == 0 and .system and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged grounded lab-fast calls at temperature 0" || echo "❌ the gateway has no lab-fast SDK call at temperature 0 with a system message"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- RAG is retrieval + grounding: pick the relevant sections, then answer only from them.
- Citing sources makes answers checkable and retrieval debuggable.
- An exact don't-know reply, enforced in code, is what makes an assistant trustworthy.
