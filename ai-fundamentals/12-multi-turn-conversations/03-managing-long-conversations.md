---
type: lesson
title: "Managing long conversations"
minutes: 7
---

A support chat, a coding session, an agent run - real conversations grow. Here is how to keep them inside the window, fast, and cheap.

## Strategy 1: a sliding window

Keep the system message plus the last N turns; drop older ones.

```bash
# keep system message + last 6 messages
jq '.messages = ([.messages[0]] + .messages[1:][-6:])' chat.json
```

Simple and predictable. The cost: anything said before the window is forgotten.

## Strategy 2: summarize old turns

When the history gets long, ask the model to summarize it, then replace the old turns with one message:

```json
{"role": "system", "content": "Summary of the conversation so far: the user is debugging a 502 on checkout-api; we ruled out DNS and TLS; the next step is checking the upstream pool."}
```

You keep the key facts at a fraction of the tokens.

## Strategy 3: keep facts outside the chat

Things that must never be forgotten - the user's name, the system being discussed, decisions made - belong in a small **state** object your program maintains and re-inserts into the system message every turn. Do not rely on the model finding them 40 turns back.

## Strategy 4: start fresh

When the topic changes, start a new conversation. Old, unrelated turns only add cost and confusion. This is exactly what `/clear` does in coding assistants.

## Which to use

| Situation | Good choice |
|---|---|
| Casual chat, recent context is all that matters | Sliding window |
| Long troubleshooting session | Summarize + key facts in state |
| New task in the same tool | Start fresh |
| Facts that must survive | Explicit state in the system message |

## Watch the numbers

`usage.prompt_tokens` tells you how big each turn's input really is. If it climbs every turn, history is growing - decide on a strategy before it hits the window or the bill. Now build a conversation by hand and see the history at work.
