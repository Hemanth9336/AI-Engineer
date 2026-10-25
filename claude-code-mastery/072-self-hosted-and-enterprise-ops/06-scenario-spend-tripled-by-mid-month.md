---
type: scenario
title: "Scenario: spend tripled by mid month"
minutes: 6
---

It's the 15th. Organization spend through the gateway is already three times last month's total. No caps are set. Telemetry and the gateway's spend data are available.

### Q1. What do you look at first?

- A. The model price list
- B. Spend by user and by group (and by flow for automation accounts) for the last 15 days, compared with last month
- C. The number of seats
- D. Gateway CPU

<details><summary>Answer</summary>

**Answer: B** - Find who or what, before deciding how to cap it.

</details>

### Q2. One CI service account accounts for 70% of the spend, running the same review flow 40 times per PR. What's the fix?

- A. Cap every developer at $10/day
- B. Switch everyone to haiku
- C. Fix the trigger, and put the service account in its own group with a daily cap and an alert
- D. Turn off the gateway

<details><summary>Answer</summary>

**Answer: C** - Fix the cause, then bound that blast radius specifically.

</details>

### Q3. Leadership wants a cap today. Which is least disruptive?

- A. A $0 org cap
- B. Monthly cap equal to last month's total for the whole org
- C. An org default comfortably above normal per-person daily spend, tighter caps on automation groups, and alerts at 75%
- D. Block all opus use

<details><summary>Answer</summary>

**Answer: C** - Per-person defaults with headroom stop runaways without stopping normal work.

</details>

### Q4. The gateway's Postgres had an outage for an hour. Were caps enforced during it?

- A. Yes, always
- B. Only for contractors
- C. Not by default - enforcement fails open on store errors unless fail_closed_on_error is set
- D. Caps are enforced by the provider

<details><summary>Answer</summary>

**Answer: C** - Decide deliberately whether availability or zero unmetered spend matters more.

</details>
