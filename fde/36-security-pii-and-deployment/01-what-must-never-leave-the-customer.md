---
type: lesson
title: "What must never leave the customer"
minutes: 6
---

Every enterprise customer will ask: "Where does our data go?" Before you build anything, you need a clear answer - and a list of what must never leave their environment.

## Kinds of sensitive data

| Category | Examples | Typical rule |
|---|---|---|
| **Personal data (PII)** | Names, emails, phone numbers, addresses, IBANs, card numbers, national ids | Minimise; redact before external calls; strict retention |
| **Special categories** | Health, religion, union membership, biometrics | Often forbidden from external processing entirely |
| **Credentials and secrets** | API keys, passwords, tokens | Never in prompts, logs or repos |
| **Confidential business data** | Margins, contracts, M&A, unreleased results | Only to approved processors, often only in-region |
| **Regulated data** | Payment card data (PCI), banking secrecy, medical records | Governed by specific regulations and audits |

## Questions to ask in discovery

- Which data classes will the assistant touch - questions, documents, tool results?
- Which jurisdictions apply (GDPR in the EU, sector rules for banks and health)?
- Is an external model API allowed at all? With which providers and regions?
- What may be logged, for how long, and who can read it?
- Who approves: security, privacy (DPO), legal, works council?

## Data minimisation

The safest data is data you never send. Before a ticket goes to a model, ask what the model needs to do its job. To summarise "box arrived crushed, customer wants refund", it doesn't need the customer's email, phone or IBAN. **Redact first, send second.**

## Get it in writing

Write down the data flows - what goes where, under which agreement - and get the customer's security team to sign off before the pilot. It's slower for a week and saves the project later.
