---
type: quiz
title: "Quick check: sandboxing"
minutes: 5
---

### Q1. Why resolve a path before checking it's inside the workspace?

- A. It's faster
- B. Python requires it
- C. So .., absolute paths and symlinks are turned into the real location before the comparison
- D. To make paths shorter

<details><summary>Answer</summary>

**Answer: C** - `services/../../secret.txt` and `etc-link/passwd` only reveal where they point after resolving.

</details>

### Q2. Why pass an explicit env= to subprocess.run?

- A. Otherwise the child inherits the harness's environment, including the API key
- B. To speed it up
- C. Commands need HOME
- D. It's required on Linux

<details><summary>Answer</summary>

**Answer: A** - `printenv` would show OPENAI_API_KEY to the model.

</details>

### Q3. Your argument check blocks `cat /etc/passwd`. Why isn't that enough?

- A. It is enough
- B. cat might be renamed
- C. A program can open any path itself - a python -c one-liner that opens /etc/passwd passes the check
- D. Linux ignores paths

<details><summary>Answer</summary>

**Answer: C** - String checks are a filter. OS-level sandboxes and containers enforce the real boundary.

</details>

### Q4. Which threat does a container with only the workspace mounted NOT stop?

- A. Reading ~/.ssh on the host
- B. A poisoned file making the agent delete files in the workspace
- C. Seeing host processes
- D. Writing to /etc on the host

<details><summary>Answer</summary>

**Answer: B** - Inside the box, the agent can still misuse what it's allowed to touch.

</details>

### Q5. What's the safest network setting for an agent that only needs to edit local files?

- A. Full internet access
- B. It doesn't matter
- C. Only HTTPS
- D. No network (--network none)

<details><summary>Answer</summary>

**Answer: D** - No network means nothing it reads can be uploaded anywhere.

</details>
