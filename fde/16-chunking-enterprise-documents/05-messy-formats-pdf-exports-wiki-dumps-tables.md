---
type: lesson
title: "Messy formats: PDF exports, wiki dumps, tables"
minutes: 5
---

The documents in demos are clean Markdown. The documents at customers are not. Expect to spend real time on cleaning - it decides answer quality more than any prompt.

## What you'll find

| Source | Typical mess |
|---|---|
| **PDF exports** | Headers and footers on every page ("Page 3 of 40", "CONFIDENTIAL"), words split by hyphenation, two-column layouts read across, scanned pages with no text at all |
| **Wiki / intranet dumps** | HTML tags, navigation breadcrumbs ("Home > Policies > ..."), "Last edited by" lines, empty template pages, duplicate pages |
| **Word documents** | Tracked changes, comments, numbered lists that lose their numbers |
| **Spreadsheets and tables** | Flattened into a stream of cells with no headers |
| **Email threads** | Quoted replies repeated 10 times, signatures, legal disclaimers |
| **Everything** | Windows line endings, odd encodings, `&nbsp;` and `&amp;`, runs of spaces |

## Cleaning rules that pay off

1. **Remove boilerplate** - breadcrumbs, footers, signatures, disclaimers. Repeated text makes every chunk look alike.
2. **Drop empty and template pages** - "TODO: fill in this page" shouldn't be retrievable.
3. **Strip markup but keep structure** - remove tags, keep headings and list items as lines.
4. **Decode entities and normalise whitespace** - `&nbsp;` to a space, collapse runs of spaces, unify line endings.
5. **Keep tables readable** - turn each row into a sentence-like line with its column names: `Standard pallet: max weight 800 kg, max height 1.8 m`.
6. **Flag what you can't read** - scanned PDFs need OCR; report how many pages had no text rather than silently skipping them.

## Write cleaning as rules you can show

Customers will ask why a document isn't being found. Cleaning code with explicit, named rules ("drop lines starting with `Home >`") is easy to explain and adjust. Run it on the full export, then **count** what happened: pages kept, pages dropped and why, characters removed. Those numbers often reveal problems - "40% of pages were empty templates" is a finding worth telling the customer.
