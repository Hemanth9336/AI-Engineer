---
type: task
title: "Analyze a sales CSV"
minutes: 30
---

## Set up

Set up creates `/root/mastery/048-sales/sales.csv` (240 orders from June to October 2026) and `questions.md`: five questions with exact definitions.

```bash
rm -rf /root/mastery/048-sales && mkdir -p /root/mastery/048-sales && cd /root/mastery/048-sales
cat > sales.csv <<'EOF'
order_id,date,region,product,units,unit_cents,returned
5001,2026-08-18,APAC,widget,5,1266,0
5002,2026-08-26,APAC,doohickey,8,4951,0
5003,2026-10-09,APAC,widget,9,1255,0
5004,2026-06-29,US,gadget,6,2434,0
5005,2026-09-04,APAC,doohickey,9,4954,0
5006,2026-08-21,US,gizmo,3,757,0
5007,2026-09-14,US,doohickey,4,4994,0
5008,2026-09-03,APAC,gizmo,4,790,0
5009,2026-08-24,APAC,gadget,1,2405,0
5010,2026-07-08,EU,widget,7,1296,0
5011,2026-08-21,APAC,gizmo,5,776,0
5012,2026-09-04,US,gadget,4,2447,0
5013,2026-10-03,US,gadget,8,2409,1
5014,2026-10-10,APAC,gadget,5,2441,1
5015,2026-08-18,EU,gadget,3,2402,0
5016,2026-10-06,APAC,widget,6,1272,0
5017,2026-06-04,APAC,widget,2,1280,0
5018,2026-07-14,EU,gizmo,2,786,1
5019,2026-09-20,EU,gizmo,9,798,0
5020,2026-06-28,APAC,widget,6,1275,0
5021,2026-06-19,APAC,gizmo,5,797,0
5022,2026-10-19,EU,gadget,6,2429,0
5023,2026-10-13,US,widget,6,1292,0
5024,2026-06-22,APAC,doohickey,1,4961,0
5025,2026-09-22,US,doohickey,9,4997,0
5026,2026-08-16,EU,doohickey,4,4997,0
5027,2026-10-19,US,gizmo,5,766,0
5028,2026-08-06,APAC,doohickey,4,4957,0
5029,2026-09-22,EU,gizmo,4,764,1
5030,2026-08-24,APAC,gizmo,4,783,0
5031,2026-10-04,US,doohickey,2,4988,0
5032,2026-06-05,US,gadget,9,2405,0
5033,2026-08-16,US,gizmo,7,784,0
5034,2026-10-11,EU,widget,3,1292,1
5035,2026-10-09,US,widget,5,1286,0
5036,2026-08-18,APAC,widget,2,1292,0
5037,2026-06-04,EU,widget,3,1283,0
5038,2026-08-11,APAC,widget,5,1280,0
5039,2026-07-10,EU,doohickey,7,4951,0
5040,2026-08-20,EU,gizmo,7,768,0
5041,2026-07-17,APAC,gadget,8,2448,0
5042,2026-06-18,EU,gadget,2,2444,0
5043,2026-10-04,US,doohickey,8,4992,0
5044,2026-08-31,US,doohickey,2,4994,0
5045,2026-10-19,APAC,gizmo,1,793,0
5046,2026-07-18,APAC,doohickey,8,4986,0
5047,2026-07-13,EU,gizmo,9,790,0
5048,2026-09-08,EU,gadget,7,2446,1
5049,2026-08-01,US,gizmo,8,788,0
5050,2026-07-26,EU,gizmo,6,756,0
5051,2026-08-07,US,widget,5,1287,0
5052,2026-10-18,EU,doohickey,1,4956,1
5053,2026-08-24,US,gadget,6,2427,0
5054,2026-10-07,US,gizmo,3,781,0
5055,2026-09-05,US,gizmo,9,784,0
5056,2026-07-20,US,gizmo,1,755,0
5057,2026-08-29,EU,gadget,5,2402,0
5058,2026-10-11,EU,doohickey,7,4983,0
5059,2026-06-05,APAC,gadget,3,2447,1
5060,2026-08-08,US,widget,3,1280,0
5061,2026-06-08,US,widget,5,1294,0
5062,2026-08-16,APAC,widget,6,1256,0
5063,2026-10-02,US,gadget,5,2445,0
5064,2026-10-11,EU,gizmo,2,756,0
5065,2026-09-17,EU,gizmo,6,763,0
5066,2026-06-15,EU,widget,4,1264,0
5067,2026-06-27,EU,widget,4,1277,0
5068,2026-06-13,APAC,doohickey,4,4992,0
5069,2026-06-20,EU,gadget,1,2419,0
5070,2026-09-30,EU,gadget,3,2431,0
5071,2026-10-10,EU,gizmo,8,783,0
5072,2026-08-10,APAC,widget,1,1281,0
5073,2026-09-21,US,doohickey,8,4958,0
5074,2026-08-05,APAC,gadget,8,2405,0
5075,2026-06-28,APAC,doohickey,1,4978,0
5076,2026-06-18,APAC,doohickey,2,4995,0
5077,2026-06-05,EU,gadget,3,2439,0
5078,2026-07-08,EU,widget,7,1292,1
5079,2026-08-22,US,gadget,2,2441,0
5080,2026-07-20,US,gizmo,4,795,0
5081,2026-08-15,EU,widget,1,1297,1
5082,2026-06-10,APAC,gizmo,4,773,0
5083,2026-09-20,APAC,gadget,6,2428,0
5084,2026-09-26,US,gadget,5,2424,0
5085,2026-06-05,EU,doohickey,6,4992,0
5086,2026-07-09,US,doohickey,2,4953,0
5087,2026-07-25,APAC,gizmo,5,769,0
5088,2026-08-29,EU,widget,4,1287,0
5089,2026-09-06,APAC,gadget,4,2441,0
5090,2026-09-19,APAC,gizmo,7,750,0
5091,2026-10-13,EU,doohickey,5,4986,0
5092,2026-07-31,US,widget,8,1262,0
5093,2026-10-16,APAC,gadget,8,2432,0
5094,2026-06-13,APAC,widget,3,1280,0
5095,2026-10-14,US,gizmo,7,793,0
5096,2026-07-01,US,gizmo,1,792,0
5097,2026-08-02,APAC,gadget,2,2440,0
5098,2026-09-11,US,widget,9,1254,0
5099,2026-09-17,APAC,gizmo,7,798,0
5100,2026-08-12,EU,gadget,7,2433,0
5101,2026-08-01,EU,widget,6,1285,0
5102,2026-09-30,US,gadget,7,2416,1
5103,2026-07-04,EU,widget,6,1292,1
5104,2026-07-25,APAC,gizmo,4,780,0
5105,2026-08-06,EU,gadget,5,2409,0
5106,2026-09-20,US,widget,4,1273,0
5107,2026-08-21,EU,doohickey,2,4954,0
5108,2026-06-14,EU,doohickey,8,4954,0
5109,2026-08-04,APAC,doohickey,6,4999,0
5110,2026-08-11,US,widget,9,1272,0
5111,2026-07-09,US,widget,4,1293,0
5112,2026-08-31,EU,gadget,4,2444,0
5113,2026-09-20,US,gadget,4,2441,1
5114,2026-07-08,US,gadget,5,2429,0
5115,2026-06-10,APAC,gadget,7,2404,0
5116,2026-10-18,EU,doohickey,8,4980,1
5117,2026-06-05,US,widget,5,1279,0
5118,2026-09-25,US,doohickey,5,4982,0
5119,2026-10-07,APAC,gizmo,3,766,0
5120,2026-06-28,APAC,gizmo,8,786,0
5121,2026-06-10,APAC,widget,2,1295,0
5122,2026-06-11,US,gadget,7,2426,0
5123,2026-09-25,US,doohickey,5,4998,0
5124,2026-06-29,US,doohickey,3,4977,0
5125,2026-08-15,EU,gadget,3,2404,0
5126,2026-10-07,APAC,doohickey,3,4970,0
5127,2026-06-20,APAC,doohickey,9,4965,0
5128,2026-08-22,US,gadget,5,2448,0
5129,2026-07-11,US,doohickey,2,4989,0
5130,2026-09-19,EU,gizmo,4,785,0
5131,2026-08-22,EU,widget,9,1277,0
5132,2026-06-13,EU,gizmo,5,778,0
5133,2026-08-07,EU,doohickey,3,4989,0
5134,2026-08-17,US,widget,2,1274,0
5135,2026-06-12,EU,gadget,5,2441,0
5136,2026-06-23,US,doohickey,1,4984,0
5137,2026-10-03,APAC,gizmo,6,755,0
5138,2026-09-20,US,gizmo,4,793,0
5139,2026-07-16,EU,gadget,2,2406,0
5140,2026-07-24,EU,gadget,2,2412,0
5141,2026-06-07,APAC,gadget,5,2446,0
5142,2026-07-16,EU,doohickey,5,4967,0
5143,2026-07-13,US,gizmo,8,777,0
5144,2026-10-10,US,widget,5,1268,0
5145,2026-06-24,EU,widget,9,1289,1
5146,2026-08-19,APAC,gizmo,4,768,0
5147,2026-06-14,US,widget,8,1258,0
5148,2026-09-12,US,doohickey,9,4953,0
5149,2026-08-24,APAC,widget,2,1268,0
5150,2026-09-27,US,gadget,2,2423,1
5151,2026-06-21,US,widget,1,1281,0
5152,2026-10-06,EU,gizmo,1,793,0
5153,2026-06-26,US,doohickey,4,4956,0
5154,2026-10-11,US,gizmo,8,796,0
5155,2026-08-28,US,doohickey,6,4950,1
5156,2026-06-11,APAC,gadget,4,2426,0
5157,2026-10-02,EU,doohickey,7,4965,0
5158,2026-07-27,EU,gizmo,3,784,0
5159,2026-09-14,EU,gizmo,8,796,0
5160,2026-09-03,EU,doohickey,3,4988,0
5161,2026-10-19,US,widget,1,1290,0
5162,2026-08-02,APAC,doohickey,1,4976,0
5163,2026-08-14,APAC,gadget,6,2440,0
5164,2026-08-04,APAC,gizmo,6,774,0
5165,2026-06-24,US,widget,7,1296,0
5166,2026-10-08,US,gizmo,9,779,0
5167,2026-07-26,EU,gadget,6,2429,0
5168,2026-07-29,APAC,doohickey,3,4964,0
5169,2026-10-17,EU,gizmo,1,759,0
5170,2026-09-22,US,doohickey,2,4962,0
5171,2026-08-27,EU,gizmo,1,778,0
5172,2026-06-22,EU,doohickey,1,4986,0
5173,2026-06-29,EU,gadget,9,2433,0
5174,2026-09-22,US,widget,5,1299,0
5175,2026-09-29,APAC,doohickey,1,4996,0
5176,2026-06-28,US,gadget,9,2408,0
5177,2026-07-20,APAC,doohickey,2,4996,0
5178,2026-08-31,EU,doohickey,3,4997,0
5179,2026-08-25,APAC,gizmo,4,776,0
5180,2026-07-06,EU,doohickey,7,4991,0
5181,2026-07-17,US,doohickey,5,4975,0
5182,2026-08-26,APAC,doohickey,9,4992,0
5183,2026-08-14,EU,gizmo,8,764,0
5184,2026-10-02,US,gadget,8,2431,1
5185,2026-08-25,APAC,widget,3,1292,0
5186,2026-06-27,US,doohickey,1,4991,0
5187,2026-06-03,US,gizmo,6,785,0
5188,2026-07-19,APAC,gizmo,5,780,0
5189,2026-08-03,APAC,gadget,4,2436,0
5190,2026-08-14,US,doohickey,9,4993,1
5191,2026-06-22,US,widget,8,1262,0
5192,2026-06-15,APAC,widget,9,1293,0
5193,2026-06-03,EU,widget,8,1281,0
5194,2026-08-04,US,doohickey,9,4964,0
5195,2026-10-07,APAC,widget,2,1259,0
5196,2026-07-09,EU,gadget,9,2437,0
5197,2026-08-17,EU,gadget,7,2402,0
5198,2026-07-12,APAC,doohickey,2,4976,0
5199,2026-08-27,US,widget,3,1250,0
5200,2026-09-13,EU,gadget,3,2413,0
5201,2026-09-17,EU,gadget,1,2417,0
5202,2026-06-12,EU,doohickey,8,4952,0
5203,2026-08-25,US,doohickey,6,4964,0
5204,2026-08-01,US,widget,4,1284,0
5205,2026-10-19,APAC,widget,2,1283,0
5206,2026-06-06,EU,gadget,3,2411,0
5207,2026-07-03,EU,gizmo,5,776,0
5208,2026-08-31,US,gizmo,4,798,0
5209,2026-09-20,APAC,gadget,5,2424,0
5210,2026-10-10,US,doohickey,3,4964,0
5211,2026-09-14,EU,doohickey,6,4997,0
5212,2026-07-12,US,gadget,3,2408,0
5213,2026-06-25,APAC,gadget,5,2431,0
5214,2026-06-27,EU,doohickey,3,4959,0
5215,2026-07-17,EU,gizmo,4,772,0
5216,2026-08-29,US,doohickey,6,4959,0
5217,2026-10-14,US,gadget,9,2413,0
5218,2026-07-05,EU,gizmo,3,754,1
5219,2026-08-28,APAC,widget,7,1294,0
5220,2026-06-29,EU,doohickey,4,4987,0
5221,2026-10-02,APAC,gizmo,6,758,0
5222,2026-09-21,APAC,doohickey,4,4982,0
5223,2026-07-08,APAC,gadget,3,2434,0
5224,2026-09-11,EU,widget,1,1295,0
5225,2026-06-11,US,doohickey,8,4972,0
5226,2026-08-18,APAC,gizmo,9,798,0
5227,2026-06-27,EU,doohickey,2,4994,0
5228,2026-07-23,APAC,doohickey,8,4975,0
5229,2026-07-08,US,widget,2,1282,0
5230,2026-07-04,APAC,doohickey,1,4967,0
5231,2026-06-10,US,gadget,6,2407,0
5232,2026-09-01,APAC,doohickey,9,4994,0
5233,2026-07-01,EU,doohickey,4,4973,0
5234,2026-10-20,US,gadget,8,2446,0
5235,2026-06-16,EU,gizmo,9,778,0
5236,2026-07-08,EU,doohickey,3,4982,0
5237,2026-07-11,APAC,gizmo,5,792,0
5238,2026-10-04,US,gadget,9,2438,1
5239,2026-09-13,APAC,gadget,1,2446,0
5240,2026-06-02,APAC,gadget,1,2437,0
EOF
cat > questions.md <<'EOF'
# Questions about sales.csv

Net value of an order = units x unit_cents. Returned orders (returned = 1) count as zero revenue.

- q1: Net revenue in cents for Q3 2026 (2026-07-01 to 2026-09-30 inclusive), excluding returned orders. Integer.
- q2: The region with the highest net revenue over the whole file, excluding returned orders. String.
- q3: The product with the most returned units (sum of units over returned orders). String.
- q4: The median net order value in cents of EU orders that were not returned. Number (an even count takes the mean of the two middle values).
- q5: The number of distinct dates with at least one returned order. Integer.
EOF
head -3 sales.csv && echo "$(($(wc -l < sales.csv) - 1)) orders"
```

