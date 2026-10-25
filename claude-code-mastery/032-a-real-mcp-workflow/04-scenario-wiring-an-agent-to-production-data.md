---
type: scenario
title: "Scenario: wiring an agent to production data"
minutes: 9
---

Your analytics team wants Claude to answer ad-hoc questions about the production orders database. Someone proposes the community "postgres" MCP server with the read-write `DATABASE_URL` from the deploy config, added to the repo's `.mcp.json` so everyone has it.

### Q1. What is the biggest problem with the proposal?

- A. A read-write production credential, committed for every clone and CI job, behind a server that runs arbitrary SQL
- B. Postgres is slow
- C. MCP does not support Postgres
- D. The tool names are long

<details><summary>Answer</summary>

**Answer: A** - Every part widens reach: the credential, the scope, and the tool surface.

</details>

### Q2. Which change shrinks the risk the most?

- A. Ask Claude to be careful in CLAUDE.md
- B. Use a bigger model
- C. Rename the server
- D. Use a read-only database role on a replica, scoped to the tables analytics needs

<details><summary>Answer</summary>

**Answer: D** - Least privilege at the data layer holds no matter what the agent or server does.

</details>

### Q3. Where should the server's configuration live?

- A. Local or user scope on the analysts' machines, with the credential from their environment
- B. The committed .mcp.json
- C. CLAUDE.md
- D. A public gist

<details><summary>Answer</summary>

**Answer: A** - Credentials and sensitive servers stay out of shared, committed config.

</details>

### Q4. The server exposes `query(sql)` and `execute(sql)`. What do you do in settings?

- A. Allow both
- B. Allow mcp__pg__query, deny mcp__pg__execute
- C. Deny both
- D. Nothing - the role is read-only

<details><summary>Answer</summary>

**Answer: B** - Defense in depth: deny the write tool even if the role should refuse it.

</details>

### Q5. Six months later, how do you know what the agent queried?

- A. You cannot
- B. From git log
- C. From the session transcripts and a PostToolUse audit hook on mcp__pg__.*, plus the database's own query log
- D. Ask Claude

<details><summary>Answer</summary>

**Answer: C** - Audit at the agent and at the database.

</details>
