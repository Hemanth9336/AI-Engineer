---
type: quiz
title: "Quick check: what slurp changes"
minutes: 9
---

### Q1. `jq 'length' runs/*/*.json` over 3 files prints three numbers. What does `jq -s 'length' runs/*/*.json` print?

- A. The same three numbers
- B. 3 - slurp reads every file into one array first
- C. The total size in bytes
- D. An error

<details><summary>Answer</summary>

**Answer: B** - Without -s the filter runs once per input; with -s once over the array of all inputs.

</details>

### Q2. Why tag each record with `input_filename` *before* slurping?

- A. It's faster
- B. Slurp deletes file names
- C. input_filename is only defined while jq reads each input; after slurping there's one array and no per-file name
- D. @csv needs it

<details><summary>Answer</summary>

**Answer: C** - Attach the file-derived task in a first pass, then aggregate in a second.

</details>

### Q3. One run file is truncated. What does `jq -s ... runs/*/*.json` do?

- A. Skips it
- B. Fails with a parse error, so you get no ledger at all
- C. Treats it as null
- D. Warns and continues

<details><summary>Answer</summary>

**Answer: B** - Validate files first and pass only good ones; name the bad ones on stderr.

</details>

### Q4. Which filter turns `["a", 2, 0.5]` into the CSV line `"a",2,0.5`?

- A. tostring
- B. join(",")
- C. @csv, with jq -r
- D. @text

<details><summary>Answer</summary>

**Answer: C** - @csv quotes strings; -r prints it raw.

</details>
