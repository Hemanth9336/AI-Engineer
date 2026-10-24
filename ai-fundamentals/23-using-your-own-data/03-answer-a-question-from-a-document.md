---
type: task
title: "Answer a question from a document"
minutes: 13
---

## Scenario

The payments team keeps a short runbook. On-call engineers want answers from it - and an honest "not in the document" when it doesn't say, instead of a confident guess.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/23-grounding
cd /root/ai-lab/23-grounding
cat > runbook.md <<'EOF'
# Payments API runbook

The payments API listens on port 8443 behind the internal load balancer lb-pay-01.
It is owned by the payments-core team. On-call rotates every Monday at 10:00 UTC.

To restart it, run: sudo systemctl restart payments-api
Logs are in journald: journalctl -u payments-api --since "15 min ago"

If error rates stay above 5% for 10 minutes, page the payments-core on-call.
EOF
```

## What to build

Write a request for each question below, both for `lab-fast` with `temperature: 0`. Each request's **system** message must contain the full text of `runbook.md` between a `<document>` line and a `</document>` line, tell the model to answer only from the document, and say that if the document doesn't contain the answer it must reply exactly `NOT IN DOCUMENT`. The **user** message is the question.

| File | Question |
|---|---|
| `q1.json` | What port does the payments API listen on? |
| `q2.json` | Who approves database failovers? |

Save the responses to `q1-response.json` and `q2-response.json`, and the replies to `q1.txt` and `q2.txt`.

`q1.txt` must contain `8443`. `q2.txt` must be exactly `NOT IN DOCUMENT` - the runbook doesn't say.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Write a small shell function `ask() {{ ... }}` that takes a file name and a question, so both requests are built the same way.
- `jq -n --arg doc "$(cat runbook.md)" --arg q "$2" '...'` inserts both safely.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/23-grounding
ask() {
  jq -n --arg doc "$(cat runbook.md)" --arg q "$2" '{
    model: "lab-fast",
    temperature: 0,
    messages: [
      {role: "system", content: ("Answer the question using only the document inside <document> tags. If the document does not contain the answer, reply exactly: NOT IN DOCUMENT\n\n<document>\n" + $doc + "\n</document>")},
      {role: "user", content: $q}
    ]
  }' > "$1.json"
  curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @"$1.json" -o "$1-response.json"
  jq -r '.choices[0].message.content' "$1-response.json" > "$1.txt"
  echo "$1: $(cat "$1.txt")"
}
ask q1 "What port does the payments API listen on?"
ask q2 "Who approves database failovers?"
```

</details>

## Check your work

```bash
D=/root/ai-lab/23-grounding
for q in q1 q2; do
  jq -e --arg doc "$(cat $D/runbook.md)" '.model == "lab-fast" and .temperature == 0 and .messages[0].role == "system" and (.messages[0].content | contains("<document>\n" + $doc + "\n</document>"))' $D/$q.json >/dev/null 2>&1 && echo "✅ $q.json grounds lab-fast in the whole runbook at temperature 0" || echo "❌ $q.json needs lab-fast, temperature 0, and the runbook between <document> and </document> in the system message"
  jq -e '.messages[0].content | contains("NOT IN DOCUMENT")' $D/$q.json >/dev/null 2>&1 && echo "✅ $q.json allows NOT IN DOCUMENT" || echo "❌ tell the model to reply exactly NOT IN DOCUMENT when the answer isn't there"
done
jq -e '.messages[-1] == {role: "user", content: "What port does the payments API listen on?"}' $D/q1.json >/dev/null 2>&1 && echo "✅ q1.json asks about the port" || echo "❌ q1.json's user message must be the port question"
jq -e '.messages[-1] == {role: "user", content: "Who approves database failovers?"}' $D/q2.json >/dev/null 2>&1 && echo "✅ q2.json asks about failover approval" || echo "❌ q2.json's user message must be the failover question"
[ -s $D/q1.txt ] && [ "$(cat $D/q1.txt)" = "$(jq -r '.choices[0].message.content' $D/q1-response.json 2>/dev/null)" ] && echo "✅ q1.txt holds exactly the reply in q1-response.json" || echo "❌ extract .choices[0].message.content from q1-response.json into q1.txt"
[ -s $D/q2.txt ] && [ "$(cat $D/q2.txt)" = "$(jq -r '.choices[0].message.content' $D/q2-response.json 2>/dev/null)" ] && echo "✅ q2.txt holds exactly the reply in q2-response.json" || echo "❌ extract .choices[0].message.content from q2-response.json into q2.txt"
grep -q '8443' $D/q1.txt 2>/dev/null && echo "✅ q1 answers 8443 from the runbook" || echo "❌ q1.txt should contain 8443"
[ "$(tr -d '\r' < $D/q2.txt 2>/dev/null | sed 's/[[:space:].]*$//')" = "NOT IN DOCUMENT" ] && echo "✅ q2 admits the runbook doesn't say" || echo "❌ q2.txt should be exactly NOT IN DOCUMENT - got '$(cat $D/q2.txt 2>/dev/null)'"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Grounding = the source in delimiters + 'answer only from it' + an exact 'not found' reply.
- An escape hatch turns a confident guess into an honest, machine-checkable answer.
- Pasting works for small documents; RAG retrieves the relevant pieces for large ones.
