---
type: quiz
title: "Quick check: just enough Python"
minutes: 3
---

### Q1. `reply = {"choices": [{"message": {"content": "Hi"}}]}`. Which expression gives "Hi"?

- A. reply["choices"][0]["message"]["content"]
- B. reply.choices.message.content
- C. reply["choices"]["message"]["content"]
- D. reply[0]["content"]

<details><summary>Answer</summary>

**Answer: A** - choices is a list - index it with [0] before reading message.

</details>

### Q2. What does `f"{n} tickets"` print when n = 4?

- A. {n} tickets
- B. 4 tickets
- C. n tickets
- D. f4 tickets

<details><summary>Answer</summary>

**Answer: B** - An f-string replaces {n} with its value.

</details>

### Q3. Why use `ticket.get("owner")` instead of `ticket["owner"]`?

- A. It is faster
- B. It works only on lists
- C. It deletes the key
- D. It returns None instead of raising an error when the key is missing

<details><summary>Answer</summary>

**Answer: D** - .get() is safe for optional fields.

</details>

### Q4. What does `if __name__ == "__main__":` do?

- A. Runs the block only when the file is executed directly, not when imported
- B. Makes the script faster
- C. Defines the main function
- D. Imports sys

<details><summary>Answer</summary>

**Answer: A** - It lets the same file be run as a script and imported for testing.

</details>
