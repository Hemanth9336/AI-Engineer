---
type: lesson
title: "Where AI falls short"
minutes: 6
---

Generative AI is genuinely useful and genuinely limited. Using it well means knowing both. These are the failure modes you will meet most.

## Confident mistakes

A model produces the most plausible-sounding answer, not a verified one. When it does not know, it often does not say so - it invents a confident answer instead. This is called **hallucination**: a made-up API function, a fake citation, a wrong number stated as fact. Topic 04 explains why it happens; topic 22 covers how to reduce it.

## Stale knowledge

A model learned from data up to a **training cutoff**. Ask about something newer - last month's release, today's outage - and it either does not know or guesses. Tools with web search help, but only when they actually search.

## Weak spots

- **Exact counting and arithmetic.** It may miscount letters or get long sums wrong. Let real code do the maths.
- **Long chains of reasoning.** Errors compound step by step. Topic 08 shows how to help.
- **Your private context.** It does not know your systems, customers, or internal names unless you give it that information (topic 23).
- **Consistency.** Ask twice, get two answers. Fine for drafts, a problem for anything that needs to be repeatable.

## Risks that are not about accuracy

- **Privacy.** What you paste is sent to a provider. Keep secrets and personal data out unless your tool is approved for it.
- **Prompt injection.** Text the AI reads - an email, a web page - can contain instructions that hijack it (topic 22).
- **Over-trust.** The more fluent the answer, the easier it is to stop checking.

## A simple rule

Match your checking to the stakes:

| Stakes | Example | What to do |
|---|---|---|
| Low | Brainstorming names | Use it freely |
| Medium | An email to a customer | Read and edit before sending |
| High | A config change, a legal clause, a medical question | Verify against a real source or an expert, every time |

Used this way, AI is a fast, tireless first draft and a patient explainer - not an oracle. Next topic: what a large language model actually is, so these limits make sense.
