---
type: lesson
title: "Hallucinations and limits"
minutes: 6
---

A **hallucination** is when a model states something false - a made-up fact, function, quote, or link - with the same confidence it uses for true things. It is the single most important limit to understand, because the output looks exactly as good when it is wrong.

## Why it happens

Go back to how an LLM works: it predicts plausible next tokens. Nothing in that loop checks the answer against reality.

- **Plausible beats true.** If the most natural-sounding continuation is a function named `read_config()`, it will write `read_config()` whether or not that function exists.
- **Gaps get filled.** When the model never saw the answer - a niche tool, your company's systems, last week's news - it does not go quiet. It produces something that fits the shape of an answer.
- **It was trained to be helpful.** Answering feels more helpful than refusing, so "I don't know" is less common than it should be.

## What it looks like in practice

```text
You:   Which flag makes the 'deployctl' tool skip health checks?
Model: Use deployctl --skip-health, or set DEPLOYCTL_NO_HEALTH=1.
```

If `deployctl` is an internal tool the model has never seen, both answers are invented - and they look perfectly reasonable.

## Other limits to keep in mind

- **Knowledge cutoff.** It does not know what happened after its training data ends.
- **No memory between requests.** Over the API, every request starts fresh; it remembers only what you send (topic 12).
- **Exactness.** Counting, long arithmetic, and character-level tasks are unreliable (you saw why in the tokens lesson).
- **Sensitivity to wording.** Small changes in a prompt can change the answer.

## What actually helps

| Do this | Why |
|---|---|
| Give it the source material and ask it to answer only from that | Grounding replaces guessing (topic 23) |
| Tell it that "I don't know" is an acceptable answer | Makes honest gaps more likely |
| Ask for steps or evidence, not just a verdict | Errors become visible (topic 08) |
| Verify anything that matters against a real source | The only reliable fix |

Lowering the temperature makes answers more consistent, but a consistent wrong answer is still wrong. Treat a model like a fast, well-read colleague who never says "I'm not sure" - useful, and always worth checking.
