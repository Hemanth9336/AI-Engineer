---
type: lesson
title: "Documentation generated from source"
minutes: 19
---

Generated docs fail in a specific way: they read well and describe a function that doesn't exist, a parameter with the wrong name, or an example that never ran. The fix is the same as for onboarding documents: make every claim checkable, then check it.

## Three kinds of claims, three checks

| Claim in the README | How to verify |
|---|---|
| A signature, in a heading such as `` ### `top_words(text, n=3)` `` | Parse the module with `ast` and compare names, parameters, and defaults |
| Coverage: every public function is documented | Compare the set of headings with the module's public functions |
| An example: `>>> top_words("a b a", n=1)` | Run it: `python3 -m doctest README.md` executes every `>>>` line in a text file |

`doctest` treats any `>>>` line in a Markdown file as a test and compares the next lines with the real output. An example that doesn't run, or prints something else, fails.

## A fixed format makes it parseable

Pick a format and put it in the prompt:

```markdown
## API

### `word_count(text)`

Number of words in `text`.

    >>> from textstats import word_count
    >>> word_count("one two  three")
    3
```

Then a verification script can find every `` ### `name(params)` `` heading, and doctest can run every example.

Note the **indented** example, not a fenced one. doctest reads the expected output up to the next blank line, so the closing ```` ``` ```` of a fenced block is taken as part of the output, and the example fails. Indent examples by four spaces (Markdown still renders them as code), or put a blank line before the closing fence.

## Close the loop

Write the verifier **first**, then let Claude run it as part of the job: "write README.md, then run `python3 verify_readme.py` and fix anything it reports". The agent iterates against a real check instead of its own confidence. Keep the verifier in CI so the README fails the build when the code changes under it.

## Commands this node introduces

`ast` signature comparison, `python3 -m doctest README.md`, and verifier-first generation.
