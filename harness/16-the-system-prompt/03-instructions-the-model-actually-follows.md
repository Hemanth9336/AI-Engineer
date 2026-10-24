---
type: lesson
title: "Instructions the model actually follows"
minutes: 6
---

Models follow instructions *mostly*. How reliably depends a lot on how the instructions are written. Most "the model ignores my prompt" problems come from a handful of writing mistakes.

## Why rules get ignored

| Mistake | Example | Fix |
|---|---|---|
| **Contradictions** | "Always answer immediately without tools" + "Always look up the account first" | Remove one. The model can't obey both, so it obeys neither reliably |
| **Buried rules** | The privacy rule is sentence 9 of a 12-sentence paragraph | Put critical rules first, as their own bullet |
| **Vague verbs** | "You can maybe help them or open a ticket" | Say exactly what to do: "open a ticket" |
| **No reason** | "Ask for the email." | "Ask for the email, because accounts are found by email." Reasons help the model generalize to cases you didn't list |
| **Only prohibitions** | Five "Don't..." lines | Say what to do instead: "Keep answers to four sentences" beats "Don't write long answers" |
| **Shouting** | "NEVER EVER!!!" | Calm, specific wording works better than caps, and leaves real emphasis for what matters |
| **Marketing filler** | "Our support is the best and we really care..." | Delete it. Every sentence costs tokens on every step and dilutes the rules |

## Structure helps

- **Bullets, one rule each.** Easy for the model to scan, easy for you to diff and test.
- **Most important first.** Legal and safety rules at the top.
- **One example.** A short "good exchange" shows tone and format better than adjectives.
- **Consistent terms.** If it's "account email" in one rule, don't call it "login" in another.

## Prompts can only do so much

Even a perfect prompt is a request. For rules that must **never** break - privacy, refunds, destructive actions - also enforce them in the harness: filter tool results by the customer's own email, gate the refund tool, block the action. The prompt makes good behavior likely; the harness makes bad behavior impossible.

## Lint, then test

Some of these problems can be caught mechanically - a **prompt linter** that flags contradictions, shouting and missing sections. Behavior is checked with evals (topic 30). In the next task you'll use a linter to fix a prompt the model keeps ignoring.
