---
type: lesson
title: "Privacy and your data"
minutes: 7
---

Every prompt you send goes to whoever runs the model. Before pasting anything, know where it goes and what may happen to it.

## What happens to your prompts

It depends on the product and the contract:

| | Typical consumer chat app | Business / API plans |
|---|---|---|
| Used to train future models | Often on by default (can be turned off) | Usually off by default |
| Stored | Chat history, until deleted | Often kept up to ~30 days for abuse monitoring, sometimes zero-retention by agreement |
| Who can see it | Provider staff in limited cases | Same, under the contract |

Always check your organisation's approved tools and the provider's data terms. "Free and convenient" is not "approved".

## What never goes in a prompt

- **Secrets**: API keys, passwords, tokens, private keys, connection strings.
- **Personal data** you're not allowed to share: customer names, emails, addresses, health or payment details.
- **Confidential material** your company hasn't approved for that tool: unreleased financials, legal documents, security findings.

## Safer habits

1. **Redact first.** Replace real values with placeholders: `customer_42`, `<API_KEY>`, `10.0.0.x`. The model rarely needs the real ones.
2. **Send the minimum.** The 20 relevant log lines, not the whole dump with user emails in it.
3. **Use approved tools.** Company accounts with data-protection terms, not personal accounts.
4. **Consider local models** for sensitive data: with the `ollama` profile, prompts never leave the machine.
5. **Mind the logs.** Your own app's logs can leak prompts. This lab's gateway deliberately logs only metadata - model, tokens, roles - never the prompt text.

## Redaction in practice

```bash
sed -E 's/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}/<email>/g; s/sk-[A-Za-z0-9_-]+/<key>/g' app.log > app.redacted.log
```

Simple patterns catch the obvious cases. They're not perfect - for regulated data, use proper tooling and policies.
