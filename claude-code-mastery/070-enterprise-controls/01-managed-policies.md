---
type: lesson
title: "Managed policies"
minutes: 14
---

A team repo (topic 069) is a convention: anyone can edit `.claude/settings.json`. An organization that must *guarantee* behaviour, so that no one bypasses permissions or pastes production data to an unapproved model, uses **managed settings**. They sit above every other level, and a developer can't override them.

## Delivery mechanisms

| Mechanism | Where it lives | Picked up | Use when |
|---|---|---|---|
| **Server-managed settings** | The claude.ai admin console (Teams and Enterprise) | At startup, refreshed hourly | You want central policy with no endpoint tooling |
| **MDM / OS policy** | macOS profile domain `com.anthropic.claudecode`, or the Windows registry `HKLM\SOFTWARE\Policies\ClaudeCode` (value `Settings`) | At startup, checked every 30 minutes | Devices are already managed by Jamf, Intune or Group Policy |
| **Managed settings file** | `managed-settings.json` (plus an optional `managed-settings.d/` drop-in folder) in `/Library/Application Support/ClaudeCode/` (macOS), `/etc/claude-code/` (Linux, WSL) or `C:\Program Files\ClaudeCode\` (Windows) | At startup, reloaded on change | Linux hosts, golden images, machines without MDM |

`managed-mcp.json` in the same folder defines MCP servers for everyone.

By default, Claude Code uses the **highest-ranked source that delivers a policy** (server-managed, then MDM, then the file) and ignores the rest. `/status` names the source it used. Set `managedSourcesBehavior: "merge"` in the top source only when every lower source is also admin-controlled.

## What policies typically contain

```json
{
  "permissions": {
    "deny": ["Read(./.env)", "Read(./.env.*)", "Read(~/.aws/**)", "Bash(curl *)", "WebFetch"],
    "disableBypassPermissionsMode": "disable"
  },
  "allowManagedPermissionRulesOnly": true,
  "allowManagedHooksOnly": true,
  "availableModels": ["sonnet", "haiku"],
  "env": {"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp", "OTEL_EXPORTER_OTLP_ENDPOINT": "https://otel.internal.example.com"},
  "cleanupPeriodDays": 14,
  "strictKnownMarketplaces": [{"source": "github", "repo": "acme/claude-plugins"}],
  "companyAnnouncements": ["Agent usage policy: go/agents-policy"]
}
```

| Key | Effect |
|---|---|
| `permissions.deny` | Rules no lower level can undo |
| `permissions.disableBypassPermissionsMode: "disable"` | Nobody can start with `--dangerously-skip-permissions` or switch to bypass mode |
| `allowManagedPermissionRulesOnly` | Only managed allow, ask and deny rules count. Project and user rules are ignored |
| `allowManagedHooksOnly` | Only managed hooks run. Repo hooks can't execute commands on a developer's machine |
| `allowedMcpServers`, `deniedMcpServers`, `allowManagedMcpServersOnly` | Control which MCP servers may connect |
| `strictKnownMarketplaces` | Plugins only from marketplaces you list |
| `forceLoginMethod`, `forceLoginOrgUUID` | Sign-ins only to your organization's account |
| `apiKeyHelper`, `otelHeadersHelper` | Scripts that print short-lived credentials, so no static keys sit in files |
| `env` | Environment for every session: telemetry, proxies, provider switches |
| `cleanupPeriodDays` | How long local session transcripts are kept |

## Precedence, once more

```text
managed  >  command line  >  local project  >  shared project  >  user
```

A few security-sensitive keys let a *stricter* lower value still count. For example, a developer can always add their own `deny` rules. A developer can never loosen a managed value.

## Commands this node introduces

`managed-settings.json`, `managed-settings.d/`, `managed-mcp.json`, server-managed settings, `/status` (which shows the policy source), `disableBypassPermissionsMode`, `allowManagedPermissionRulesOnly`, `allowManagedHooksOnly`, `strictKnownMarketplaces`, `forceLoginOrgUUID`, and `managedSourcesBehavior`.
