---
type: lesson
title: "Choosing the provider transport"
minutes: 14
---

Claude Code can reach Claude through several transports. Each one changes who authenticates, who bills, which features are available, and where requests go.

| Transport | Turn it on | Auth | Bills to | Notes |
|---|---|---|---|---|
| Claude account (Pro, Max, Team, Enterprise) | `/login` | OAuth sign-in | The subscription | Every feature, including cloud sessions, Remote Control and Code Review |
| Anthropic API (Console) | `ANTHROPIC_API_KEY` or `apiKeyHelper` | An API key | The Console organization | Typical for CI and the SDK |
| Amazon Bedrock | `CLAUDE_CODE_USE_BEDROCK=1` | The AWS credential chain, or `AWS_BEARER_TOKEN_BEDROCK` | Your AWS account | Invoke API (not Converse). The optional Mantle endpoint (`CLAUDE_CODE_USE_MANTLE`) has its own model IDs |
| Google Cloud's Agent Platform | `CLAUDE_CODE_USE_VERTEX=1` | Application Default Credentials | Your GCP project | `CLOUD_ML_REGION` can be `global`, multi-region, or regional |
| Microsoft Foundry | `CLAUDE_CODE_USE_FOUNDRY=1` | A Foundry resource and key, or Entra ID | Your Azure subscription | |
| A gateway | `ANTHROPIC_BASE_URL`, or the Claude apps gateway sign-in | Whatever the gateway requires | Whatever the gateway's upstream is | Centralizes the credential, the policy and the logs (topic 070) |

## How to choose

1. **Is there a data-residency or cloud-commitment requirement?** Then use Bedrock, Agent Platform or Foundry in the required region, or a gateway in front of them.
2. **Do developers need the account-only features** (cloud sessions, Remote Control, Code Review, Chrome)? Then they need Claude Team or Enterprise seats, possibly *in addition to* cloud-provider inference.
3. **CI and automation:** an API key or cloud role scoped to the job, never a person's subscription.
4. **Many developers on a shared upstream:** put a gateway in front for SSO, per-person attribution and spend caps.

## Exactly one transport per session

The provider switches are mutually exclusive. If `CLAUDE_CODE_USE_BEDROCK=1` leaks into a shell where you meant to use your subscription, every request goes to AWS. Check `/status`: its **API provider** line is the ground truth for what this session uses.

Put the switches in the `env` block of settings (managed, for fleets) rather than in shell profiles. That way they apply to Claude Code only, don't leak to other tools, and can't be half-set.

## Endpoint overrides

`ANTHROPIC_BEDROCK_BASE_URL` and `ANTHROPIC_VERTEX_BASE_URL` point the provider client at a proxy or a private endpoint (for example, a VPC endpoint). A proxy in that path must pass the provider's streaming format through unchanged. Bedrock streams `application/vnd.amazon.eventstream`, and a proxy that rewrites it to server-sent events breaks streaming.

## Commands this node introduces

`/login`, `/status` (its API provider line), `ANTHROPIC_API_KEY`, `CLAUDE_CODE_USE_MANTLE`, `CLAUDE_CODE_USE_FOUNDRY`, `ANTHROPIC_BEDROCK_BASE_URL`, and `ANTHROPIC_VERTEX_BASE_URL`.
