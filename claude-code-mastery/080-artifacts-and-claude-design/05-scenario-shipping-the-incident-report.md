---
type: scenario
title: "Scenario: shipping the incident report"
minutes: 7
---

After a two-hour outage, you ask Claude to turn the timeline, graphs and root-cause notes into an incident report as an artifact. Leadership, two partner companies, and the whole engineering org need to read it. Some graphs come from your internal metrics MCP server.

### Q1. The graphs come from a local MCP server. Will the published page show live graphs?

- A. Yes
- B. No - local MCP servers can feed data while building, but the published page can't call them; bake the graphs into the page as a snapshot
- C. Only for you
- D. Only on mobile

<details><summary>Answer</summary>

**Answer: B** - An incident report should be a frozen record anyway.

</details>

### Q2. How do you share it with the engineering org but not the partners yet?

- A. Make it public
- B. Make everyone an editor
- C. Email the HTML
- D. Share with everyone in the organization (sign-in required); keep it off public links until it's approved

<details><summary>Answer</summary>

**Answer: D** - Org sharing limits viewers to signed-in colleagues.

</details>

### Q3. Partners need it next week, and your Team plan has External sharing off. What has to happen?

- A. Nothing
- B. An Owner enables External sharing, then you share that version publicly (public viewers see an unverified-content notice)
- C. Upload it elsewhere
- D. Use /design

<details><summary>Answer</summary>

**Answer: B** - Public links are an organization decision.

</details>

### Q4. Reviewers comment while you're still editing. How do you avoid showing them half-finished edits?

- A. Stop editing
- B. Create a new artifact each time
- C. Keep publishing new versions, and use Share to choose which version viewers see
- D. Turn off comments

<details><summary>Answer</summary>

**Answer: C** - Versions let you iterate on one URL without exposing every draft.

</details>
