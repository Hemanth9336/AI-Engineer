---
type: lesson
title: "Being specific"
minutes: 7
---

The quickest way to improve almost any prompt is to replace vague words with specific ones. Models take what you write literally, and fill everything you did not write with the most average answer.

## Swap vague for specific

| Vague | Specific |
|---|---|
| "Keep it short" | "Under 60 words" |
| "Make a list" | "Exactly 5 bullet points, each starting with a verb" |
| "For beginners" | "For a support agent who has never used a terminal" |
| "Explain the error" | "Explain what caused the error and the one command that fixes it" |
| "Professional tone" | "Polite and direct, like an email to a customer you respect" |
| "Summarize this" | "Summarize this incident in 3 sentences: what broke, impact, fix" |

Numbers, named formats, and named audiences are the strongest kinds of specific.

## Say what you want, not only what you don't

"Don't be wordy" tells the model what to avoid but not what to aim for. "Answer in two sentences" gives it a target. Positive instructions are easier to follow than negative ones; when you need a "don't", pair it with a "do":

```text
Do not use jargon. Explain it the way you would to a new hire in their first week.
```

## Give the reason

A short reason helps the model make good choices you did not spell out:

```text
Keep each bullet under 12 words - these will be read on a phone during an outage.
```

Now it knows to front-load the important word, skip pleasantries, and avoid tables.

## Specific output for code

When code will read the answer, be strict: name the exact format and tell it to output nothing else.

```text
Reply with exactly 5 lines. Each line starts with "- ". No heading, no introduction,
no closing sentence.
```

Your script can then rely on the shape - and your checker can test it, which is exactly what the next task does.
