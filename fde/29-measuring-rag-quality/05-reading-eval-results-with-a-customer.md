---
type: lesson
title: "Reading eval results with a customer"
minutes: 5
---

You'll present eval results to people who don't read JSON: support leads, compliance officers, a COO. How you present them decides whether they trust the system - and whether they make the right call.

## Lead with what they care about

Translate metrics into outcomes:

| Metric | Say it as |
|---|---|
| hit@3 = 0.94 | "For 94 of 100 questions, the right policy reaches the assistant." |
| Correct 88% | "88 of 100 answers match what your team said is right." |
| Trap refusal 100% | "Every question your docs don't cover got 'I don't know' - no invented answers." |
| Faithfulness 97% | "3 of 100 answers added a detail that isn't in the source. Here they are." |

## Show the failures, not just the number

Bring the actual failing cases - question, answer, what was wrong, and which bucket it's in:

- **Fixable now** - a missing doc, a chunking problem, a prompt rule.
- **Needs the customer** - an ambiguous policy, a contradicting document, a missing expected answer.
- **Acceptable** - a hard edge case where a refusal is fine.

Failures grouped this way turn the meeting into a plan.

## Compare against something real

78% means nothing alone. Compare with **today's process**: how often do human agents give the wrong fee? How long does a correct answer take now? An assistant at 88% that answers instantly and refuses when unsure may beat a 92%-accurate team with a two-day queue - or it may not, for a compliance-critical answer. That's the customer's decision, made with numbers.

## Never overstate

Say what the eval covers and what it doesn't: "120 questions, mostly about parcels; pallets aren't well covered yet." The credibility you keep by being precise is worth more than a higher-sounding number.
