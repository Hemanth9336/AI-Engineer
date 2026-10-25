---
type: quiz
title: "Quick check: reading the run object"
minutes: 9
---

### Q1. A nightly job prints nothing. `jq .subtype run.json` says `error_max_turns`. What happened?

- A. The run hit its --max-turns limit before finishing, so there is no result
- B. The model refused
- C. The prompt was empty
- D. Auth failed

<details><summary>Answer</summary>

**Answer: A** - Max-turns stops the run with an error subtype and no result.

</details>

### Q2. Which field tells you that Claude tried to run `git push` but was not allowed?

- A. usage
- B. permission_denials
- C. num_turns
- D. subtype

<details><summary>Answer</summary>

**Answer: B** - Every refused tool call is listed there.

</details>

### Q3. Your script does `result=$(claude -p ... | jq -r .result)` and gets the literal text `null`. Most likely cause?

- A. The answer was null
- B. The JSON was too big
- C. jq is broken
- D. The run failed - check subtype and is_error before reading result

<details><summary>Answer</summary>

**Answer: D** - result is absent on failed runs; gate first.

</details>

### Q4. Which jq command exits non-zero when the run failed?

- A. jq .is_error run.json
- B. jq . run.json
- C. jq -r .result run.json
- D. jq -e '.is_error == false' run.json

<details><summary>Answer</summary>

**Answer: D** - -e sets the exit code from the last value: false or null makes it non-zero.

</details>
