---
type: quiz
title: "Quick check: authenticating an Agent Platform deployment"
minutes: 9
---

### Q1. A CI job on GKE needs Claude Code on Google Cloud's Agent Platform. What's the recommended identity?

- A. A service account bound through workload identity, with roles/aiplatform.user on the project
- B. A personal gcloud login copied into the image
- C. An Anthropic API key
- D. A JSON key committed to the repo

<details><summary>Answer</summary>

**Answer: A** - Machine identity without long-lived keys; grant only the predict permission it needs.

</details>

### Q2. Credentials work, but requests go to the wrong project. Which variable decides the project?

- A. GOOGLE_CLOUD_PROJECT
- B. CLOUD_ML_REGION
- C. The project in the key file
- D. ANTHROPIC_VERTEX_PROJECT_ID

<details><summary>Answer</summary>

**Answer: D** - Claude Code addresses the project in ANTHROPIC_VERTEX_PROJECT_ID even if other sources disagree.

</details>

### Q3. A developer sees `Could not load the default credentials`. First step?

- A. Reinstall Claude Code
- B. gcloud auth application-default login (or set GOOGLE_APPLICATION_CREDENTIALS)
- C. Change CLOUD_ML_REGION
- D. Use /logout

<details><summary>Answer</summary>

**Answer: B** - That error means there are no Application Default Credentials on the machine.

</details>

### Q4. Which IAM permission must the identity have for model calls?

- A. aiplatform.models.list
- B. aiplatform.endpoints.predict (in roles/aiplatform.user)
- C. storage.objects.get
- D. iam.serviceAccounts.actAs

<details><summary>Answer</summary>

**Answer: B** - Invocation and token counting need endpoints.predict.

</details>

### Q5. You want expired developer credentials renewed automatically. Which setting?

- A. gcpAuthRefresh, for example gcloud auth application-default login
- B. awsAuthRefresh
- C. apiKeyHelper
- D. otelHeadersHelper

<details><summary>Answer</summary>

**Answer: A** - Claude Code runs it when credentials are expired or can't be loaded, then retries.

</details>