## What to build

1. Read `questions.md`. Note how each definition removes an ambiguity (net value, returns, inclusive dates, the median rule).
2. Run Claude headless with `Read`, `Write`, `Bash(python3 analysis.py)`, and `Bash(head *)`, saving `analysis-run.json`:
   > Answer the questions in questions.md about sales.csv. Compute every answer with code: write analysis.py that loads sales.csv with the csv module, computes q1 to q5 exactly as defined, writes answers.json, and prints it. Run it. Never estimate from reading the rows.
3. Look at `analysis.py`: does every answer come from code, and is anything hard-coded?

The checker computes all five answers itself and compares them exactly. It also re-runs your `analysis.py` in a clean folder, and runs it once more on a modified CSV to prove the numbers come from the data.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- If an answer is off, check the definition in questions.md first - date bounds and returns are the usual culprits.
- statistics.median already takes the mean of the two middle values for an even count.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/048-sales
claude -p 'Answer the questions in questions.md about sales.csv. Compute every answer with code: write analysis.py that loads sales.csv with the csv module, computes q1 to q5 exactly as defined, writes answers.json, and prints it. Run it. Never estimate from reading the rows.' --allowedTools Read Write "Bash(python3 analysis.py)" "Bash(head *)" --output-format json < /dev/null > analysis-run.json
jq -r .result analysis-run.json
cat answers.json
```

</details>

## Check your work

```bash
D=/root/mastery/048-sales; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
python3 - <<'PYEOF'
import glob, hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def text(p):
    try:
        return Path(p).read_text()
    except Exception:
        return ""
