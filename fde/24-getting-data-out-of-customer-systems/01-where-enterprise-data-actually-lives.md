---
type: lesson
title: "Where enterprise data actually lives"
minutes: 5
---

Demos start with a folder of clean files. Customers start with **systems**. Before you can build anything, you need to know where the knowledge lives, who owns it, and how you're allowed to get it out.

## Typical sources

| Source | Examples | What's tricky |
|---|---|---|
| Document stores | SharePoint, Google Drive, Box, network drives | Permissions per folder, many file formats, duplicates and old versions |
| Wikis | Confluence, Notion, internal wikis | Templates, stale pages, HTML exports |
| Ticketing / CRM | Zendesk, ServiceNow, Salesforce, Jira | Personal data in every record, huge volumes, API rate limits |
| Databases | PostgreSQL, SQL Server, Oracle, data warehouses | Schema knowledge needed, soft-deleted rows, access through DBAs |
| Line-of-business apps | ERP, order management, core banking | Often only an API, sometimes only a nightly CSV export |
| Email and chat | Exchange, Slack, Teams | Highest sensitivity; usually off-limits |

## Questions for discovery

For every source you want to use:

1. **Who owns it?** One named person who can approve access and answer questions.
2. **How do we read it?** API, database read replica, scheduled export, or a manual dump?
3. **What's in scope?** Which spaces, folders or tables - and which are explicitly excluded?
4. **How fresh must it be?** Real time, hourly, nightly, or a one-off?
5. **What's sensitive?** Personal data, financial data, legal holds?
6. **What are the permissions?** Can they be exported with the content?
7. **What's the "truth"?** If the wiki and the PDF disagree, which wins?

## Start with the smallest useful slice

You don't need everything on day one. The pilot needs the documents behind the use case - often one wiki space and one table. A narrow, well-understood slice ships in days; "connect all of SharePoint" takes months and fails security review.

In this topic you'll ingest the two most common formats an FDE actually receives: a **CSV export** and a **database**.
