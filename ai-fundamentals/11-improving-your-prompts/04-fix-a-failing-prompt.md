---
type: task
title: "Fix a failing prompt"
minutes: 10
---

## Scenario

A monitoring bot forwards alerts to a model and posts the reply to a dashboard that expects exactly one line: `service=<name> status=<up|degraded|down> region=<code>`. The current prompt in `bad.json` returns paragraphs. Fix it.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/11-refine
cd /root/ai-lab/11-refine
printf '%s\n' "ALERT 10:02 UTC: The Payments API is completely down for customers in the EU region. Every request fails." > alert.txt
jq -n --arg a "$(cat alert.txt)" '{model: "lab-fast", messages: [{role: "user", content: ("Tell me about this alert: " + $a)}]}' > bad.json
```

## What to build

1. Send `bad.json` and save its reply to `/root/ai-lab/11-refine/bad-reply.txt`. Read it and note what is wrong.
2. Write `/root/ai-lab/11-refine/fixed.json` for `lab-fast` with **`temperature: 0`**. It must include the full text of `alert.txt`, and get the model to reply with exactly one line in this format, all values lower-case:

```text
service=<name> status=<up|degraded|down> region=<code>
```

3. Send it, save the response to `fixed-response.json` and the reply to `/root/ai-lab/11-refine/fixed-reply.txt`.

For this alert the dashboard expects exactly `service=payments status=down region=eu`. Run the refine loop until you get it.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Put the format rules in a system message and the alert in the user message.
- Show the literal template and list the allowed status values.
- Say 'all values lower-case' and 'output only that one line'.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/11-refine
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @bad.json | jq -r '.choices[0].message.content' > bad-reply.txt
jq -n --arg a "$(cat alert.txt)" '{
  model: "lab-fast",
  temperature: 0,
  messages: [
    {role: "system", content: "You turn monitoring alerts into one status line for a dashboard. Reply with exactly one line in this format and nothing else:\nservice=<service> status=<up|degraded|down> region=<region>\nUse one lower-case word for the service, one of up, degraded or down for the status, and the lower-case region code (for example eu or us). Example: service=search status=degraded region=us"},
    {role: "user", content: $a}
  ]
}' > fixed.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @fixed.json -o fixed-response.json
jq -r '.choices[0].message.content' fixed-response.json > fixed-reply.txt
cat fixed-reply.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/11-refine; R=$D/fixed.json
[ "$(wc -w < $D/bad-reply.txt 2>/dev/null || echo 0)" -ge 5 ] && echo "✅ bad-reply.txt shows what the old prompt returned" || echo "❌ send bad.json and save its reply to bad-reply.txt"
jq -e '.model == "lab-fast" and .temperature == 0' $R >/dev/null 2>&1 && echo "✅ fixed.json uses lab-fast at temperature 0" || echo "❌ fixed.json needs model lab-fast and temperature 0"
jq -e --arg a "$(cat $D/alert.txt)" '[.messages[].content] | any(contains($a))' $R >/dev/null 2>&1 && echo "✅ the request includes the alert text" || echo "❌ include the full text of alert.txt in a message"
jq -e '[.messages[].content] | join(" ") | contains("service=") and contains("status=") and contains("region=")' $R >/dev/null 2>&1 && echo "✅ the prompt spells out the line format" || echo "❌ show the exact format service=... status=... region=... in the prompt"
[ -s $D/fixed-reply.txt ] && [ "$(cat $D/fixed-reply.txt)" = "$(jq -r '.choices[0].message.content' $D/fixed-response.json 2>/dev/null)" ] && echo "✅ fixed-reply.txt holds exactly the reply in fixed-response.json" || echo "❌ extract .choices[0].message.content from fixed-response.json into fixed-reply.txt"
[ "$(grep -c . $D/fixed-reply.txt 2>/dev/null)" = 1 ] && echo "✅ the reply is a single line" || echo "❌ the reply must be exactly one line"
[ "$(tr -d '\r' < $D/fixed-reply.txt 2>/dev/null | sed 's/[[:space:]]*$//')" = "service=payments status=down region=eu" ] && echo "✅ the reply is exactly what the dashboard expects" || echo "❌ got '$(cat $D/fixed-reply.txt 2>/dev/null)' - expected service=payments status=down region=eu"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Diagnose the weak answer first: here the cause was a missing output format.
- A literal template, allowed values, and an example pin the output down.
- `temperature: 0` and a saved prompt file make the result repeatable.