def sha(p):
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except Exception:
        return None
def sh(cmd, cwd=None, env=None, input=None, timeout=60):
    try:
        r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, cwd=cwd, input=input,
                           timeout=timeout, env=dict(os.environ, **(env or {})))
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"
def sessions(d):
    # Claude Code saves every session (console or -p) as ~/.claude/projects/<dir>/<id>.jsonl, one JSON row per event
    real, out = os.path.realpath(d), []
    for f in sorted(glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")), key=os.path.getmtime):
        rows = []
        for line in open(f, errors="replace"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
        if any(r.get("cwd") and os.path.realpath(r["cwd"]) == real for r in rows):
            out.append(rows)
    return out
def ran(pat, d=None):
    return [rows for rows in sessions(d or os.getcwd()) if any(re.search(pat, p, re.I | re.S) for p in prompts(rows))]
def content(r):
    c = (r.get("message") or {}).get("content")
    return c if isinstance(c, list) else ([{"type": "text", "text": c}] if isinstance(c, str) else [])
def prompts(rows):
    return [b.get("text", "") for r in rows if r.get("type") == "user" and not r.get("isMeta") for b in content(r) if b.get("type") == "text"]
def uses(rows):
    return [b for r in rows if r.get("type") == "assistant" for b in content(r) if b.get("type") == "tool_use"]
def results(rows):
    return [b for r in rows if r.get("type") == "user" for b in content(r) if b.get("type") == "tool_result"]
def models(rows):
    return {(r.get("message") or {}).get("model") for r in rows if r.get("type") == "assistant"} - {None, "<synthetic>"}
def is_haiku(m):
    return bool(m) and ("haiku" in m.lower() or m == os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL"))
def events(p):
    out = []
    for line in text(p).splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out
def init(ev):
    return next((e for e in ev if e.get("type") == "system" and e.get("subtype") == "init"), {})
def result(ev):
    return next((e for e in ev if e.get("type") == "result"), {})
def ev_uses(ev):
    return [b for e in ev if e.get("type") == "assistant" for b in content(e) if b.get("type") == "tool_use"]
def transcript(sid):
    for f in glob.glob(os.path.expanduser(f"~/.claude/projects/*/{sid}.jsonl")):
        rows = []
        for line in open(f, errors="replace"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
        return f, rows
    return None, []
def rtext(b):
    c = b.get("content")
    return c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))
def result_for(rows, pred):
    ids = [u["id"] for u in uses(rows) if pred(u)]
    return [b for b in results(rows) if b.get("tool_use_id") in ids]
def run_rows(p):
    env = load(p) or {}
    return transcript(env.get("session_id") or "none")[1]
SALES = 'order_id,date,region,product,units,unit_cents,returned\n5001,2026-08-18,APAC,widget,5,1266,0\n5002,2026-08-26,APAC,doohickey,8,4951,0\n5003,2026-10-09,APAC,widget,9,1255,0\n5004,2026-06-29,US,gadget,6,2434,0\n5005,2026-09-04,APAC,doohickey,9,4954,0\n5006,2026-08-21,US,gizmo,3,757,0\n5007,2026-09-14,US,doohickey,4,4994,0\n5008,2026-09-03,APAC,gizmo,4,790,0\n5009,2026-08-24,APAC,gadget,1,2405,0\n5010,2026-07-08,EU,widget,7,1296,0\n5011,2026-08-21,APAC,gizmo,5,776,0\n5012,2026-09-04,US,gadget,4,2447,0\n5013,2026-10-03,US,gadget,8,2409,1\n5014,2026-10-10,APAC,gadget,5,2441,1\n5015,2026-08-18,EU,gadget,3,2402,0\n5016,2026-10-06,APAC,widget,6,1272,0\n5017,2026-06-04,APAC,widget,2,1280,0\n5018,2026-07-14,EU,gizmo,2,786,1\n5019,2026-09-20,EU,gizmo,9,798,0\n5020,2026-06-28,APAC,widget,6,1275,0\n5021,2026-06-19,APAC,gizmo,5,797,0\n5022,2026-10-19,EU,gadget,6,2429,0\n5023,2026-10-13,US,widget,6,1292,0\n5024,2026-06-22,APAC,doohickey,1,4961,0\n5025,2026-09-22,US,doohickey,9,4997,0\n5026,2026-08-16,EU,doohickey,4,4997,0\n5027,2026-10-19,US,gizmo,5,766,0\n5028,2026-08-06,APAC,doohickey,4,4957,0\n5029,2026-09-22,EU,gizmo,4,764,1\n5030,2026-08-24,APAC,gizmo,4,783,0\n5031,2026-10-04,US,doohickey,2,4988,0\n5032,2026-06-05,US,gadget,9,2405,0\n5033,2026-08-16,US,gizmo,7,784,0\n5034,2026-10-11,EU,widget,3,1292,1\n5035,2026-10-09,US,widget,5,1286,0\n5036,2026-08-18,APAC,widget,2,1292,0\n5037,2026-06-04,EU,widget,3,1283,0\n5038,2026-08-11,APAC,widget,5,1280,0\n5039,2026-07-10,EU,doohickey,7,4951,0\n5040,2026-08-20,EU,gizmo,7,768,0\n5041,2026-07-17,APAC,gadget,8,2448,0\n5042,2026-06-18,EU,gadget,2,2444,0\n5043,2026-10-04,US,doohickey,8,4992,0\n5044,2026-08-31,US,doohickey,2,4994,0\n5045,2026-10-19,APAC,gizmo,1,793,0\n5046,2026-07-18,APAC,doohickey,8,4986,0\n5047,2026-07-13,EU,gizmo,9,790,0\n5048,2026-09-08,EU,gadget,7,2446,1\n5049,2026-08-01,US,gizmo,8,788,0\n5050,2026-07-26,EU,gizmo,6,756,0\n5051,2026-08-07,US,widget,5,1287,0\n5052,2026-10-18,EU,doohickey,1,4956,1\n5053,2026-08-24,US,gadget,6,2427,0\n5054,2026-10-07,US,gizmo,3,781,0\n5055,2026-09-05,US,gizmo,9,784,0\n5056,2026-07-20,US,gizmo,1,755,0\n5057,2026-08-29,EU,gadget,5,2402,0\n5058,2026-10-11,EU,doohickey,7,4983,0\n5059,2026-06-05,APAC,gadget,3,2447,1\n5060,2026-08-08,US,widget,3,1280,0\n5061,2026-06-08,US,widget,5,1294,0\n5062,2026-08-16,APAC,widget,6,1256,0\n5063,2026-10-02,US,gadget,5,2445,0\n5064,2026-10-11,EU,gizmo,2,756,0\n5065,2026-09-17,EU,gizmo,6,763,0\n5066,2026-06-15,EU,widget,4,1264,0\n5067,2026-06-27,EU,widget,4,1277,0\n5068,2026-06-13,APAC,doohickey,4,4992,0\n5069,2026-06-20,EU,gadget,1,2419,0\n5070,2026-09-30,EU,gadget,3,2431,0\n5071,2026-10-10,EU,gizmo,8,783,0\n5072,2026-08-10,APAC,widget,1,1281,0\n5073,2026-09-21,US,doohickey,8,4958,0\n5074,2026-08-05,APAC,gadget,8,2405,0\n5075,2026-06-28,APAC,doohickey,1,4978,0\n5076,2026-06-18,APAC,doohickey,2,4995,0\n5077,2026-06-05,EU,gadget,3,2439,0\n5078,2026-07-08,EU,widget,7,1292,1\n5079,2026-08-22,US,gadget,2,2441,0\n5080,2026-07-20,US,gizmo,4,795,0\n5081,2026-08-15,EU,widget,1,1297,1\n5082,2026-06-10,APAC,gizmo,4,773,0\n5083,2026-09-20,APAC,gadget,6,2428,0\n5084,2026-09-26,US,gadget,5,2424,0\n5085,2026-06-05,EU,doohickey,6,4992,0\n5086,2026-07-09,US,doohickey,2,4953,0\n5087,2026-07-25,APAC,gizmo,5,769,0\n5088,2026-08-29,EU,widget,4,1287,0\n5089,2026-09-06,APAC,gadget,4,2441,0\n5090,2026-09-19,APAC,gizmo,7,750,0\n5091,2026-10-13,EU,doohickey,5,4986,0\n5092,2026-07-31,US,widget,8,1262,0\n5093,2026-10-16,APAC,gadget,8,2432,0\n5094,2026-06-13,APAC,widget,3,1280,0\n5095,2026-10-14,US,gizmo,7,793,0\n5096,2026-07-01,US,gizmo,1,792,0\n5097,2026-08-02,APAC,gadget,2,2440,0\n5098,2026-09-11,US,widget,9,1254,0\n5099,2026-09-17,APAC,gizmo,7,798,0\n5100,2026-08-12,EU,gadget,7,2433,0\n5101,2026-08-01,EU,widget,6,1285,0\n5102,2026-09-30,US,gadget,7,2416,1\n5103,2026-07-04,EU,widget,6,1292,1\n5104,2026-07-25,APAC,gizmo,4,780,0\n5105,2026-08-06,EU,gadget,5,2409,0\n5106,2026-09-20,US,widget,4,1273,0\n5107,2026-08-21,EU,doohickey,2,4954,0\n5108,2026-06-14,EU,doohickey,8,4954,0\n5109,2026-08-04,APAC,doohickey,6,4999,0\n5110,2026-08-11,US,widget,9,1272,0\n5111,2026-07-09,US,widget,4,1293,0\n5112,2026-08-31,EU,gadget,4,2444,0\n5113,2026-09-20,US,gadget,4,2441,1\n5114,2026-07-08,US,gadget,5,2429,0\n5115,2026-06-10,APAC,gadget,7,2404,0\n5116,2026-10-18,EU,doohickey,8,4980,1\n5117,2026-06-05,US,widget,5,1279,0\n5118,2026-09-25,US,doohickey,5,4982,0\n5119,2026-10-07,APAC,gizmo,3,766,0\n5120,2026-06-28,APAC,gizmo,8,786,0\n5121,2026-06-10,APAC,widget,2,1295,0\n5122,2026-06-11,US,gadget,7,2426,0\n5123,2026-09-25,US,doohickey,5,4998,0\n5124,2026-06-29,US,doohickey,3,4977,0\n5125,2026-08-15,EU,gadget,3,2404,0\n5126,2026-10-07,APAC,doohickey,3,4970,0\n5127,2026-06-20,APAC,doohickey,9,4965,0\n5128,2026-08-22,US,gadget,5,2448,0\n5129,2026-07-11,US,doohickey,2,4989,0\n5130,2026-09-19,EU,gizmo,4,785,0\n5131,2026-08-22,EU,widget,9,1277,0\n5132,2026-06-13,EU,gizmo,5,778,0\n5133,2026-08-07,EU,doohickey,3,4989,0\n5134,2026-08-17,US,widget,2,1274,0\n5135,2026-06-12,EU,gadget,5,2441,0\n5136,2026-06-23,US,doohickey,1,4984,0\n5137,2026-10-03,APAC,gizmo,6,755,0\n5138,2026-09-20,US,gizmo,4,793,0\n5139,2026-07-16,EU,gadget,2,2406,0\n5140,2026-07-24,EU,gadget,2,2412,0\n5141,2026-06-07,APAC,gadget,5,2446,0\n5142,2026-07-16,EU,doohickey,5,4967,0\n5143,2026-07-13,US,gizmo,8,777,0\n5144,2026-10-10,US,widget,5,1268,0\n5145,2026-06-24,EU,widget,9,1289,1\n5146,2026-08-19,APAC,gizmo,4,768,0\n5147,2026-06-14,US,widget,8,1258,0\n5148,2026-09-12,US,doohickey,9,4953,0\n5149,2026-08-24,APAC,widget,2,1268,0\n5150,2026-09-27,US,gadget,2,2423,1\n5151,2026-06-21,US,widget,1,1281,0\n5152,2026-10-06,EU,gizmo,1,793,0\n5153,2026-06-26,US,doohickey,4,4956,0\n5154,2026-10-11,US,gizmo,8,796,0\n5155,2026-08-28,US,doohickey,6,4950,1\n5156,2026-06-11,APAC,gadget,4,2426,0\n5157,2026-10-02,EU,doohickey,7,4965,0\n5158,2026-07-27,EU,gizmo,3,784,0\n5159,2026-09-14,EU,gizmo,8,796,0\n5160,2026-09-03,EU,doohickey,3,4988,0\n5161,2026-10-19,US,widget,1,1290,0\n5162,2026-08-02,APAC,doohickey,1,4976,0\n5163,2026-08-14,APAC,gadget,6,2440,0\n5164,2026-08-04,APAC,gizmo,6,774,0\n5165,2026-06-24,US,widget,7,1296,0\n5166,2026-10-08,US,gizmo,9,779,0\n5167,2026-07-26,EU,gadget,6,2429,0\n5168,2026-07-29,APAC,doohickey,3,4964,0\n5169,2026-10-17,EU,gizmo,1,759,0\n5170,2026-09-22,US,doohickey,2,4962,0\n5171,2026-08-27,EU,gizmo,1,778,0\n5172,2026-06-22,EU,doohickey,1,4986,0\n5173,2026-06-29,EU,gadget,9,2433,0\n5174,2026-09-22,US,widget,5,1299,0\n5175,2026-09-29,APAC,doohickey,1,4996,0\n5176,2026-06-28,US,gadget,9,2408,0\n5177,2026-07-20,APAC,doohickey,2,4996,0\n5178,2026-08-31,EU,doohickey,3,4997,0\n5179,2026-08-25,APAC,gizmo,4,776,0\n5180,2026-07-06,EU,doohickey,7,4991,0\n5181,2026-07-17,US,doohickey,5,4975,0\n5182,2026-08-26,APAC,doohickey,9,4992,0\n5183,2026-08-14,EU,gizmo,8,764,0\n5184,2026-10-02,US,gadget,8,2431,1\n5185,2026-08-25,APAC,widget,3,1292,0\n5186,2026-06-27,US,doohickey,1,4991,0\n5187,2026-06-03,US,gizmo,6,785,0\n5188,2026-07-19,APAC,gizmo,5,780,0\n5189,2026-08-03,APAC,gadget,4,2436,0\n5190,2026-08-14,US,doohickey,9,4993,1\n5191,2026-06-22,US,widget,8,1262,0\n5192,2026-06-15,APAC,widget,9,1293,0\n5193,2026-06-03,EU,widget,8,1281,0\n5194,2026-08-04,US,doohickey,9,4964,0\n5195,2026-10-07,APAC,widget,2,1259,0\n5196,2026-07-09,EU,gadget,9,2437,0\n5197,2026-08-17,EU,gadget,7,2402,0\n5198,2026-07-12,APAC,doohickey,2,4976,0\n5199,2026-08-27,US,widget,3,1250,0\n5200,2026-09-13,EU,gadget,3,2413,0\n5201,2026-09-17,EU,gadget,1,2417,0\n5202,2026-06-12,EU,doohickey,8,4952,0\n5203,2026-08-25,US,doohickey,6,4964,0\n5204,2026-08-01,US,widget,4,1284,0\n5205,2026-10-19,APAC,widget,2,1283,0\n5206,2026-06-06,EU,gadget,3,2411,0\n5207,2026-07-03,EU,gizmo,5,776,0\n5208,2026-08-31,US,gizmo,4,798,0\n5209,2026-09-20,APAC,gadget,5,2424,0\n5210,2026-10-10,US,doohickey,3,4964,0\n5211,2026-09-14,EU,doohickey,6,4997,0\n5212,2026-07-12,US,gadget,3,2408,0\n5213,2026-06-25,APAC,gadget,5,2431,0\n5214,2026-06-27,EU,doohickey,3,4959,0\n5215,2026-07-17,EU,gizmo,4,772,0\n5216,2026-08-29,US,doohickey,6,4959,0\n5217,2026-10-14,US,gadget,9,2413,0\n5218,2026-07-05,EU,gizmo,3,754,1\n5219,2026-08-28,APAC,widget,7,1294,0\n5220,2026-06-29,EU,doohickey,4,4987,0\n5221,2026-10-02,APAC,gizmo,6,758,0\n5222,2026-09-21,APAC,doohickey,4,4982,0\n5223,2026-07-08,APAC,gadget,3,2434,0\n5224,2026-09-11,EU,widget,1,1295,0\n5225,2026-06-11,US,doohickey,8,4972,0\n5226,2026-08-18,APAC,gizmo,9,798,0\n5227,2026-06-27,EU,doohickey,2,4994,0\n5228,2026-07-23,APAC,doohickey,8,4975,0\n5229,2026-07-08,US,widget,2,1282,0\n5230,2026-07-04,APAC,doohickey,1,4967,0\n5231,2026-06-10,US,gadget,6,2407,0\n5232,2026-09-01,APAC,doohickey,9,4994,0\n5233,2026-07-01,EU,doohickey,4,4973,0\n5234,2026-10-20,US,gadget,8,2446,0\n5235,2026-06-16,EU,gizmo,9,778,0\n5236,2026-07-08,EU,doohickey,3,4982,0\n5237,2026-07-11,APAC,gizmo,5,792,0\n5238,2026-10-04,US,gadget,9,2438,1\n5239,2026-09-13,APAC,gadget,1,2446,0\n5240,2026-06-02,APAC,gadget,1,2437,0'

import csv, io, statistics, shutil
ok(text("sales.csv").rstrip() == SALES.rstrip(), "sales.csv is unchanged", "don't edit sales.csv")
rs = list(csv.DictReader(io.StringIO(SALES)))
net = lambda r: int(r["units"]) * int(r["unit_cents"])
keep = [r for r in rs if r["returned"] == "0"]
reg, ret = {}, {}
for r in keep:
    reg[r["region"]] = reg.get(r["region"], 0) + net(r)
for r in rs:
    if r["returned"] == "1":
        ret[r["product"]] = ret.get(r["product"], 0) + int(r["units"])
want = {"q1": sum(net(r) for r in keep if "2026-07-01" <= r["date"] <= "2026-09-30"), "q2": max(reg, key=reg.get), "q3": max(ret, key=ret.get),
        "q4": statistics.median(net(r) for r in keep if r["region"] == "EU"), "q5": len({r["date"] for r in rs if r["returned"] == "1"})}
a = load("answers.json") or {}
for k, v in want.items():
    got = a.get(k)
    same = (isinstance(got, (int, float)) and not isinstance(got, bool) and abs(got - v) < 0.01) if isinstance(v, (int, float)) else got == v
    ok(same, f"{k} is exactly right ({v})", f"{k} is wrong: got {got!r}")
ok(os.path.exists("analysis.py") and "csv" in text("analysis.py"), "analysis.py is saved next to the answers", "keep the script that computed the answers as analysis.py")
with tempfile.TemporaryDirectory() as t:
    shutil.copy("analysis.py", t)
    Path(t, "sales.csv").write_text(SALES + "\n")
    rc, out, err = sh("python3 analysis.py", cwd=t)
    again = load(os.path.join(t, "answers.json")) or {}
ok(rc == 0 and again == a, "re-running analysis.py reproduces answers.json exactly", f"python3 analysis.py in a clean folder should reproduce answers.json - rc {rc}, {err.strip()[-200:]}")
alt = "\n".join(SALES.splitlines()[:1] + [l for l in SALES.splitlines()[1:] if not l.split(",")[1].startswith("2026-08")])
with tempfile.TemporaryDirectory() as t:
    shutil.copy("analysis.py", t)
    Path(t, "sales.csv").write_text(alt + "\n")
    rc, out, err = sh("python3 analysis.py", cwd=t)
    moved = load(os.path.join(t, "answers.json")) or {}
alt_rs = list(csv.DictReader(io.StringIO(alt)))
alt_q1 = sum(net(r) for r in alt_rs if r["returned"] == "0" and "2026-07-01" <= r["date"] <= "2026-09-30")
ok(rc == 0 and moved.get("q1") == alt_q1, "analysis.py computes from the data (different CSV, different answer)", "analysis.py must compute from sales.csv - on a CSV without August its q1 should change accordingly")
rows = run_rows("analysis-run.json")
ran = result_for(rows, lambda u: u.get("name") == "Bash" and "analysis.py" in (u.get("input") or {}).get("command", ""))
ok(ran and not ran[-1].get("is_error"), "Claude ran analysis.py itself", "the headless run should execute python3 analysis.py")
PYEOF
```

## What you learned

- Exact answers come from code the agent writes and runs, never from reading rows.
- Definitions in the question decide the answer; pin them before asking.
- Keep the script: it is the audit trail and reproduces the numbers on demand.
