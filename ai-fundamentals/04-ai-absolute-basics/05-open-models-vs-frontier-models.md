---
type: lesson
title: "Open models vs frontier models"
minutes: 6
---

There are two broad families of models, and the difference matters for cost, privacy, and capability.

## Frontier models

**Frontier models** are the largest, most capable models from the big labs: OpenAI's GPT models, Anthropic's Claude, Google's Gemini. You cannot download them. You use them through the company's apps or **API**, and the company runs them in its own data centres.

- **Strengths:** the best quality at hard reasoning, writing, and coding; huge context windows; nothing to install.
- **Trade-offs:** you pay per token, your data travels to the provider, and the provider decides when a model changes or retires.

## Open models

**Open models** (more precisely, **open-weights** models) publish their trained parameters so anyone can download and run them: Meta's Llama, Mistral, Alibaba's Qwen, DeepSeek, Google's Gemma, and OpenAI's gpt-oss, among others.

- **Strengths:** run them on your own hardware or private cloud, so data never leaves; no per-token bill beyond your hardware; you can fine-tune them; they never change under you.
- **Trade-offs:** the best ones need serious GPUs; small ones that fit on a laptop are noticeably weaker; you run and secure them yourself.

"Open weights" is not always "open source": you get the model, but often not the training data, and the licence may limit commercial use. Read it before you build on one.

## Running an open model yourself

Tools like **Ollama** make a small open model a two-command job:

```bash
curl -fsSL https://ollama.com/install.sh | sh     # install Ollama
ollama run llama3.2:3b "Explain DNS in one sentence."   # download once, then chat
```

Many hosting services (OpenRouter, Together, Groq, cloud providers) also serve open models over an API, so you get open-model pricing without managing GPUs.

## How the lab uses both

The lab gateway gives you five models with stable names. Four are general-purpose models from your chosen provider, and **`lab-open`** is an open-weights model whenever your profile has one. Topic 13 compares them properly.

| Choose | When |
|---|---|
| Frontier | Quality matters most, data may leave your network, volume is moderate |
| Open | Data must stay in-house, volume is huge, or you need full control |

Next: why every model, open or frontier, sometimes makes things up.
