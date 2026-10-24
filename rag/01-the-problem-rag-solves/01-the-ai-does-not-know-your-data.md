---
type: lesson
title: "The AI does not know your data"
minutes: 8
---

Ask an AI model "what is DNS?" and it gives you a good answer. Now ask it "what time does the payments team deploy to production?" and the conversation stops working. A typical reply:

```text
I don't have any information about the payments team's deployment
schedule. Could you point me to where this might be documented,
like a wiki page or a team handbook?
```

Why? The model learned from public text on the internet. Books, websites, documentation. Your team's runbook was never part of that. Your deploy time, your on-call rules, your customer notes - the model has never seen any of it.

## Two ways models handle the gap

Not every model reacts the same way when you ask about something it never learned:

- **Good models admit it**, like the reply above: "I don't have information about that."
- **Some models, and especially older ones, guess instead.** They answer in a confident tone with something that sounds normal, like "many teams deploy on Fridays" - which looks like an answer and is not one.

The second behavior is more dangerous, because a wrong answer that looks right can end up in real decisions. But notice: both behaviors leave you in the same place. You asked a question, and you did not get YOUR answer. The information is simply not inside the model.

## You cannot fix this with a better question

People try. They write longer prompts, they ask nicely, they ask twice. It does not help, because the problem is not the question. No prompt can pull out something that was never put in.

But read that model reply again, because it points at the fix itself: "could you point me to where this might be documented?" The model is asking for the document. Think about how you would help a new teammate who asks "when do we deploy?". You would not tell them to guess. You would hand them the runbook page and say: read this, the answer is here.

You can do exactly the same thing with a model. **Give it the document, then ask the question.** That one move is the heart of everything in this course.

In the next lesson you run both versions yourself: the model without the document, and the model with it.
