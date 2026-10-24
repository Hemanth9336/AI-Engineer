---
type: lesson
title: "Models remember nothing"
minutes: 5
---

Chat interfaces feel like talking to someone who remembers you. The API doesn't work that way. **Every request is independent.** The model sees exactly the messages you send in that request - nothing from earlier calls, nothing from other users.

```text
Request 1:  user: "My name is Priya and my order is MER-55120."
            -> "Thanks Priya, how can I help with MER-55120?"

Request 2:  user: "What is my order number?"
            -> "I don't have access to your order details."
```

Request 2 has no idea request 1 happened. The "memory" in ChatGPT-style products is the application **re-sending the conversation** every time.

## Why it's designed this way

- **Scale**: providers don't need to store state per user; any server can handle any request.
- **Privacy and control**: what the model sees is exactly what you sent. Nothing leaks between users or sessions by accident.
- **Cost transparency**: you pay for exactly the tokens you send.

## What it means for you

- **You own the conversation state.** Your code stores the messages and sends them each time.
- **Long conversations get expensive**: turn 20 re-sends turns 1-19. Cost grows with every turn.
- **Eventually the history won't fit** in the context window, so you'll need to trim or summarize (third lesson).
- **"Memory" across sessions is a feature you build**: store facts about the user and add them to the prompt.

Customers often assume the assistant "learns" from conversations. It doesn't - not within the weights (that's training), and not between requests unless your code sends the history. Expect to explain this more than once.
