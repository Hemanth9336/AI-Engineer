---
type: task
title: "Get parseable JSON from a model"
minutes: 13
---

## Scenario

An alert router needs the host, port, and status from free-text alerts, as JSON it can parse with `jq`.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/15-json
cd /root/ai-lab/15-json
echo "WARNING from monitor-3: database db-01 is answering slowly on port 5432 - replication lag is 40s and rising, but it is still serving queries." > alert.txt
```

## What to build

Write `/root/ai-lab/15-json/json-request.json` for `lab-fast` that:

1. Turns on JSON mode with `"response_format": {"type": "json_object"}`.
2. Includes the full text of `alert.txt`.
3. Asks for a JSON object with exactly the keys `host` (string), `port` (number), and `status` (one of `up`, `degraded`, `down`).

Send it, save the response to `json-response.json`, and save the reply content to `/root/ai-lab/15-json/status.json`.

The checker parses `status.json` with `jq` and expects host `db-01`, port `5432` as a **number**, and status `degraded`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Put the key list in a system message, and the alert in the user message.
- Remember to use the word JSON in your messages - JSON mode needs it.
- `jq -e '.port | type == "number"' status.json` tests the type.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/15-json
jq -n --arg a "$(cat alert.txt)" '{
  model: "lab-fast",
  temperature: 0,
  response_format: {type: "json_object"},
  messages: [
    {role: "system", content: "Extract alert details. Reply with only a JSON object with exactly these keys: \"host\" (string), \"port\" (number), \"status\" (one of \"up\", \"degraded\", \"down\"). A service that is slow but still serving is degraded."},
    {role: "user", content: $a}
  ]
}' > json-request.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @json-request.json -o json-response.json
jq -r '.choices[0].message.content' json-response.json > status.json
jq . status.json
```

</details>

## Check your work

```bash
D=/root/ai-lab/15-json; R=$D/json-request.json; J=$D/status.json
jq -e '.model == "lab-fast" and .response_format.type == "json_object"' $R >/dev/null 2>&1 && echo "✅ json-request.json turns on JSON mode for lab-fast" || echo "❌ add \"response_format\": {\"type\": \"json_object\"} and model lab-fast"
jq -e --arg a "$(cat $D/alert.txt)" '[.messages[].content] | any(contains($a))' $R >/dev/null 2>&1 && echo "✅ the request includes the alert" || echo "❌ include the full text of alert.txt"
jq -e '[.messages[].content] | join(" ") | contains("host") and contains("port") and contains("status") and test("json"; "i")' $R >/dev/null 2>&1 && echo "✅ the prompt names the keys and says JSON" || echo "❌ name the keys host, port, status - and use the word JSON - in your messages"
[ -s $J ] && [ "$(cat $J)" = "$(jq -r '.choices[0].message.content' $D/json-response.json 2>/dev/null)" ] && echo "✅ $J holds exactly the reply in json-response.json" || echo "❌ extract .choices[0].message.content from json-response.json into $J"
jq -e 'type == "object"' $J >/dev/null 2>&1 && echo "✅ status.json is valid JSON" || echo "❌ status.json does not parse as a JSON object"
jq -e 'keys == ["host", "port", "status"]' $J >/dev/null 2>&1 && echo "✅ it has exactly host, port, status" || echo "❌ status.json must have exactly the keys host, port, status (got: $(jq -c keys $J 2>/dev/null))"
jq -e '.host == "db-01" and .port == 5432 and .status == "degraded"' $J >/dev/null 2>&1 && echo "✅ host db-01, port 5432 (a number), status degraded" || echo "❌ expected {\"host\":\"db-01\",\"port\":5432,\"status\":\"degraded\"} - got $(jq -c . $J 2>/dev/null)"
jq -se 'any(.[]; .json_mode == true and .model == "lab-fast" and .ok)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway saw a JSON-mode request" || echo "❌ the gateway has no successful JSON-mode request yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- JSON mode guarantees valid syntax; the prompt still has to define the keys and types.
- Name allowed values (an enum) so the model can't invent new ones.
- Always parse and validate model JSON before another program trusts it.
