---
type: quiz
title: "Quick check: the streaming run that refuses to start"
minutes: 8
---

### Q1. `claude -p 'hi' --output-format stream-json` exits 1 immediately. Why?

- A. No network
- B. stream-json is interactive only
- C. The prompt is too short
- D. In print mode stream-json requires --verbose

<details><summary>Answer</summary>

**Answer: D** - Add --verbose.

</details>

### Q2. Which event in a stream tells you which MCP servers failed to load?

- A. The result event
- B. The first assistant event
- C. The system init event (mcp_server_errors)
- D. None

<details><summary>Answer</summary>

**Answer: C** - init lists tools and servers, including skipped --mcp-config entries.

</details>

### Q3. You pass `--json-schema '{"type":"nope"}'`. What happens?

- A. The model ignores it
- B. It falls back to text
- C. claude exits with 'not a valid JSON Schema' before any model call
- D. structured_output is null

<details><summary>Answer</summary>

**Answer: C** - Invalid schemas are rejected up front.

</details>

### Q4. A run returns subtype success, exit 0, and no structured_output. Should the gate pass it?

- A. Yes - it succeeded
- B. No - the required output is missing, so fail closed
- C. Only on weekdays
- D. Yes, if result has text

<details><summary>Answer</summary>

**Answer: B** - Success of the run is not success of the contract.

</details>
