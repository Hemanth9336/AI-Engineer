---
type: task
title: "Write a role prompt for a real task"
minutes: 11
---

## Scenario

Yesterday's payments incident needs explaining to the finance director, who is not technical and has asked what happened. The engineering write-up is in `incident.txt`.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/09-roles
cd /root/ai-lab/09-roles
cat > incident.txt <<'EOF'
At 14:02 UTC the payments-api pods were OOMKilled after a memory leak shipped in v2.3.1.
p99 latency rose to 9s and 18% of checkout requests failed with 5xx errors for 23 minutes.
We rolled back to v2.3.0 at 14:25 UTC and error rates returned to normal. No payments were charged twice.
EOF
```

## What to build

Write `/root/ai-lab/09-roles/role.json` for `lab-fast`:

1. A **system** message that starts with `You are` and gives the model a role, and that names the audience: the **finance director**, who is **non-technical**.
2. A **user** message that contains the full text of `incident.txt` and asks for an explanation in **under 100 words**, with **no technical jargon**, keeping the facts (23 minutes, 18%) unchanged.

Send it, save the response to `role-response.json` and the reply to `/root/ai-lab/09-roles/explanation.txt`.

The checker reads the explanation: it must be under 130 words, mention the 23 minutes, and contain none of `OOMKilled`, `p99`, `5xx`, `pods`, or `v2.3.1`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Build the user message from the file with `jq --arg inc "$(cat incident.txt)"`.
- Name the jargon you want translated: 'say servers ran out of memory, not OOMKilled'.
- If the reply still contains a technical term, add it to your list and send again.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/09-roles
jq -n --arg inc "$(cat incident.txt)" '{
  model: "lab-fast",
  messages: [
    {role: "system", content: "You are an incident communications lead. You explain technical problems to a non-technical finance director: plain words, calm tone, impact first."},
    {role: "user", content: ("Explain the incident below to our finance director in under 100 words. Use no technical jargon: do not use the words OOMKilled, p99, 5xx, pods or version numbers. Keep the facts exactly: it lasted 23 minutes and 18% of checkout attempts failed.\n\nIncident:\n" + $inc)}
  ]
}' > role.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @role.json -o role-response.json
jq -r '.choices[0].message.content' role-response.json > explanation.txt
cat explanation.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/09-roles; R=$D/role.json; E=$D/explanation.txt
jq -e '.model == "lab-fast" and .messages[0].role == "system" and (.messages[0].content | startswith("You are"))' $R >/dev/null 2>&1 && echo "✅ the system message gives the model a role" || echo "❌ role.json needs model lab-fast and a system message starting with 'You are'"
jq -e '.messages[0].content | test("finance director"; "i") and test("non-technical"; "i")' $R >/dev/null 2>&1 && echo "✅ the system message names the non-technical finance director" || echo "❌ name the audience in the system message: a non-technical finance director"
jq -e --arg inc "$(cat $D/incident.txt)" '.messages[-1].role == "user" and (.messages[-1].content | contains($inc))' $R >/dev/null 2>&1 && echo "✅ the user message carries the whole incident text" || echo "❌ include the full text of incident.txt in the user message"
jq -e '.messages[-1].content | test("100 words") and test("jargon"; "i")' $R >/dev/null 2>&1 && echo "✅ the user message sets the length and bans jargon" || echo "❌ ask for under 100 words and no technical jargon"
[ -s $D/explanation.txt ] && [ "$(cat $D/explanation.txt)" = "$(jq -r '.choices[0].message.content' $D/role-response.json 2>/dev/null)" ] && echo "✅ explanation.txt holds exactly the reply in role-response.json" || echo "❌ extract .choices[0].message.content from role-response.json into explanation.txt"
W=$(wc -w < $E 2>/dev/null || echo 999); [ "$W" -lt 130 ] && echo "✅ the explanation is $W words" || echo "❌ the explanation is $W words - it must be under 130"
grep -q '23' $E 2>/dev/null && echo "✅ the explanation keeps the 23 minutes" || echo "❌ the explanation lost the duration (23 minutes)"
! grep -Eiq 'OOMKilled|p99|5xx|pods|v2\.3\.1' $E 2>/dev/null && [ -s $E ] && echo "✅ the explanation has no jargon" || echo "❌ the explanation still uses jargon: $(grep -Eio 'OOMKilled|p99|5xx|pods|v2\.3\.1' $E 2>/dev/null | sort -u | tr '\n' ' ')"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A role in the system message sets the lens: priorities, vocabulary, and tone.
- Naming the audience precisely changes what detail the model includes.
- Say which facts must stay fixed, and which words to translate, when you reframe.
