---
type: lesson
title: "Operating managed settings"
minutes: 10
---

Managed settings (topic 070) are code that runs on every developer's machine. Operate them like code.

## Source control and review

- Keep the policy in a repository: `managed-settings.json`, the `managed-settings.d/*.json` fragments, the MDM profile sources, the gateway `managed.policies`.
- Every change gets a pull request, review from security and from a developer representative, and a change note.
- **Split by owner** with `managed-settings.d/`. Security owns `10-security.json`, platform owns `20-telemetry.json`. Each team edits its own file, with no merge conflicts in one shared file.

## Validate before you ship

```bash
jq empty managed-settings.json managed-settings.d/*.json          # valid JSON
claude --settings ./managed-settings.json -p "/status" < /dev/null  # loads, and shows what applies
```

Then test on a canary machine that has the real managed file: confirm `/status` names the managed source, try a denied action, and run a normal task. An invalid managed file is reported, but don't make the first person to notice a developer on deadline.

## Staged rollout

| Stage | Who | Watch |
|---|---|---|
| Canary | The platform team (5-10 machines) | `/status`, error rates in telemetry, support messages |
| Early adopters | One volunteer team | Blocked actions that should have been allowed |
| Everyone | MDM or file distribution to all | The same, plus `companyAnnouncements` to say what changed |

Server-managed settings and MDM can't target groups the same way everywhere. Use separate profiles or files per group, or gateway policies per IdP group, when groups need different rules.

## Drift and exceptions

- MDM can **redeploy the profile on a schedule**, which matters because a local admin can edit the file.
- Exceptions ("payments needs `Bash(psql *)`") are policy changes for a group, reviewed like any other. Never "edit the file on that one laptop".
- Telemetry shows denied actions: a spike after a change means the policy is blocking real work.

## Commands this node introduces

Policy as code, `managed-settings.d/` ownership, `jq empty`, `claude --settings` for testing, canary rollout, `companyAnnouncements`, and scheduled MDM redeploy.
