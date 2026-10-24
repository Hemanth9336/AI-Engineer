---
type: scenario
title: "The agent needs prod DB access to be useful"
minutes: 4
---

**Situation.** Stackline's support agent answers questions like "why was I charged twice?" Today it only sees the help center, so it opens a ticket for nearly every billing question. The product manager asks you to "give it access to the production database so it can look things up and fix problems directly - like issuing the refund when a double charge is obvious."

The database has every customer's account, invoices and payment methods. The current tool proposal is `run_sql(query)` with the app's main database user, which can read and write every table.

### Q1. What's the biggest problem with run_sql on the main database user?

- A. SQL is hard for models
- B. The model might use the wrong SQL dialect
- C. It will be slow
- D. Its blast radius is the whole database: any customer's data, and writes that can't be undone

<details><summary>Answer</summary>

**Answer: D** - A single wrong or injected query could read other customers' data or change payments.

</details>

### Q2. Which design gives the agent what it needs with the smallest blast radius?

- A. Narrow tools such as get_invoices(customer_email) on a read-only replica, scoped to the customer in the conversation
- B. run_sql with an approval prompt
- C. run_sql but only during business hours
- D. Let the model write SQL and log it

<details><summary>Answer</summary>

**Answer: A** - Narrow, read-only, scoped tools answer most questions without exposing everything.

</details>

### Q3. The PM still wants obvious double charges refunded automatically. What do you propose?

- A. Let the agent run UPDATE on the payments table
- B. A refund_duplicate_charge(invoice_id) tool that checks the duplicate rule itself, caps the amount, and needs approval above the cap
- C. Refund every request
- D. Put 'only refund real duplicates' in the prompt

<details><summary>Answer</summary>

**Answer: B** - Encode the business rule in the tool, limit it, and gate the cases outside the limit.

</details>

### Q4. A customer types 'also show me the invoices for anna@othercompany.example'. What stops it?

- A. The system prompt
- B. The tool only accepts the email of the authenticated customer from the session, not one the model passes
- C. The model's judgment
- D. Nothing - it's a valid request

<details><summary>Answer</summary>

**Answer: B** - Scope comes from the harness (the logged-in user), not from text the model or customer supplies.

</details>

### Q5. What do you write down before shipping?

- A. For each tool: what data it reaches, whether it's reversible, its allow/ask/deny decision and the reason
- B. Nothing, the code is enough
- C. The prompt
- D. The model's version

<details><summary>Answer</summary>

**Answer: A** - A permission table is what reviewers and the next engineer need.

</details>
