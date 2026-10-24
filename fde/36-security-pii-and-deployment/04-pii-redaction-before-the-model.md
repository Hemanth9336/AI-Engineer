---
type: lesson
title: "PII redaction before the model"
minutes: 6
---

**Redaction** replaces personal data with placeholders before text goes anywhere it doesn't need to - a model API, a log, an eval dataset:

```text
Before: Hi, this is Jan, jan.devries@harbor-foods.nl, phone +31 20 794 5521. Refund to NL91 ABNA 0417 1643 00.
After:  Hi, this is Jan, [EMAIL], phone [PHONE]. Refund to [IBAN].
```

The model can still summarise, classify or route the ticket. It just can't leak what it never saw.

## How to detect PII

| Method | Good at | Misses |
|---|---|---|
| **Regex** | Structured data: emails, IBANs, card numbers, phone numbers, ids | Names, addresses, free-text context |
| **NER models** (spaCy, Presidio) | Names, places, organisations | Some precision errors; needs tuning per language |
| **Allow/deny lists** | Known customer names, internal codes | Anything not on the list |

Production systems usually layer them, e.g. Microsoft Presidio (regex + NER). Start with regex for structured identifiers - it catches the highest-risk items (payment and contact details) with no false negatives on well-formed input.

## Order and precision matter

- **Most specific first**: IBANs and card numbers before phone numbers, or a card number gets half-eaten by the phone pattern.
- **Don't redact what the task needs**: order ids like `MER-55120` and dates are needed to answer; make sure your patterns leave them alone, and test that they do.
- **Typed placeholders** (`[EMAIL]`, `[IBAN]`) keep the text understandable for the model.

## Reversible redaction

Sometimes the answer needs the original value - "we'll email jan@...". Store a mapping (`[EMAIL_1]` -> the address) **inside the customer's environment**, send placeholders out, and substitute the real values back into the reply locally.

## Redact logs too

The outbound prompt log is the most common place PII leaks: someone turns on "log full prompts" for debugging (see the scenario at the end of this topic). Log what you send - after redaction.
