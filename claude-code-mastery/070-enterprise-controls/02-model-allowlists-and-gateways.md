---
type: lesson
title: "Model allowlists and gateways"
minutes: 14
---

## Restricting models

`availableModels` in managed settings limits what developers can choose with `/model`, `--model` or the `model` setting:

```json
{"availableModels": ["sonnet", "haiku", "claude-opus-4-8"], "model": "sonnet"}
```

- Entries can be aliases (`sonnet`), version prefixes, or full model IDs. On cloud providers, write them in the IDs the provider uses (topic 071).
- `model` sets the default. `enforceAvailableModels: true` (recent versions) makes even the built-in default and the startup fallbacks respect the list.
- On Bedrock, Google Cloud's Agent Platform and Microsoft Foundry, the console's model controls don't reach sessions. Managed `availableModels` and `model` are the controls there.

Why restrict at all? Cost (opus by default for everyone is expensive), data handling (only models approved by your review), and predictability (everyone on the same pinned versions).

## LLM gateways

A **gateway** sits between Claude Code and the model provider:

```text
developer laptops ──HTTPS──▶ gateway (your infrastructure) ──▶ Anthropic API / Bedrock / Agent Platform / Foundry
                              SSO, model policy, spend caps, logs, failover
```

| Without a gateway | With a gateway |
|---|---|
| Each developer or CI job holds an API key or cloud credential | The upstream credential lives only on the gateway. Developers sign in with SSO |
| Offboarding means revoking keys and hoping none were copied | Disable the user in the IdP; their gateway token expires within the session lifetime |
| Usage is attributed to whoever owns the key | Usage is per developer and per group |
| Every client is configured per provider | Clients speak one API; the gateway translates and fails over between upstreams |

Two ways to run one:

- **Claude apps gateway**, built into the `claude` binary (`claude gateway --config gateway.yaml`). It provides OIDC sign-in, per-IdP-group model access and managed settings, OTLP telemetry relay, spend limits, and upstreams for Bedrock, Claude Platform on AWS, Google Cloud, Microsoft Foundry or the Anthropic API. Developers point at it with managed settings `forceLoginMethod: "gateway"` and `forceLoginGatewayUrl`. It must be on a **private** address, because a trusted gateway can push settings to every laptop.
- **Your own LLM gateway** (LiteLLM, an API gateway, a proxy). Point Claude Code at it with `ANTHROPIC_BASE_URL` (plus `ANTHROPIC_AUTH_TOKEN` or an `apiKeyHelper`). It must forward the Anthropic Messages API faithfully, including the `anthropic-beta` headers and the streaming responses.

## Commands this node introduces

`availableModels`, `enforceAvailableModels`, managed `model`, `claude gateway --config`, `forceLoginMethod: "gateway"`, `forceLoginGatewayUrl`, `ANTHROPIC_BASE_URL`, and `apiKeyHelper`.
