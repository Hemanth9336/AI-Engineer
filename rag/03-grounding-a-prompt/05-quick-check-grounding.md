---
type: quiz
title: "Quick check: grounding"
minutes: 5
---

### Q1. Why put the document inside <document> tags?

- A. Tags make the request cheaper
- B. They hide the document from the model
- C. The API requires XML
- D. They mark exactly where the source starts and stops, so its text is treated as data

<details><summary>Answer</summary>

**Answer: D** - Delimiters separate your instructions from the document's own text.

</details>

### Q2. Your document says employees get 20 vacation days, but the model answers 25. Which rule was missing?

- A. Use temperature 1
- B. Put the question first
- C. Answer using only the document
- D. Use a bigger model

<details><summary>Answer</summary>

**Answer: C** - Without 'only the document', the model blends in general knowledge.

</details>

### Q3. Why ask for an exact refusal sentence rather than 'say if you don't know'?

- A. Your code can detect it reliably and you can test it
- B. It sounds more polite
- C. It uses fewer tokens
- D. Models can't say 'I don't know' otherwise

<details><summary>Answer</summary>

**Answer: A** - An exact string is machine-checkable.

</details>

### Q4. Where should the question go in a grounded prompt?

- A. Before the instructions
- B. After the document, as the user message
- C. Inside the document tags
- D. In a separate request

<details><summary>Answer</summary>

**Answer: B** - Instructions and document first, then the question at the end.

</details>
