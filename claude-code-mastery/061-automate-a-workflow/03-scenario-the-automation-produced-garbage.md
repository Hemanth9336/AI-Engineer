---
type: scenario
title: "Scenario: the automation produced garbage"
minutes: 11
---

Your nightly digest has run for a month. This morning the published report reads "I'm sorry, I can't access log files" and nothing else. The team's dashboard has been showing it since 7:30.

### Q1. Which stage of the script failed to do its job?

- A. Verify - an output that names none of the digest's signatures should never have been published
- B. The agent step
- C. Gather
- D. Cron

<details><summary>Answer</summary>

**Answer: A** - Agents will occasionally produce nonsense; the verify stage exists to catch it.

</details>

### Q2. What should a failed verification leave behind?

- A. Nothing
- B. The bad draft published with a warning
- C. Yesterday's report untouched, the failed draft in a scratch folder, a reason on stderr, and a non-zero exit
- D. An empty report

<details><summary>Answer</summary>

**Answer: C** - Keep the last good output and the evidence for debugging.

</details>

### Q3. The draft says it can't access log files. What likely changed?

- A. The prompt or input changed - for example the digest came out empty or the stdin redirect broke, so the model saw no data
- B. The model got worse
- C. Cron's timezone
- D. Disk space

<details><summary>Answer</summary>

**Answer: A** - Check the gather stage's output first; the agent can only work with what it was given.

</details>

### Q4. How would you find out about a failure before the team does?

- A. Read the report every morning
- B. Have cron mail or page on a non-zero exit, and log stderr to a file
- C. Run it twice
- D. Lower max-turns

<details><summary>Answer</summary>

**Answer: B** - A non-zero exit is only useful if something listens for it.

</details>
