---
type: scenario
title: "Scenario: reviewing a gateway and runner rollout"
minutes: 6
---

A platform team asks you to review their design: a Claude apps gateway on a public load balancer "so remote staff don't need VPN", a static AWS access key in `gateway.yaml` for the Bedrock upstream, `session.ttl_hours: 72`, and three self-hosted runners with `--capacity 10` for 40 developers.

### Q1. What's wrong with the public load balancer?

- A. Nothing, if it uses HTTPS
- B. It costs more
- C. Claude Code refuses public gateway addresses by design, because a gateway can push settings that run commands on laptops; put it behind VPN or a private endpoint
- D. OIDC needs a private address

<details><summary>Answer</summary>

**Answer: C** - The private-address rule protects every developer machine from a spoofed or exposed gateway.

</details>

### Q2. How should the Bedrock credential be supplied instead?

- A. Base64-encode the key
- B. An environment variable in the Compose file
- C. A workload identity (IRSA, a task role, an instance profile) with an empty auth block, so no static key exists
- D. Each developer's own key

<details><summary>Answer</summary>

**Answer: C** - The upstream credential is the crown jewel; make it short-lived and unexportable.

</details>

### Q3. Why is `ttl_hours: 72` a problem?

- A. A deprovisioned employee keeps working for up to three days; the TTL bounds revocation
- B. Tokens get too large
- C. It breaks SSO
- D. Postgres fills up

<details><summary>Answer</summary>

**Answer: A** - Keep it near the default of one hour.

</details>

### Q4. Will three runners at capacity 10 serve 40 developers?

- A. No - each runner locks to one owner at a time, so three runners serve at most three developers at once; size by concurrent owners or use the autoscaler
- B. Yes, 30 slots is close enough
- C. Yes, if sessions are short
- D. Only with drain-grace

<details><summary>Answer</summary>

**Answer: A** - Capacity is per owner; owners, not sessions, set the minimum fleet.

</details>
