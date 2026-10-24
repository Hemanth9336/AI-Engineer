---
type: lesson
title: "Variables, strings, and f-strings"
minutes: 5
---

You don't need to be a software engineer to be an FDE, but you will write small Python scripts every day: call a model, read a file, reshape some JSON. This topic covers just enough Python for the rest of the skill. If you already write Python, skim the lessons and do the tasks quickly.

## Variables

A variable is a name for a value. Python figures out the type from the value:

```python
customer = "Meridian Logistics"   # a string (text)
agents = 400                      # an integer
price = 0.40                      # a float (decimal number)
pilot = True                      # a boolean
```

## Strings

Text goes in quotes - single or double, both work. Triple quotes allow several lines:

```python
system = """You are a support assistant.
Answer in at most 50 words."""
```

Useful string operations:

```python
name = "  Meridian Logistics  "
name.strip()          # "Meridian Logistics" - remove surrounding spaces
name.lower()          # "  meridian logistics  "
"MER-1" + "-XZ"       # "MER-1-XZ" - join with +
len("hello")          # 5
"policy" in "return policy"   # True
"a,b,c".split(",")    # ["a", "b", "c"]
```

## f-strings: the one you'll use most

Put `f` before the quotes and anything inside `{}` is replaced by its value. This is how you build prompts:

```python
customer = "Meridian Logistics"
question = "Where is my parcel?"
max_words = 50
prompt = f"You support {customer}. Question: {question} Answer in at most {max_words} words."
print(prompt)
```

You can put expressions inside the braces too: `f"{len(question)} characters"`, `f"{price * 1000:.2f}"` (two decimals).

## Reading command-line arguments

Scripts in this skill take their inputs from the command line: `python prompt.py "Meridian" "Where is my parcel?"`. The arguments arrive as strings in `sys.argv`:

```python
import sys

customer = sys.argv[1]      # sys.argv[0] is the script name
question = sys.argv[2]
```
