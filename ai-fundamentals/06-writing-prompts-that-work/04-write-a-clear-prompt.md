---
type: task
title: "Write a clear prompt"
minutes: 10
---

## Scenario

A teammate sent `Write something about backups.` to a model and got a generic essay. The real job: a short reminder for developers about the new nightly backups. Rewrite the prompt so the first answer is usable.

## Set up

The Set up saves the teammate's vague request so you can compare:

```bash
ailab status
mkdir -p /root/ai-lab/06-prompts
cd /root/ai-lab/06-prompts
cat > vague.json <<'EOF'
{"model": "lab-fast", "messages": [{"role": "user", "content": "Write something about backups."}]}
EOF
```

## What to build

1. Send `vague.json` and save the reply text to `/root/ai-lab/06-prompts/vague-reply.txt`. Read it.
2. Write `/root/ai-lab/06-prompts/clear.json` for `lab-fast` with:
   - a **system** message (at least 8 words) that gives the model a role and names the audience: developers;
   - a **user** message (at least 25 words) that includes these facts: backups run nightly at **02:00 UTC**, they are stored in **s3://acme-backups**, restores are requested in **#ops**; and that asks for **exactly 5 bullet points, each line starting with `- `, and no other text**.
3. Send it, save the response to `clear-response.json` and the reply text to `clear-reply.txt`.

The checker counts the bullet lines in your reply, so the prompt has to really control the format.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Put the role and audience in the system message, the facts and format in the user message.
- Spell the format out literally: `exactly 5 bullet points`, `each line starts with "- "`, `no heading or closing line`.
- If the reply adds an introduction line, tighten the prompt and send it again.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/06-prompts
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @vague.json | jq -r '.choices[0].message.content' > vague-reply.txt
cat > clear.json <<'EOF'
{
  "model": "lab-fast",
  "messages": [
    {"role": "system", "content": "You are a platform engineer writing short, friendly reminders for the developers on your team."},
    {"role": "user", "content": "Write a reminder about our new nightly database backups. Facts: backups run nightly at 02:00 UTC, they are stored in s3://acme-backups, and restores are requested in #ops. Write exactly 5 bullet points, each line starting with '- ', and no other text: no heading, no introduction, no closing line."}
  ]
}
EOF
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @clear.json -o clear-response.json
jq -r '.choices[0].message.content' clear-response.json > clear-reply.txt
cat clear-reply.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/06-prompts; R=$D/clear.json
[ -s $D/vague-reply.txt ] && echo "✅ vague-reply.txt holds the vague prompt's answer" || echo "❌ send vague.json and save the reply text to vague-reply.txt"
jq -e '.model == "lab-fast" and .messages[0].role == "system" and (.messages[0].content | split(" ") | length) >= 8' $R >/dev/null 2>&1 && echo "✅ clear.json starts with a system message of 8+ words" || echo "❌ clear.json needs model lab-fast and a system message of at least 8 words first"
jq -e '.messages[0].content | test("developer"; "i")' $R >/dev/null 2>&1 && echo "✅ the system message names the audience" || echo "❌ name the audience (developers) in the system message"
jq -e '.messages[1].role == "user" and (.messages[1].content | split(" ") | length) >= 25' $R >/dev/null 2>&1 && echo "✅ the user message has 25+ words" || echo "❌ the user message needs at least 25 words"
jq -e '.messages[1].content | test("02:00 UTC") and test("s3://acme-backups") and test("#ops")' $R >/dev/null 2>&1 && echo "✅ the user message includes all three facts" || echo "❌ include 02:00 UTC, s3://acme-backups and #ops in the user message"
jq -e '.messages[1].content | test("5|five"; "i") and test("bullet"; "i")' $R >/dev/null 2>&1 && echo "✅ the user message asks for 5 bullet points" || echo "❌ ask for exactly 5 bullet points"
[ -s $D/clear-reply.txt ] && [ "$(cat $D/clear-reply.txt)" = "$(jq -r '.choices[0].message.content' $D/clear-response.json 2>/dev/null)" ] && echo "✅ clear-reply.txt holds exactly the reply in clear-response.json" || echo "❌ extract .choices[0].message.content from clear-response.json into clear-reply.txt"
N=$(grep -c '^- ' $D/clear-reply.txt 2>/dev/null); [ "${N:-0}" -eq 5 ] && echo "✅ the reply has exactly 5 bullet lines" || echo "❌ the reply has ${N:-0} lines starting with '- ' - tighten the format instructions and send again"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Task, context, audience, format, constraints - each one you leave out is a guess.
- Role and audience go in the system message; facts and format in the user message.
- A strict, literal format instruction gives you output your code can count on.
