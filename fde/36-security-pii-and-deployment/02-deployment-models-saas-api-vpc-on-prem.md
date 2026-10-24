---
type: lesson
title: "Deployment models: SaaS API, VPC, on-prem"
minutes: 6
---

Where the model runs decides what the customer's security team will accept. There are three broad options, and many customers mix them.

| Model | How it works | Pros | Cons |
|---|---|---|---|
| **Public SaaS API** | Calls go to the provider's endpoint over the internet | Newest models, no infrastructure, fast start | Data leaves the customer's network; relies on the provider's contract |
| **Private cloud / VPC** | The model runs in the customer's cloud account or a dedicated, region-locked deployment (e.g. via their cloud provider) | Data stays in their cloud tenancy and region; uses existing cloud agreements | Fewer model choices, more setup, sometimes higher cost |
| **On-prem / self-hosted** | Open-weight models on the customer's own GPUs | Full control; works air-gapped | Hardware cost, operations burden, weaker models than the frontier |

## What actually matters to security teams

- **Data retention** - does the provider store prompts and outputs? For how long? Can it be zero?
- **Training use** - is customer data used to train models? Enterprise API terms usually say no; consumer apps may differ.
- **Region** - does processing stay in the EU (or wherever required)?
- **Access** - who at the provider can see data, and under what conditions (abuse monitoring)?
- **Certifications and contract** - SOC 2, ISO 27001, a data processing agreement.

## Design for portability

Customers change their minds after the security review. Keep the model behind one function or gateway (as the lab does), configure the endpoint and model name from the environment, and keep your evals - so moving from a SaaS API to a VPC deployment is a configuration change plus an eval run, not a rewrite.
