---
type: lesson
title: "Why first prompts fail"
minutes: 7
---

Your first prompt for a new task will often disappoint. That is normal - even for experienced prompt writers. The skill is not writing a perfect prompt first time; it is knowing why it missed and fixing it quickly.

## The usual reasons

1. **Missing context.** The model did not know something you know: the system name, the audience, what "the usual format" means here.
2. **Ambiguous task.** "Summarize" - in one line or one page? "Check" - for bugs, style, or security?
3. **No format.** You wanted one line for a script; it wrote three friendly paragraphs.
4. **Conflicting instructions.** "Be thorough" and "keep it short" in the same prompt; the model picks one.
5. **Instructions buried in data.** The real question sits after 200 lines of pasted log, easy to lose.
6. **Unclear edge cases.** What should it do when the information is missing? If you don't say, it invents something.

Nearly every bad answer comes from one of these. None of them is fixed by a bigger model or by asking in capital letters.

## It is not the model's fault (mostly)

When an answer is wrong, the instinct is to blame the model. Usually the prompt was underspecified, and the model filled the gap with the most average guess. Ask: **could a sharp new colleague have done better with exactly this prompt and nothing else?** If not, the prompt is the problem.

## Sometimes it is the model

There are real model limits: exact counting, very long chains of arithmetic, facts it never learned, events after its cutoff. Those are signs to change the approach - give it the data, use code for maths, try a stronger or reasoning model - rather than to keep rewording.

## Expect to iterate

Treat a prompt like code: write it, run it on real inputs, look at the output, change one thing, run again. Two or three rounds is typical for a prompt that a script will rely on. Next: reading a weak answer to find out which of the six problems you have.
