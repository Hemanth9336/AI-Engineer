---
type: quiz
title: "Quick check: chunking"
minutes: 6
---

### Q1. Why does a question about stolen laptops match a laptop chunk better than the whole handbook?

- A. The chunk is shorter to download
- B. The handbook is not in English
- C. Embedding models only read the first word
- D. A focused chunk has a sharp vector; a whole document's vector averages many topics

<details><summary>Answer</summary>

**Answer: D** - One vector for many topics sits near none of them.

</details>

### Q2. chunk_text('abcdefghij', size=5, overlap=2) returns:

- A. ['abcde', 'fghij']
- B. ['abcde', 'defgh', 'ghij']
- C. ['abcde', 'cdefg', 'efghi', 'ghij']
- D. ['ab', 'cd', 'ef']

<details><summary>Answer</summary>

**Answer: B** - Step = 5 - 2 = 3: starts at 0, 3, 6; the third reaches the end.

</details>

### Q3. What problem does overlap solve?

- A. It makes chunks smaller
- B. It speeds up embedding
- C. It removes duplicates
- D. A fact on a chunk boundary would otherwise be split so that no chunk holds it whole

<details><summary>Answer</summary>

**Answer: D** - Overlap repeats the boundary region in both chunks.

</details>

### Q4. Your documents haven't changed. A user asks a new question. What must be embedded?

- A. All chunks again
- B. The whole document
- C. Nothing
- D. Only the question

<details><summary>Answer</summary>

**Answer: D** - Indexing happens once; querying embeds just the question.

</details>
