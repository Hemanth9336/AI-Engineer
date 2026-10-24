---
type: lesson
title: "Output filters"
minutes: 5
---

Input filters stop bad requests. **Output filters** stop bad answers - checked in code after the model replies and before the user sees anything.

## Why the prompt isn't enough

You'll write "never promise refunds" in the system prompt. The model will follow it 99% of the time. With 10,000 conversations a day, 1% is 100 promises your customer's legal team has to honour. Rules that matter get **enforced in code** as well.

## What to check

| Check | Example violation | Why the customer cares |
|---|---|---|
| **Commitments** | "We will refund you 120 EUR" | Legally binding promises the bot can't authorise |
| **Banned phrases** | "We guarantee delivery by Friday", "this is legal advice" | Contract and liability language |
| **Competitors** | "Faster than DHL!" | Brand and legal policy |
| **Contact details** | An email or URL outside the company's domains | Phishing via injected content (next lesson) |
| **PII** | Another customer's address or phone number | Data protection (topic 36) |
| **Format** | Invalid JSON, a missing citation | Downstream code breaks |

## What to do on a violation

1. **Replace** the reply with a safe fallback: "I can't confirm that here - a Meridian agent will follow up by email."
2. **Log** the original reply, the violation and the conversation id - each one is a prompt bug to fix.
3. Optionally **regenerate** once with a stricter instruction, then fall back.

## Keep the rules in data

Competitor lists and banned phrases change. Keep them in a policy file the customer can review and edit, not hard-coded across your codebase. And test the filter like any function: a list of replies that must pass and replies that must be caught.
