---
type: scenario
title: "Scenario: the Frankfurt office cannot start a session"
minutes: 9
---

Your company runs Claude Code on Bedrock through managed settings: `CLAUDE_CODE_USE_BEDROCK=1` and `AWS_REGION=us-east-1`, with `us.` model pins. A new office in Frankfurt has a data-residency rule, so their machines get `AWS_REGION=eu-central-1`. Since then, every session there fails with a 400 error naming `us.anthropic.claude-sonnet-4-6`.

### Q1. Why does the region change alone not work?

- A. Frankfurt doesn't support Claude
- B. Bedrock needs a restart
- C. The IAM policy is per office
- D. The pins still name us. inference profiles; in an eu-* region those need to be eu. profiles

<details><summary>Answer</summary>

**Answer: D** - Pinned IDs are used exactly as written; the prefix has to match the region's profiles.

</details>

### Q2. What's the clean fix for the Frankfurt group?

- A. Remove all pins
- B. A separate managed policy for that group: AWS_REGION=eu-central-1 and eu.anthropic... pins for every alias
- C. Tell them to use --model
- D. Switch them to the Anthropic API

<details><summary>Answer</summary>

**Answer: B** - Keep pinning; deliver a group-specific policy (a different MDM profile or file, or a gateway policy per IdP group).

</details>

### Q3. After the fix, Haiku-tier background calls still fail. What did you miss?

- A. ANTHROPIC_DEFAULT_HAIKU_MODEL (and the small/fast region) also needs an eu. profile enabled in that account
- B. Nothing
- C. Haiku isn't allowed in the EU
- D. A cache

<details><summary>Answer</summary>

**Answer: A** - Every alias in use needs a valid pin for the region.

</details>

### Q4. How do you verify before rolling it out to the whole office?

- A. On one machine: /status shows the region and models, aws bedrock list-inference-profiles --region eu-central-1 lists the pinned IDs, and a test prompt succeeds
- B. Roll out and watch Slack
- C. Check the AWS bill
- D. Ask AWS support

<details><summary>Answer</summary>

**Answer: A** - Prove the identity, the model access, and the resolved config on one machine first.

</details>
