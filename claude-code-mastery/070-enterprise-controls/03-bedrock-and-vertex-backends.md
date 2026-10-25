---
type: lesson
title: "Bedrock and Vertex backends"
minutes: 14
---

Many organizations already have cloud agreements, data-residency rules and IAM in AWS or Google Cloud. Claude Code can send inference there instead of to the Anthropic API.

| | Amazon Bedrock | Google Cloud's Agent Platform (formerly Vertex AI) |
|---|---|---|
| Switch | `CLAUDE_CODE_USE_BEDROCK=1` | `CLAUDE_CODE_USE_VERTEX=1` |
| Where | `AWS_REGION` (or the profile's region) | `CLOUD_ML_REGION` (`global`, `eu`, `us`, or a region) and `ANTHROPIC_VERTEX_PROJECT_ID` |
| Identity | The AWS SDK credential chain (SSO profile, role, instance profile) or `AWS_BEARER_TOKEN_BEDROCK` | Application Default Credentials (`gcloud auth application-default login`, a service account, workload identity) |
| Permissions | `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` (plus `ListInferenceProfiles` and `GetInferenceProfile`) | `aiplatform.endpoints.predict` (role `roles/aiplatform.user`) |
| Model access | Enable the models in the account (a one-time use-case form) | Enable the models in Model Garden for the project |
| Credential refresh | The `awsAuthRefresh` and `awsCredentialExport` settings | The `gcpAuthRefresh` setting |

Microsoft Foundry (`CLAUDE_CODE_USE_FOUNDRY=1`) follows the same pattern.

## What changes for developers

- Billing and rate limits are your cloud account's. Raise quotas with your cloud provider, not Anthropic.
- `/logout` isn't available. Authentication is the cloud credential.
- Some features need a claude.ai account and don't work with cloud credentials alone: cloud sessions, Code Review, Remote Control, and Claude in Chrome. Plan seats if you need them.
- Some tools differ by provider. For example, WebSearch isn't available on Bedrock.

## The one rule for fleets: pin your models

Without pins, aliases like `sonnet` and `opus` resolve to Claude Code's built-in default for that provider. That default may not be enabled in your account yet, and it changes when Claude Code updates. Pin every alias in managed settings `env`:

```json
{"env": {
  "CLAUDE_CODE_USE_BEDROCK": "1", "AWS_REGION": "eu-central-1",
  "ANTHROPIC_DEFAULT_OPUS_MODEL": "eu.anthropic.claude-opus-4-8",
  "ANTHROPIC_DEFAULT_SONNET_MODEL": "eu.anthropic.claude-sonnet-4-6",
  "ANTHROPIC_DEFAULT_HAIKU_MODEL": "eu.anthropic.claude-haiku-4-5-20251001-v1:0"}}
```

Then a model upgrade is a policy change you make deliberately, not something that happens to 200 people overnight. Topic 071 covers regions, identity chains and the failures you'll see.

## Commands this node introduces

`CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`, `CLAUDE_CODE_USE_FOUNDRY`, `AWS_REGION`, `CLOUD_ML_REGION`, `ANTHROPIC_VERTEX_PROJECT_ID`, `AWS_BEARER_TOKEN_BEDROCK`, `awsAuthRefresh`, `gcpAuthRefresh`, and `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU}_MODEL`.
