---
type: lesson
title: "Keeping history in the messages list"
minutes: 5
---

A multi-turn chat is a list that grows by two messages per turn:

```python
messages = [{"role": "system", "content": SYSTEM}]

while True:
    text = input()
    messages.append({"role": "user", "content": text})
    reply = client.chat.completions.create(model="lab-mini", messages=messages).choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    print(reply)
```

After three turns the request contains:

```text
system, user, assistant, user, assistant, user
```

## Details that matter

- **The system message stays first** and is sent every time.
- **Append the assistant's reply**, not just the user's messages - otherwise the model sees questions with no answers and gets confused.
- **Store the history per conversation**, keyed by a conversation id. At a customer that's a database table or a cache, not a Python variable - servers restart and users come back tomorrow.
- **Tool calls are history too.** In a tool-using assistant, the assistant tool-call messages and `tool` results go in the list.
- **Never mix conversations.** Sending user A's history in user B's request is a data leak.

## Reading input in a script

`input()` reads one line from standard input and raises `EOFError` when input ends. That lets you test a chat loop without typing:

```bash
printf 'Hi\nWhat did I just say?\n' | python chat.py
```

The task's checker uses exactly that.
