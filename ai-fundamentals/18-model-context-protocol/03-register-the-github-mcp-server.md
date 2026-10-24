---
type: task
title: "Register the GitHub MCP server"
minutes: 13
---

## Scenario

Your team wants everyone's Claude Code to have the official GitHub MCP server in the `platform-tools` repo, without anyone committing their personal access token.

## Set up

```bash
mkdir -p /root/ai-lab/18-mcp/platform-tools
cd /root/ai-lab/18-mcp/platform-tools
git init -q 2>/dev/null || true
```

## What to build

In `/root/ai-lab/18-mcp/platform-tools`:

1. Use `claude mcp add` to register a server named `github` at **project scope**, using the **http** transport, URL `https://api.githubcopilot.com/mcp/`, and the header `Authorization: Bearer ${GITHUB_PAT}` - with `${GITHUB_PAT}` saved literally, not expanded.
2. Look at the `.mcp.json` it created.
3. Save the output of `claude mcp get github` to `/root/ai-lab/18-mcp/get.txt`.

You don't need a real token for this task: the checker looks at the configuration, not the connection. If you do have a GitHub token, keep it in your environment as `GITHUB_PAT` - never in a file.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Options come before the name: `claude mcp add --scope project --transport http github <url> --header '...'`.
- Single quotes around the header keep `${GITHUB_PAT}` literal.
- `jq . .mcp.json` shows what was saved.
- To redo it, remove the old entry first: `claude mcp remove github -s project`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/18-mcp/platform-tools
claude mcp remove github -s project 2>/dev/null || true
claude mcp add --scope project --transport http github https://api.githubcopilot.com/mcp/ \
  --header 'Authorization: Bearer ${GITHUB_PAT}'
jq . .mcp.json
claude mcp get github > /root/ai-lab/18-mcp/get.txt 2>&1
cat /root/ai-lab/18-mcp/get.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/18-mcp; M=$D/platform-tools/.mcp.json
jq -e '.mcpServers.github' $M >/dev/null 2>&1 && echo "✅ .mcp.json in platform-tools defines a github server" || echo "❌ add the server with --scope project from inside platform-tools"
jq -e '.mcpServers.github.type == "http"' $M >/dev/null 2>&1 && echo "✅ it uses the http transport" || echo "❌ use --transport http"
jq -e '.mcpServers.github.url | test("^https://api\\.githubcopilot\\.com/mcp/?$")' $M >/dev/null 2>&1 && echo "✅ it points at the official GitHub MCP URL" || echo "❌ the URL must be https://api.githubcopilot.com/mcp/"
jq -e '.mcpServers.github.headers.Authorization == "Bearer ${GITHUB_PAT}"' $M >/dev/null 2>&1 && echo "✅ the token is the literal placeholder \${GITHUB_PAT}" || echo "❌ the Authorization header must be exactly 'Bearer \${GITHUB_PAT}' - use single quotes"
! grep -rEq 'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}' $D 2>/dev/null && [ -f $M ] && echo "✅ no GitHub token is stored in any file" || echo "❌ a real GitHub token is in a file under $D - remove it and rotate it"
grep -q 'Project config' $D/get.txt 2>/dev/null && grep -q 'api.githubcopilot.com/mcp' $D/get.txt && echo "✅ get.txt shows the project-scoped github server" || echo "❌ save the output of claude mcp get github to $D/get.txt"
```

## What you learned

- MCP is a standard way to plug tools and data into any AI client.
- Project scope writes `.mcp.json`, which the whole team shares through git.
- Reference secrets as `${VAR}` and quote them so the shell doesn't expand them.
