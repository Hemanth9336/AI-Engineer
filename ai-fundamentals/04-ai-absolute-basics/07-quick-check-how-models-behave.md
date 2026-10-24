---
type: quiz
title: "Quick check: how models behave"
minutes: 5
---

### Q1. What is an LLM actually doing when it writes a reply?

- A. Looking up the answer in a database of facts
- B. Following rules that engineers wrote for each question
- C. Running a search engine and copying the top result
- D. Predicting the next token again and again, based on patterns learned in training

<details><summary>Answer</summary>

**Answer: D** - An LLM generates text one token at a time. There is no answer database inside it, which is why it can be fluent and wrong.

</details>

### Q2. Roughly how many English words fit in 1,000 tokens?

- A. About 75
- B. About 750
- C. About 7,500
- D. Exactly 1,000

<details><summary>Answer</summary>

**Answer: B** - A token is about three-quarters of an English word, so 1,000 tokens is about 750 words. Code and other languages use more tokens per word.

</details>

### Q3. A request uses 1,000 input tokens and 1,000 output tokens. Why is the output usually the bigger part of the bill?

- A. Output tokens are counted twice
- B. The reply always has more words
- C. Input tokens are free
- D. Providers price output tokens higher than input tokens, often several times higher

<details><summary>Answer</summary>

**Answer: D** - Generating tokens costs the provider more than reading them, so output is priced higher per million tokens.

</details>

### Q4. Your company must not send customer records outside its own network. Which model choice fits?

- A. A frontier model through a consumer chat app
- B. An open-weights model running on hardware the company controls
- C. Any model, as long as you delete the chat afterwards
- D. A frontier model, but only on weekends

<details><summary>Answer</summary>

**Answer: B** - Open-weights models can run entirely in-house, so the data never leaves. Frontier models run on the provider's servers.

</details>
