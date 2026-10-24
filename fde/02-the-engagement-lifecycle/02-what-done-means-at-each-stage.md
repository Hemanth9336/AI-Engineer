---
type: lesson
title: "What done means at each stage"
minutes: 8
---

"Is the pilot done?" sounds like a simple question. Without agreed exit criteria it becomes an argument. Define **done** for each stage up front, in writing, with the customer.

| Stage | Done means | Evidence you show |
|---|---|---|
| Discovery | One use case scoped, with a success metric, data access confirmed, and an owner on the customer side | A one-page scoping document the sponsor signs off |
| Pilot | The success metric is met on real users and a test set | Weekly eval scores, pilot user feedback, and failure examples with fixes |
| Production | Safe to run for everyone: cost and safety limits, logging, monitoring, and security approval | A passing security review, dashboards, a load test, and a cost estimate at full volume |
| Handoff | The customer team runs and changes it without you | A runbook, a trained owner who has shipped a change, and an on-call rota |

## Good exit criteria are measurable

Compare:

- Weak: "The pilot users are happy with the assistant."
- Strong: "On the 60-question test set the assistant answers at least 85% correctly and refuses 100% of out-of-scope questions; pilot agents use it on at least 40% of tickets in week four."

The strong version can be checked by anyone, and it stops the goalposts moving in either direction. A sponsor can't declare failure on a vibe, and you can't declare success on a demo.

## Done is not perfect

Exit criteria are thresholds, not perfection. An assistant that's right 87% of the time with a clean refusal for everything else can be very valuable - if that's what everyone agreed it needed to do. "100% accurate" is never an exit criterion; you'll see why in the evals and expectations topics.

## Write them down early

Exit criteria for the pilot belong in the discovery document. Production criteria belong in the pilot plan. Handoff criteria belong in the production plan. Each stage defines what the next one must prove.
