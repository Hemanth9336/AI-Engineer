---
type: task
title: "Build a support ticket triage tool"
minutes: 60
---

## Scenario

**Project.** The support team gets hundreds of tickets a day and sorts them by hand. Build a command-line tool that triages a file of tickets with a model: category, priority, and a one-line summary for each - as validated JSON that other tools can trust.

This project combines what you've learned: the OpenAI SDK (topic 19), JSON mode and validation (topic 15), choosing a model (topic 13), clear prompts with allowed values (topics 06-11), and key hygiene.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/24-triage
cd /root/ai-lab/24-triage
cat > tickets.jsonl <<'EOF'
{"id": "T-1001", "text": "I was charged twice for my October subscription. Please refund one of the payments."}
{"id": "T-1002", "text": "The mobile app crashes every time I open the reports tab on Android 15."}
{"id": "T-1003", "text": "Nobody on our team can log in - the whole dashboard returns 500 errors since 09:00."}
{"id": "T-1004", "text": "How do I export my data to CSV?"}
{"id": "T-1005", "text": "Our invoice lists the wrong company address, can you fix it for next month?"}
EOF
```

## What to build

Write `/root/ai-lab/24-triage/triage.py`, used like this:

```bash
python triage.py tickets.jsonl > triage.json
```

**Input**: a JSON Lines file, one ticket per line with `id` and `text`.

**Output** on stdout: a JSON **array**, one object per ticket **in input order**, each with exactly these keys:

| Key | Allowed values |
|---|---|
| `id` | The ticket's id, copied from the input (not from the model) |
| `category` | `billing`, `bug`, `outage`, `question` |
| `priority` | `P1` (service down for many users), `P2` (broken or money wrong), `P3` (questions and small requests) |
| `summary` | One sentence, at most 20 words |

**Requirements**:

1. Use the OpenAI SDK with **JSON mode** and `temperature: 0`. Choose `lab-mini` or `lab-fast`.
2. **Validate** each model reply in code: valid JSON, allowed category and priority, a non-empty summary. If it's invalid, retry once; if it's still invalid, exit with an error on stderr rather than emitting bad data.
3. With no argument, print a usage message to stderr and exit 2.
4. No key or URL in the code.

Run it on `tickets.jsonl` and save the result to `/root/ai-lab/24-triage/triage.json`. The checker also runs your tool on tickets it hasn't shown you.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Keep the allowed values in Python sets and check `d.get("category") in CATEGORIES`.
- Build each output object yourself - `{"id": ticket["id"], **fields}` - so the id can't be changed by the model.
- `json.dump(results, sys.stdout, indent=2)` writes the array.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/24-triage
cat > triage.py <<'EOF'
import json
import sys

from openai import OpenAI

MODEL = "lab-fast"
CATEGORIES = {"billing", "bug", "outage", "question"}
PRIORITIES = {"P1", "P2", "P3"}
SYSTEM = """You triage customer support tickets. Reply with only a JSON object with these keys:
"category": one of "billing", "bug", "outage", "question"
"priority": "P1" if the service is down for many users, "P2" if something is broken or money is wrong, "P3" for questions and small requests
"summary": one sentence of at most 20 words"""


def valid(d):
    return (isinstance(d, dict) and d.get("category") in CATEGORIES and d.get("priority") in PRIORITIES
            and isinstance(d.get("summary"), str) and d["summary"].strip() != "")


def triage(client, text):
    for _ in range(2):
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
        )
        try:
            d = json.loads(resp.choices[0].message.content)
        except (json.JSONDecodeError, TypeError):
            continue
        if valid(d):
            return {"category": d["category"], "priority": d["priority"], "summary": d["summary"].strip()}
    raise ValueError("model returned invalid triage twice")


def main():
    if len(sys.argv) != 2:
        print("usage: triage.py TICKETS.jsonl", file=sys.stderr)
        sys.exit(2)
    client = OpenAI()
    results = []
    with open(sys.argv[1]) as f:
        for line in f:
            if not line.strip():
                continue
            ticket = json.loads(line)
            try:
                results.append({"id": ticket["id"], **triage(client, ticket["text"])})
            except ValueError as e:
                print(f"triage: {ticket['id']}: {e}", file=sys.stderr)
                sys.exit(1)
    json.dump(results, sys.stdout, indent=2)
    print()
    print(f"triaged {len(results)} tickets", file=sys.stderr)


if __name__ == "__main__":
    main()
EOF
python triage.py tickets.jsonl > triage.json
jq -c '.[]' triage.json
```

