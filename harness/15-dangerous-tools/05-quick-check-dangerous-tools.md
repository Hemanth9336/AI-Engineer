---
type: quiz
title: "Quick check: dangerous tools"
minutes: 4
---

### Q1. Which action is irreversible?

- A. send_email to a customer
- B. write_file to a new file on a git branch
- C. read_file on a config
- D. list_dir

<details><summary>Answer</summary>

**Answer: A** - You can't unsend an email. Reads change nothing; a branch write can be reverted.

</details>

### Q2. You add a new tool and forget to put it in RISK. What should a safe harness do?

- A. Treat it as irreversible and require approval
- B. Run it automatically
- C. Crash
- D. Ask the model how risky it is

<details><summary>Answer</summary>

**Answer: A** - Default deny: a forgotten classification costs an extra prompt, not an accident.

</details>

### Q3. The user presses Enter at 'APPROVE? delete_file {...} [y/N]' without typing anything. What happens?

- A. The file is deleted
- B. The prompt repeats forever
- C. The call is denied - the default is no
- D. The agent crashes

<details><summary>Answer</summary>

**Answer: C** - Only an explicit yes approves. Silence, Enter or a closed input all mean no.

</details>

### Q4. Why does the denial message say 'Do not retry it'?

- A. It's polite
- B. The API requires it
- C. Without it, some models immediately ask for the same call again
- D. It saves tokens

<details><summary>Answer</summary>

**Answer: C** - Denial results steer the model's next step - toward asking what the user wants instead.

</details>

### Q5. The model writes a very convincing reason why the delete is safe. What should the gate do?

- A. Approve, the reason is good
- B. Still ask the human - the model's reasoning doesn't change the rule
- C. Ask the model to double-check
- D. Delete half the files

<details><summary>Answer</summary>

**Answer: B** - Gates are enforced by the harness; the model can't argue its way past them.

</details>
