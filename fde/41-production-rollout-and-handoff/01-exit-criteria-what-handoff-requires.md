---
type: lesson
title: "Exit criteria: what handoff requires"
minutes: 7
---

An FDE engagement ends. The system shouldn't. **Handoff** is the point where the customer's team owns the assistant - and it should be planned from the first week, not improvised in the last.

## Exit criteria

Agree, early, what must be true before you leave:

| Area | Exit criterion |
|---|---|
| **Quality** | Pilot criteria met; evals pass at the agreed bar |
| **Ownership** | Named owners for the system, the golden set, the prompts and on-call |
| **Operations** | Deploys, restarts and re-index run by the customer's team without you |
| **Monitoring** | Daily report and alerts going to the customer's people |
| **Change process** | Prompt and model changes go through evals and the gate - and the team has done it at least once |
| **Documentation** | A runbook covering how it works, how to run it and what to do when it breaks |
| **Security** | Data flows, logging and retention signed off by the customer's security and privacy owners |

## "Done" means they've done it

The strongest exit criterion is **demonstrated**: the customer's engineer has deployed a change, run the evals, handled a (simulated) incident and updated the golden set - while you watched and didn't touch the keyboard.

## Leave less behind

Simplicity is a handoff feature. Every clever component you built is something the customer has to understand. Before you leave, remove what isn't needed, prefer standard tools the team already knows, and make configuration explicit.