</details>

## Check your work

```bash
D=/root/ai-lab/24-triage; P=$D/triage.py; J=$D/triage.json; T=$(mktemp -d)
grep -q 'from openai import OpenAI' $P 2>/dev/null && grep -q 'json_object' $P && echo "✅ triage.py uses the OpenAI SDK with JSON mode" || echo "❌ use the OpenAI SDK with response_format json_object"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $P 2>/dev/null && [ -s $P ] && echo "✅ $P reads the key from the environment" || echo "❌ $P must not contain a key - let the SDK read it from the environment"
jq -e 'type == "array" and length == 5' $J >/dev/null 2>&1 && echo "✅ triage.json is an array of 5 results" || echo "❌ triage.json should be a JSON array with one object per ticket"
jq -e '[.[].id] == ["T-1001", "T-1002", "T-1003", "T-1004", "T-1005"]' $J >/dev/null 2>&1 && echo "✅ ids are copied in input order" || echo "❌ keep the ticket ids, in input order"
jq -e 'all(.[]; (keys == ["category", "id", "priority", "summary"]) and (.category | IN("billing", "bug", "outage", "question")) and (.priority | IN("P1", "P2", "P3")) and (.summary | type == "string" and length > 0))' $J >/dev/null 2>&1 && echo "✅ every result has exactly id, category, priority, summary with allowed values" || echo "❌ each object needs exactly id, category, priority, summary - with allowed values only"
jq -e 'all(.[]; (.summary | split(" ") | length) <= 25)' $J >/dev/null 2>&1 && echo "✅ summaries are short" || echo "❌ keep each summary to one short sentence"
jq -e '(.[] | select(.id == "T-1003")) | .category == "outage" and .priority == "P1"' $J >/dev/null 2>&1 && echo "✅ the login outage is outage / P1" || echo "❌ T-1003 (nobody can log in, 500 errors) should be outage with priority P1"
jq -e '(.[] | select(.id == "T-1001") | .category == "billing") and (.[] | select(.id == "T-1004") | .category == "question")' $J >/dev/null 2>&1 && echo "✅ the double charge is billing and the CSV question is a question" || echo "❌ T-1001 should be billing and T-1004 question"
printf '%s\n' '{"id": "X-1", "text": "Can I change my username?"}' '{"id": "X-2", "text": "The checkout page shows a blank screen for every user."}' > $T/new.jsonl
(cd $D && python $P $T/new.jsonl > $T/out.json 2>/dev/null); jq -e '[.[].id] == ["X-1", "X-2"] and all(.[]; (.category | IN("billing", "bug", "outage", "question")) and (.priority | IN("P1", "P2", "P3")))' $T/out.json >/dev/null 2>&1 && echo "✅ it triages tickets it hasn't seen" || echo "❌ python triage.py on a new file should print a valid array for X-1 and X-2"
python $P >/dev/null 2>$T/err; rc=$?; [ $rc = 2 ] && [ -s $T/err ] && echo "✅ no argument: usage on stderr, exit 2" || echo "❌ with no argument print usage to stderr and exit 2 (exit was $rc)"
jq -se 'any(.[]; .ok and .json_mode and (.client | startswith("OpenAI/Python")) and (.model | IN("lab-mini", "lab-fast")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged JSON-mode SDK calls" || echo "❌ the gateway has no JSON-mode calls from the OpenAI SDK on lab-mini or lab-fast"
rm -rf $T
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A real AI tool is mostly normal engineering: input, validation, errors, exit codes.
- Copy trusted fields (like ids) from your input, never from the model.
- Validate every model reply against allowed values, retry once, then fail loudly.
