---
type: lesson
title: "What fine-tuning does and does not do"
minutes: 7
---

"Can we fine-tune the model on our data?" is one of the most common customer questions - and one of the most commonly misunderstood. Answering it well is a core FDE skill.

## What fine-tuning is

**Fine-tuning** continues training a model on your own examples - usually hundreds to thousands of input/output pairs - so its weights shift toward producing outputs like yours.

```text
{"messages": [{"role": "user", "content": "box came smashed"}, {"role": "assistant", "content": "{\"category\": \"damage\", \"urgency\": \"normal\"}"}]}
```

## What it's good at

| Good for | Example |
|---|---|
| **Format and style** | Always reply in the company's tone, or always emit a strict JSON schema |
| **A narrow, repeated task** | Classify tickets into 40 categories with company-specific rules |
| **Making a small model do a big model's job** | Distil a large model's outputs into a cheaper, faster model |
| **Shorter prompts** | Behaviour learned in the weights doesn't need 3,000 tokens of instructions per call |

## What it's bad at

| Bad for | Why |
|---|---|
| **Teaching facts** | Facts get blurred into the weights unreliably; the model still invents nearby "facts", and you can't cite the source |
| **Knowledge that changes** | A new returns policy means retraining; with RAG you update a document |
| **Permissions** | Everything in the training data is available to everyone who uses the model |
| **Fixing a vague task** | If people can't agree on the right output, neither can training examples |

## The hidden costs

Collecting and cleaning examples, an eval set to prove it helped, re-training when the base model is upgraded, hosting a custom model, and losing easy access to newer base models. The training run is often the cheapest part.
