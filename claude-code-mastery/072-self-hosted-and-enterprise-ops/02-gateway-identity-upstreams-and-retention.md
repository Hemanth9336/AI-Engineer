---
type: lesson
title: "Gateway identity, upstreams, and retention"
minutes: 10
---

## Identity

With a gateway (topic 070), developers sign in with your IdP over OIDC. Then:

- **Short-lived tokens.** The gateway issues bearer tokens with a session lifetime (`session.ttl_hours`, one hour by default). Deprovisioning someone in the IdP cuts their access within that window. Keep the TTL short.
- **Domain and group checks.** `allowed_email_domains` rejects identities from outside your organization. IdP groups map to model access and to managed-settings policies. Groups are the unit of policy, so keep them meaningful (`payments-eng`, `contractors`).
- **A token identifies a person, not a program.** Any client can set `User-Agent`. Use request metadata for routing and metrics, never as proof of which tool is calling.
- **Private address only.** Claude Code refuses to sign in to a gateway on a public address, because a trusted gateway can push settings that run commands on laptops. Run it behind an internal load balancer or VPN, and set `access_control.allow_cidrs` to the client ranges.

## Upstreams

```yaml
upstreams:
  - provider: bedrock          # primary, in-region
    region: eu-central-1
    auth: {}                   # empty: the AWS default chain - use an instance role or IRSA, not static keys
  - provider: vertex           # failover
    ...
```

- The gateway holds the only upstream credential. Use workload identity (IRSA, an ECS task role, GKE workload identity) so it isn't a static key in a file.
- **Failover** between upstreams keeps developers working through a regional incident. Check that every upstream satisfies your data-residency rule *before* listing it as a failover target.
- **Model catalog.** Expose only the models you've approved per group. The gateway rejects others server-side, regardless of what the client asks for.
- **Boot is fail-closed**: the config, Postgres, OIDC discovery and upstream clients are checked before it serves. Inference credentials resolve on the first request, so test a real prompt after every deploy.

## Retention

Decide, write down and configure how long each kind of data lives:

| Data | Where | Typical retention |
|---|---|---|
| Local session transcripts | Developer machines, `~/.claude/projects/` | `cleanupPeriodDays` in managed settings (for example 14) |
| Gateway audit log (sign-ins, rejections, admin changes) | Your log pipeline | Your security log standard, often a year |
| Telemetry (metrics, events, traces) | Your OTLP backend | Metrics long, events shorter. Content switches off (topic 068) |
| Spend counters and spend audit | Gateway Postgres | Back it up; it's the source for caps |
| Prompts and responses | The model provider, per its terms, or zero-retention agreements | Contractual |
| Cloud session transcripts | Anthropic, for resuming sessions | Per your plan's terms |

## Commands this node introduces

OIDC sign-in, `session.ttl_hours`, `allowed_email_domains`, IdP groups, `access_control.allow_cidrs`, `upstreams` and failover, fail-closed boot, and `cleanupPeriodDays`.
