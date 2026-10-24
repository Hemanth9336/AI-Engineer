---
type: lesson
title: "Functions, files, and running scripts"
minutes: 5
---

## Functions

A function packages a few lines under a name, so you can reuse and test them:

```python
def word_count(text):
    return len(text.split())

word_count("Your parcel is in Leeds")   # 5
```

Arguments can have defaults, and a function can return several values:

```python
def summarize(path, top=3):
    ...
    return total, high
```

## Reading and writing files

```python
text = open("policy.txt").read()                    # the whole file as one string
lines = open("tickets.txt").read().splitlines()     # a list of lines, without newline characters

with open("out.txt", "w") as f:                     # "w" overwrites, "a" appends
    f.write("one line\n")
```

`with` closes the file for you. For paths, `pathlib` is handy:

```python
from pathlib import Path

p = Path("tickets.txt")
p.exists()
p.read_text()
p.write_text("hello\n")
```

Watch for the classic export problems: blank lines, trailing spaces, and Windows line endings. `line.strip()` and skipping empty lines fixes most of them.

## Running a script vs importing it

```python
def summarize(path):
    ...

if __name__ == "__main__":
    import sys
    print(summarize(sys.argv[1]))
```

The `if __name__ == "__main__":` block runs only when you execute the file (`python summary.py tickets.txt`). When another script or a test does `from summary import summarize`, only the function is loaded. Every script you hand over to a customer should be shaped like this - it makes your code testable.

## Running Python

```bash
python summary.py tickets.txt     # run a script with arguments
python -c "print(2 + 2)"          # one line
python                            # interactive - exit() to leave
```

In your lab, `python` is the virtual environment at `/root/ai-lab/.venv`, which already has the `openai` package installed.
