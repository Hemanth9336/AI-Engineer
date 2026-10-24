---
type: lesson
title: "Training vs inference"
minutes: 5
---

Two words you'll hear in every customer meeting, often mixed up.

## Training: building the model

**Training** is how a model learns to predict tokens. The vendor feeds it trillions of tokens of text - books, websites, code - and adjusts billions of internal numbers (**weights**) so its predictions get better. Then they tune it further on examples of helpful conversations, so it follows instructions and answers like an assistant.

Training is enormously expensive (thousands of GPUs for weeks), done rarely, and done by the model vendor. The result is a fixed file of weights with a **knowledge cutoff**: it knows nothing after the date its training data ends, and nothing that was never public - like your customer's documents.

## Inference: using the model

**Inference** is running the trained model to get an answer. Every API call you make is inference: your prompt goes in, the weights stay exactly the same, tokens come out. It costs fractions of a cent and takes seconds.

| | Training | Inference |
|---|---|---|
| Who does it | The model vendor (or you, for fine-tuning) | You, on every request |
| Changes the weights? | Yes | **No** |
| Cost | Millions | Fractions of a cent per call |
| How often | Rarely | Constantly |

## Why customers care

The question you'll hear most: **"Will our data train your model?"** Using a model through an API is inference - by itself it does not change the model. Whether a vendor *stores* your prompts and later uses them for training is a **contract and settings** question (most business APIs say no by default). You'll handle it properly in the security topic.

The second consequence: **the model doesn't learn from use.** Correct it today and it makes the same mistake tomorrow, because inference never changes the weights. To make a model "know" the customer's information, you put that information in the prompt at inference time - which is exactly what RAG does.
