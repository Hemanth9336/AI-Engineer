---
type: task
title: "Generate a formatted checklist"
minutes: 13
---

## Scenario

Release 4.2 ships tonight. The on-call engineer wants a deployment checklist they can tick off, generated from the release notes, in a fixed format a script will post to the team channel.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/10-format
cd /root/ai-lab/10-format
cat > notes.txt <<'EOF'
Release 4.2
- Adds single sign-on for enterprise customers.
- Requires database migration 0042 before the new version starts.
- The REPORTS_V2 feature flag must stay off until finance signs off.
- Rotate the webhook signing secret after deploying.
- Clear the CDN cache for /static/app.js.
EOF
```

## What to build

Write `/root/ai-lab/10-format/checklist.json` for `lab-fast` whose user message:

1. Wraps the full text of `notes.txt` between a `<notes>` line and a `</notes>` line.
2. Asks for a deployment checklist with **4 to 6 items**, **one item per line**, each line starting with `- [ ] `, and **no other text** - no heading, no introduction, no closing line.

Send it, save the response to `checklist-response.json` and the reply to `/root/ai-lab/10-format/checklist.md`.

The checker requires every non-empty line of `checklist.md` to be a `- [ ] ` item, and 4 to 6 of them.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Build the message with `jq -n --arg notes "$(cat notes.txt)"` and join with `\n<notes>\n` and `\n</notes>`.
- Show the exact line shape in the prompt: `- [ ] <action>`.
- `grep -vc '^- \[ \] ' checklist.md` counts the lines that are not checklist items.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/10-format
jq -n --arg notes "$(cat notes.txt)" '{
  model: "lab-fast",
  temperature: 0,
  messages: [{role: "user", content: ("Turn the release notes inside the <notes> tags into a deployment checklist for the on-call engineer.\nRules:\n- 4 to 6 items, one per line\n- every line starts with \"- [ ] \" followed by one action\n- output only the checklist lines: no heading, no introduction, no closing line\n\n<notes>\n" + $notes + "\n</notes>")}]
}' > checklist.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @checklist.json -o checklist-response.json
jq -r '.choices[0].message.content' checklist-response.json > checklist.md
cat checklist.md
```

</details>

## Check your work

```bash
D=/root/ai-lab/10-format; R=$D/checklist.json; C=$D/checklist.md
jq -e '.model == "lab-fast"' $R >/dev/null 2>&1 && echo "✅ checklist.json targets lab-fast" || echo "❌ write checklist.json for model lab-fast"
jq -e --arg n "$(cat $D/notes.txt)" '.messages[-1].content | contains("<notes>\n" + $n + "\n</notes>")' $R >/dev/null 2>&1 && echo "✅ the notes are wrapped in <notes> tags, word for word" || echo "❌ wrap the exact text of notes.txt between a <notes> line and a </notes> line"
jq -e '.messages[-1].content | contains("- [ ] ") and test("4 to 6|4-6|four to six"; "i")' $R >/dev/null 2>&1 && echo "✅ the prompt names the line format and the item count" || echo "❌ ask for 4 to 6 items, each line starting with '- [ ] '"
[ -s $C ] && [ "$(cat $C)" = "$(jq -r '.choices[0].message.content' $D/checklist-response.json 2>/dev/null)" ] && echo "✅ $C holds exactly the reply in checklist-response.json" || echo "❌ extract .choices[0].message.content from checklist-response.json into $C"
N=$(grep -c '^- \[ \] ' $C 2>/dev/null); [ "${N:-0}" -ge 4 ] && [ "${N:-0}" -le 6 ] && echo "✅ checklist.md has $N checklist items" || echo "❌ checklist.md has ${N:-0} '- [ ] ' items - it needs 4 to 6"
X=$(grep -v '^- \[ \] ' $C 2>/dev/null | grep -c .); [ -s $C ] && [ "${X:-0}" -eq 0 ] && echo "✅ there is no extra text around the items" || echo "❌ checklist.md has ${X:-0} non-checklist lines - forbid headings and introductions"
grep -qi 'migration' $C 2>/dev/null && echo "✅ the checklist covers the database migration" || echo "❌ the checklist should include the migration from the notes"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Name the format literally and forbid headings and introductions when code reads the output.
- Delimiters like `<notes>` keep the data separate from your instructions.
- Build delimited prompts with `jq --arg`, and verify the output's shape before using it.
