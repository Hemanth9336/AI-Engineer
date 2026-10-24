---
type: task
title: "Hold a conversation"
minutes: 10
---

## Scenario

You are setting up a Slack channel for the payments on-call rotation and want the model's help naming it and writing its description - in two turns, where the second builds on the first.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/12-chat
```

## What to build

1. Write `/root/ai-lab/12-chat/turn1.json` for `lab-fast`: a **system** message of your choice, and a **user** message asking for a name for the payments on-call Slack channel, replying with only the name. Send it, save the response to `turn1-response.json` and the reply to `reply1.txt`.
2. Write `/root/ai-lab/12-chat/turn2.json`: the same messages as turn 1, **plus** an `assistant` message whose content is exactly `reply1.txt`, **plus** a new `user` message asking for a one-sentence description of **that channel** - without repeating the name yourself. Send it, save the response to `turn2-response.json` and the reply to `reply2.txt`.

The checker confirms the history is intact and that the description uses the name from turn 1.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq --arg r "$(cat reply1.txt)" '.messages += [{role: "assistant", content: $r}, {role: "user", content: "..."}]' turn1.json > turn2.json`
- Say 'that channel' or 'it' in the second question, so the model must use the history.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/12-chat
jq -n '{model: "lab-fast", messages: [
  {role: "system", content: "You are a helpful assistant for an SRE team."},
  {role: "user", content: "Suggest a name for the Slack channel of our payments on-call rotation. Reply with only the channel name, starting with #."}
]}' > turn1.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @turn1.json -o turn1-response.json
jq -r '.choices[0].message.content' turn1-response.json > reply1.txt
jq --arg r "$(cat reply1.txt)" \
  '.messages += [{role: "assistant", content: $r}, {role: "user", content: "Write a one-sentence channel description for that channel. Mention the channel name."}]' \
  turn1.json > turn2.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @turn2.json -o turn2-response.json
jq -r '.choices[0].message.content' turn2-response.json > reply2.txt
cat reply1.txt reply2.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/12-chat
jq -e '.model == "lab-fast" and (.messages | map(.role)) == ["system", "user"]' $D/turn1.json >/dev/null 2>&1 && echo "✅ turn1.json has a system and a user message" || echo "❌ turn1.json needs model lab-fast with a system then a user message"
[ -s $D/reply1.txt ] && [ "$(cat $D/reply1.txt)" = "$(jq -r '.choices[0].message.content' $D/turn1-response.json 2>/dev/null)" ] && echo "✅ reply1.txt holds exactly the reply in turn1-response.json" || echo "❌ extract .choices[0].message.content from turn1-response.json into reply1.txt"
jq -e '(.messages | map(.role)) == ["system", "user", "assistant", "user"]' $D/turn2.json >/dev/null 2>&1 && echo "✅ turn2.json has system, user, assistant, user" || echo "❌ turn2.json must have four messages: system, user, assistant, user"
jq -e --slurpfile t1 $D/turn1.json '.messages[0:2] == $t1[0].messages' $D/turn2.json >/dev/null 2>&1 && echo "✅ turn 2 starts with the exact messages of turn 1" || echo "❌ turn2.json must begin with the same two messages as turn1.json"
jq -e --arg r "$(cat $D/reply1.txt 2>/dev/null)" '$r != "" and .messages[2].content == $r' $D/turn2.json >/dev/null 2>&1 && echo "✅ the assistant message is the turn 1 reply, word for word" || echo "❌ the assistant message must contain exactly reply1.txt"
N=$(tr -d '#' < $D/reply1.txt 2>/dev/null | tr -d '[:space:]'); [ -n "$N" ] && ! jq -r '.messages[3].content' $D/turn2.json 2>/dev/null | grep -qiF "$N" && echo "✅ the new question relies on history, not on repeating the name" || echo "❌ ask about 'that channel' without repeating the name in the second user message"
[ -s $D/reply2.txt ] && [ "$(cat $D/reply2.txt)" = "$(jq -r '.choices[0].message.content' $D/turn2-response.json 2>/dev/null)" ] && echo "✅ reply2.txt holds exactly the reply in turn2-response.json" || echo "❌ extract .choices[0].message.content from turn2-response.json into reply2.txt"
[ -n "$N" ] && grep -qiF "$N" $D/reply2.txt 2>/dev/null && echo "✅ the description uses the name from turn 1" || echo "❌ reply2.txt should mention the channel name from turn 1"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- The API is stateless: the messages list is the model's whole memory.
- You keep a conversation going by sending the earlier assistant replies back.
- Every turn re-sends the history, so long chats cost more input tokens.
