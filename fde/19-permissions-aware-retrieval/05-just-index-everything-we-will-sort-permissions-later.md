---
type: scenario
title: "Just index everything, we will sort permissions later"
minutes: 3
---

Kestrel Bank wants the pilot live in two weeks. The IT lead says: "Export the whole SharePoint into the index. Permissions are complicated - we'll add them in phase two. The pilot users are all managers anyway."

### Q1. What do you say?

- A. Fine - managers can see most things
- B. Index everything but tell the model not to reveal confidential data
- C. Refuse the pilot
- D. Explain that one shared index exposes every document to every pilot user, and propose indexing only sources all pilot users may read, with ACL sync in phase two

<details><summary>Answer</summary>

**Answer: D** - Scope the pilot to data that's safe for everyone in it.

</details>

### Q2. Why doesn't 'tell the model not to reveal confidential documents' work?

- A. Once text is in the prompt it can come out - by paraphrase, by accident or through injection
- B. It works fine
- C. Models don't read system prompts
- D. It's too expensive

<details><summary>Answer</summary>

**Answer: A** - Enforce access in retrieval, not in instructions.

</details>

### Q3. A pilot manager asks a question about salary bands, which only HR may read. With your plan, what happens?

- A. The assistant answers from HR data
- B. It forwards the question to HR
- C. It asks the manager for a password
- D. HR documents aren't in the pilot index, so it says it doesn't know

<details><summary>Answer</summary>

**Answer: D** - Data that isn't indexed can't leak.

</details>
