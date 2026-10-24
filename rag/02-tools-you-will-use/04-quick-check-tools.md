---
type: quiz
title: "Quick check: tools"
minutes: 6
---

### Q1. Why does ask() use temperature=0?

- A. It makes the model faster
- B. It makes answers as repeatable as possible, which suits answering from documents
- C. It is required by the gateway
- D. It lowers the cost

<details><summary>Answer</summary>

**Answer: B** - Low temperature removes most randomness - you want the same grounded answer each time.

</details>

### Q2. Your script fails with openai.APIConnectionError. What do you check first?

- A. The model name
- B. The temperature
- C. Whether the gateway is running - ailab status
- D. Whether the question is too long

<details><summary>Answer</summary>

**Answer: C** - A connection error means nothing answered at the URL.

</details>

### Q3. What does the if __name__ == "__main__": block give you?

- A. Faster code
- B. A web server
- C. Automatic error handling
- D. The file can be imported as a module without running its command-line part

<details><summary>Answer</summary>

**Answer: D** - Code under the guard runs only when the file is started directly.

</details>

### Q4. Which model turns text into vectors in this course?

- A. lab-fast
- B. lab-smart
- C. lab-embed
- D. lab-reasoning

<details><summary>Answer</summary>

**Answer: C** - lab-embed is the local embedding model; the lab-* chat models write answers.

</details>
