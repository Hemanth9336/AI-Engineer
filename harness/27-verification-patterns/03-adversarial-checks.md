---
type: lesson
title: "Adversarial checks"
minutes: 6
---

A verifier that agrees with everything is worse than none: it adds cost and false confidence. Good checks are **adversarial** - they try to prove the answer wrong.

## Make the checker try to break it

| Weak check | Adversarial check |
|---|---|
| "Is this answer good?" | "Find a claim in this answer that the evidence doesn't support" |
| Rereads the answer | Recomputes the facts from the source |
| Sees the generator's reasoning | Sees only the claim and the raw evidence |
| Same model, same prompt | A different prompt, often a different model |
| Pass by default | Fail by default; pass only with evidence |

## Code beats model, where it can

If a claim can be recomputed, recompute it. An incident summary that says "312 requests failed starting at 09:11:00" can be checked against the log exactly:

```python
def recompute(log_text):
    errors = [l for l in log_text.splitlines() if " ERROR " in l]
    return {"error_count": len(errors), "first_error": errors[0][11:19], ...}

mismatches = {k: {"claimed": summary[k], "actual": v} for k, v in recompute(log).items() if summary.get(k) != v}
```

No prompt, no cost, no judgment calls - and it can't be talked out of a mismatch. Use model verifiers for what code can't check (tone, completeness, whether the reasoning follows), and code for every number, name, date and file that has a source.

## Test the checker with planted errors

How do you know your checker catches anything? **Plant** an error you know about and see if it's caught. This is mutation testing for verifiers:

1. Take a correct output. Change one field: a count, a time, a version.
2. Run the checker. It must fail, and name the field.
3. Do it for **every** field. A checker that misses one kind of mutation has a blind spot.
4. Also run it on the correct output. It must pass - a checker that fails everything is useless too.

Keep those planted cases as tests. When someone "simplifies" the checker later, the tests catch the hole.
