---
type: lesson
title: "Startup checks and failure signatures"
minutes: 14
---

## What Claude Code checks at startup

On Bedrock and Agent Platform, Claude Code verifies that the models it plans to use are invokable in your account or project:

- **You pinned an older version, and a newer one is available:** it offers to update the pin.
- **You pinned nothing, and the default is unavailable:** it falls back for this session (an earlier version, or from Opus to Sonnet) and shows a notice. The fallback isn't saved.
- **A refusal is remembered on that machine for up to a day.** A default you re-enable is re-checked after about ten minutes.
- **With managed `availableModels` plus `enforceAvailableModels: true`**, the checks only consider models on your list. Write the list in the provider's IDs (`eu.anthropic...` or `claude-...@date`).
- **A model disabled mid-session:** unpinned tiers switch to a fallback with `Switched to <fallback> because <model> is not available`. Pinned versions fail instead, unless you configured a fallback chain.

## Failure signatures

| You see | Likely broken link | Fix |
|---|---|---|
| `Could not load the default credentials` (GCP) | No ADC on the machine | `gcloud auth application-default login`, or set `GOOGLE_APPLICATION_CREDENTIALS` |
| AWS credentials expired, or the browser keeps opening SSO tabs | An SSO session expired, or a proxy breaks the refresh loop | `aws sso login` before starting. Remove `awsAuthRefresh` if a TLS-inspecting proxy interrupts it |
| `AccessDeniedException` / `403` naming `bedrock:InvokeModel` | IAM policy | Grant `InvokeModel` and `InvokeModelWithResponseStream` on the inference profile *and* foundation model ARNs |
| `403` / `PERMISSION_DENIED` naming `aiplatform.endpoints.predict` | IAM on the project | Grant `roles/aiplatform.user` on the project in `ANTHROPIC_VERTEX_PROJECT_ID` |
| `404` model not found (Agent Platform) | Not enabled in Model Garden, or not served in that location | Enable it, or use a supported location or `VERTEX_REGION_CLAUDE_*` |
| `on-demand throughput isn't supported` (Bedrock) | A bare foundation model ID was used | Use an inference profile ID (`eu.anthropic...`) |
| `400` naming the model (Bedrock) | A prefix your account doesn't have enabled, or a Mantle/Invoke ID mix-up | Check `aws bedrock list-inference-profiles --region ...` |
| `429` | Provider quota in that region | Raise the quota with the cloud provider, or use `global` / cross-region profiles |
| `Bedrock streaming response has content-type ...` | A proxy rewrote the event stream | Forward the body and its `Content-Type` unchanged |
| `/status` shows no provider line | The env vars never reached the process | Set them in the settings `env` block instead of a shell profile |

## A five-minute diagnosis routine

1. `/status`: provider, region or project, the resolved model, and where the region came from.
2. Prove the identity *outside* Claude Code: `aws sts get-caller-identity --profile X`, or `gcloud auth application-default print-access-token > /dev/null`.
3. Prove model access outside Claude Code: `aws bedrock list-inference-profiles --region eu-central-1`, or the Model Garden page for the project and location.
4. Only then change Claude Code settings.

## Commands this node introduces

The startup model checks, `enforceAvailableModels`, `CLAUDE_CODE_SKIP_MODEL_ACCESS_MEMORY`, `CLAUDE_CODE_DISABLE_MODEL_ACCESS_FALLBACK`, `aws sts get-caller-identity`, `aws bedrock list-inference-profiles`, and `gcloud auth application-default print-access-token`.
