---
type: quiz
title: "Quick check: which credential does what"
minutes: 8
---

### Q1. `ANTHROPIC_API_KEY` in the action's `anthropic_api_key` input...

- A. Authenticates Claude API calls, billed to the Console organization
- B. Authenticates GitHub API calls
- C. Signs commits
- D. Is optional with no replacement

<details><summary>Answer</summary>

**Answer: A** - Alternatives are claude_code_oauth_token (a subscription) or OIDC workload identity federation.

</details>

### Q2. You want no long-lived Anthropic secret in GitHub at all. What do you use?

- A. A shorter key
- B. Workload identity federation: the job's OIDC token (id-token: write) is exchanged for API access
- C. CLAUDE_CODE_OAUTH_TOKEN
- D. A public variable

<details><summary>Answer</summary>

**Answer: B** - Federation removes stored keys; the trust lives in a federation rule in the Console.

</details>

### Q3. Claude pushed commits using `github_token: ${{ secrets.GITHUB_TOKEN }}`, and CI didn't run on them. Why?

- A. A bug
- B. The branch is protected
- C. Claude can't push
- D. GitHub doesn't trigger workflows from commits made with GITHUB_TOKEN; use the Claude GitHub App or a custom app token

<details><summary>Answer</summary>

**Answer: D** - That behavior prevents workflow loops, but it also skips your CI on those commits.

</details>

### Q4. In GitLab, which token lets the job comment on the MR or open one?

- A. ANTHROPIC_API_KEY
- B. AI_FLOW_INPUT
- C. CI_JOB_TOKEN, or a project access token with api scope stored as a masked variable
- D. The runner token

<details><summary>Answer</summary>

**Answer: C** - The Claude key talks to Claude; GitLab API access is a separate credential.

</details>

### Q5. A long-lived `CLAUDE_CODE_OAUTH_TOKEN` is shared as an org-wide secret. What's the concern?

- A. None
- B. It's tied to the subscription of the person who generated it; for shared org use prefer a Console API key or federation
- C. It expires hourly
- D. It can't be masked

<details><summary>Answer</summary>

**Answer: B** - Shared org secrets should belong to the organization, not to one person's plan.

</details>
