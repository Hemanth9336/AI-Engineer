---
type: task
title: "Automate a batch of files"
minutes: 12
---

## Scenario

The support inbox exports each customer email as a text file. Every morning someone reads them all to write a one-line summary of each. Automate it with the SDK.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/19-sdk/inbox
cd /root/ai-lab/19-sdk/inbox
cat > 001.txt <<'EOF'
Subject: Can't log in
Hi, since this morning I get "invalid session" every time I try to log in on the mobile app. Web works fine. - Priya
EOF
cat > 002.txt <<'EOF'
Subject: Invoice question
Our October invoice shows 12 seats but we only have 9 users. Can you check and send a corrected invoice? - Marco
EOF
cat > 003.txt <<'EOF'
Subject: Feature request
It would be great if exports could be scheduled weekly instead of run by hand. - Lee
EOF
```

## What to build

Write `/root/ai-lab/19-sdk/summarize.py` that:

1. Reads every `*.txt` file in `/root/ai-lab/19-sdk/inbox`, in name order.
2. For each, asks `lab-mini` (cheap and fast is right for this) for a **one-line** summary of the email.
3. Writes the summary to `/root/ai-lab/19-sdk/summaries/<name>.summary.txt` - for example `001.summary.txt` - creating the folder if needed.
4. Prints one line per file to stdout: `<file name>: <summary>`.

Run it.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `for path in sorted(Path("/root/ai-lab/19-sdk/inbox").glob("*.txt")):`
- `out.write_text(summary.strip().splitlines()[0] + "\n")` guarantees one line.
- Create one `OpenAI()` client outside the loop and reuse it.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/19-sdk
cat > summarize.py <<'EOF'
from pathlib import Path

from openai import OpenAI

INBOX = Path("/root/ai-lab/19-sdk/inbox")
OUT = Path("/root/ai-lab/19-sdk/summaries")
OUT.mkdir(exist_ok=True)
client = OpenAI()

for path in sorted(INBOX.glob("*.txt")):
    resp = client.chat.completions.create(
        model="lab-mini",
        messages=[
            {"role": "system", "content": "Summarize the customer email in one line of at most 15 words."},
            {"role": "user", "content": path.read_text()},
        ],
    )
    summary = resp.choices[0].message.content.strip().splitlines()[0]
    (OUT / f"{path.stem}.summary.txt").write_text(summary + "\n")
    print(f"{path.name}: {summary}")
EOF
python summarize.py
```

</details>

## Check your work

```bash
D=/root/ai-lab/19-sdk; P=$D/summarize.py
grep -q 'from openai import OpenAI' $P 2>/dev/null && grep -q 'lab-mini' $P && echo "✅ summarize.py uses the OpenAI SDK with lab-mini" || echo "❌ summarize.py should use the OpenAI SDK and model lab-mini"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $P 2>/dev/null && [ -s $P ] && echo "✅ $P reads the key from the environment" || echo "❌ $P must not contain a key - let the SDK read it from the environment"
for n in 001 002 003; do F=$D/summaries/$n.summary.txt; [ -s $F ] && [ "$(grep -c . $F)" = 1 ] && echo "✅ $n.summary.txt has a one-line summary" || echo "❌ $F should exist and hold exactly one line"; done
printf 'Subject: Outage\nThe dashboard has been down for an hour. - Sam\n' > $D/inbox/004.txt
(cd $D && python $P > $D/.out 2>/dev/null); grep -q '^004.txt: ' $D/.out && [ -s $D/summaries/004.summary.txt ] && echo "✅ it picks up new files and prints name: summary" || echo "❌ run on a new inbox file, it should write 004.summary.txt and print '004.txt: ...'"
rm -f $D/inbox/004.txt $D/summaries/004.summary.txt $D/.out
jq -se '[.[] | select(.ok and (.client | startswith("OpenAI/Python")) and .model == "lab-mini")] | length >= 3' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged the batch on lab-mini" || echo "❌ the gateway has fewer than 3 lab-mini SDK calls"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A loop plus the SDK turns a daily chore into a script.
- Reuse one client, pick the cheapest model that does the job, and force the output shape.
- Write results to files so the job can be re-run and checked.
