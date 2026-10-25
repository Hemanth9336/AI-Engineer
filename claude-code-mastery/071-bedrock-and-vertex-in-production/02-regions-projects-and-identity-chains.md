---
type: lesson
title: "Regions, projects, and identity chains"
minutes: 14
---

## Bedrock: regions and inference profiles

Claude Code resolves the AWS region from `AWS_REGION`, then `AWS_DEFAULT_REGION`, then the active profile's `region`, then `us-east-1`. Requests use **cross-region inference profiles**, whose ID prefix follows the region:

| Region | Prefix | Example |
|---|---|---|
| `us-*` | `us.` | `us.anthropic.claude-sonnet-4-6` |
| `eu-*` | `eu.` | `eu.anthropic.claude-sonnet-4-6` |
| `ap-*` | `apac.` | `apac.anthropic.claude-sonnet-4-6` |
| `us-gov-*` | `us-gov.` | |
| other regions | `global.` | |

`ANTHROPIC_BEDROCK_REGION_PREFIX` (`us`, `eu`, `apac`, `jp`, `au`, `global`) changes the preferred prefix without pinning. An **application inference profile ARN** (`arn:aws:bedrock:...:application-inference-profile/...`) works as a model ID, and is how many organizations tag and attribute cost. `modelOverrides` maps each Anthropic model version to your own ARN.

## Agent Platform: projects and locations

- Requests go to the project in `ANTHROPIC_VERTEX_PROJECT_ID`, even when `GOOGLE_CLOUD_PROJECT` or the credential file names another project.
- `CLOUD_ML_REGION=global` gives the best availability, but not every model is served on the global endpoint. Override per model with `VERTEX_REGION_CLAUDE_*` variables (for example `VERTEX_REGION_CLAUDE_HAIKU_4_5=us-east5`).
- A value that isn't shaped like a region is treated as unset, and falls back to `CLOUD_ML_REGION`, then `us-east5`.

## Identity chains

The model call is the last link in a chain. When it fails, find the link that broke.

```text
AWS:  SSO login / role / instance profile ─▶ AWS SDK credential chain ─▶ STS-signed request ─▶ IAM policy ─▶ model access in account+region
GCP:  gcloud ADC / service account / workload identity ─▶ access token ─▶ IAM role on the project ─▶ model enabled in Model Garden for that location
```

| Link | AWS | GCP |
|---|---|---|
| Interactive developer | `aws sso login --profile X` plus `AWS_PROFILE=X`, or `aws login` | `gcloud auth application-default login` |
| Machine (CI, server) | An instance or task role, or IRSA on EKS. No static keys | A service account via workload identity, or `GOOGLE_APPLICATION_CREDENTIALS` |
| Automatic refresh | `awsAuthRefresh: "aws sso login --profile X"` | `gcpAuthRefresh: "gcloud auth application-default login"` |
| Cross-account | `awsCredentialExport` (a command that prints credentials JSON) | Impersonation in the credential config |
| Bearer key alternative | `AWS_BEARER_TOKEN_BEDROCK` (short-term keys preferred) | |

Claude Code caches resolved AWS credentials until five minutes before they expire. A credential error clears the cache and retries.

`awsAuthRefresh` and `gcpAuthRefresh` run commands. In *project* settings they follow the same workspace-trust rule as hooks, which is another reason they belong in user or managed settings.

## Commands this node introduces

`AWS_PROFILE`, `aws sso login`, inference profile prefixes, `ANTHROPIC_BEDROCK_REGION_PREFIX`, application inference profile ARNs, `modelOverrides`, `GOOGLE_APPLICATION_CREDENTIALS`, `gcloud auth application-default login`, `VERTEX_REGION_CLAUDE_*`, and `awsCredentialExport`.
