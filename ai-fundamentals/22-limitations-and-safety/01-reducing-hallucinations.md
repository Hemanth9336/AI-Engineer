---
type: lesson
title: "Reducing hallucinations"
minutes: 7
---

A **hallucination** is a confident, fluent answer that is wrong: an invented command flag, a made-up API, a fake citation, a wrong number. It is not a bug that will be patched away - it follows from how LLMs work (topic 04): they generate **plausible** text, and plausible is not the same as true.

## When it happens most

- **Specific facts the model saw rarely**: exact version numbers, niche CLI flags, internal names.
- **Things after its knowledge cutoff**: new releases, recent incidents, today's prices.
- **Your private world**: your services, your runbooks, your customers - it has never seen them.
- **Pressure to answer**: a prompt that implies there must be an answer.
- **Long chains** of reasoning or arithmetic, where one slip carries through.

## Techniques that work

| Technique | How |
|---|---|
| **Give it the facts** | Paste the doc, log, or data into the prompt (grounding, topic 23) |
| **Allow "I don't know"** | "If the text doesn't say, reply NOT IN DOCUMENT" |
| **Ask for sources** | "Quote the line you used" - easy to check, harder to fake |
| **Use tools for exact work** | Calculations, dates, lookups via tools (topic 16) or code |
| **Lower the temperature** | `temperature: 0` for factual tasks reduces creative drift |
| **Use a stronger model** | Larger and reasoning models hallucinate less on hard questions |
| **Verify** | Run the command in a sandbox, check the docs, test the code |

## The most important habit

**Match your checking to the stakes.** A brainstorm needs no checking. A command you'll run on production, a number in a report to leadership, a statement to a customer - verify every one. "The AI said so" is never an acceptable source.

## Spotting a likely hallucination

Be suspicious of: very specific details you didn't provide (exact versions, URLs, people's names), flags or functions you've never seen, perfect-looking citations, and answers that agree a little too readily with a wrong premise in your question.
