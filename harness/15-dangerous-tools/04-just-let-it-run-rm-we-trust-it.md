---
type: scenario
title: "Just let it run rm, we trust it"
minutes: 4
---

**Situation.** Stackline's developer-tools team built a coding agent with a `run_shell(command)` tool. Approval prompts slowed people down, so last sprint they switched it to "auto-approve everything". The tech lead's view: "The model is very good, it's never done anything bad in testing, and it's only on developer laptops."

Yesterday a developer asked it to "clean up the build artifacts". The agent ran `rm -rf ./build ~/` - a stray space and a tilde from a path it had seen earlier. It deleted the developer's home directory, including uncommitted work in three other repositories and their SSH keys.

### Q1. What's the real failure here?

- A. The model had a bad day
- B. An irreversible tool (shell with rm) ran with no gate, so one wrong token became data loss
- C. The developer phrased the request badly
- D. rm is a bad command

<details><summary>Answer</summary>

**Answer: B** - Models will occasionally produce a wrong command. The harness decides whether a wrong command can do irreversible damage.

</details>

### Q2. The tech lead says 'it never did anything bad in testing'. Why isn't that enough?

- A. Testing is always useless
- B. Testing was done on a different laptop
- C. The model changes every day
- D. Rare failures don't show up in a few hundred tests but do show up in thousands of real runs - and one irreversible failure is enough

<details><summary>Answer</summary>

**Answer: D** - Safety for irreversible actions is about the worst case, not the average one.

</details>

### Q3. Which change best balances safety and speed?

- A. Turn approvals back on for every command
- B. Remove the shell tool entirely
- C. Auto-run a short allowlist of read-only commands (ls, cat, git status, tests); gate anything that deletes, overwrites or pushes
- D. Add 'never delete home directories' to the prompt

<details><summary>Answer</summary>

**Answer: C** - Classify actions: fast for reads and safe writes, a human checkpoint for the irreversible ones (topic 21 goes further with allowlists).

</details>

### Q4. A developer complains the gate prompts too often and they just press y. What should you change?

- A. Remove the gate
- B. Make the prompt red
- C. Gate fewer things (only irreversible ones), show the exact command clearly, and batch related actions
- D. Require typing the full command back

<details><summary>Answer</summary>

**Answer: C** - Approval fatigue turns a gate into a reflex. Keep gates rare and precise.

</details>

### Q5. Besides the gate, what limits the damage of a bad command that does get approved?

- A. Nothing can
- B. Logging the command afterwards
- C. A bigger model
- D. Running the agent's shell in a sandbox: one working directory, no access to the home folder or keys

<details><summary>Answer</summary>

**Answer: D** - Defense in depth: the gate catches most mistakes, the sandbox limits the rest (topic 22).

</details>
