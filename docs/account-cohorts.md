# Benchmark account cohorts

This repository includes a small, explicit seed set for the next proof step: run the signal engine across several technically relevant organizations, compare signal quality, and preserve the distinction between public evidence and account enrichment.

The cohort data lives in `src/devtools_signal_engine/cohorts.py` and is mirrored in `examples/account_cohorts.csv` for spreadsheet/CRM workflows.

## Global benchmark

These five organizations have verified public GitHub organization handles and are intended to run directly through the engine.

| Organization | GitHub org | Why it belongs | Investigation focus |
|---|---|---|---|
| Sentry | `getsentry` | Developer-first observability company with a broad repository and SDK surface. | Workflow density, CODEOWNERS, SDK/release complexity, active engineering surface. |
| Grafana Labs | `grafana` | Large observability/infrastructure engineering surface across multiple major projects. | Workflow standardization, ownership, releases, platform-team indicators. |
| HashiCorp | `hashicorp` | Infrastructure/devtools benchmark with providers, shared automation, and governance surfaces. | CI proliferation, provider scale, reusable automation, governance complexity. |
| PostHog | `PostHog` | Developer-first product company with product, SDK, integration, and tooling repositories. | SDK coordination, product-versus-satellite repositories, ownership/review signals. |
| Cloudflare | `cloudflare` | Enterprise-scale developer platform with SDK, IaC, agents, and platform repositories. | Platform engineering scale, IaC footprint, CI surface, governance maturity. |

Run the full global cohort:

```bash
export GITHUB_TOKEN=...
python -m devtools_signal_engine --cohort global
```

## Qatar market cohort

Qatar is intentionally modeled differently. A strategically relevant organization is not automatically a valid GitHub evidence target.

| Organization | Execution mode | GitHub org | Why |
|---|---|---|---|
| Qatar Computing Research Institute (QCRI) | GitHub | `qcri` | Qatar-based technical research organization with a substantial public GitHub footprint. |
| Qatar Science & Technology Park (QSTP) | Enrichment | — | Better used to discover portfolio companies and resolve their GitHub identities. |
| Qatar Development Bank (QDB) | Enrichment | — | Ecosystem/startup source rather than a verified public engineering account in this seed set. |
| Ooredoo Qatar | Enrichment | — | Strategic cloud/AI/cyber/infrastructure account; engineering entities should be resolved before GitHub claims are made. |
| Qatar Financial Centre (QFC) | Enrichment | — | Useful digital/FinTech/AI ecosystem node for downstream account discovery. |

Run the GitHub-observable Qatar target and print the enrichment-only targets separately:

```bash
export GITHUB_TOKEN=...
python -m devtools_signal_engine --cohort qatar
```

The command will run `qcri`. It will **not** invent handles for QSTP, QDB, Ooredoo, or QFC; those organizations are printed as enrichment-only next actions.

## Inspect without API calls

```bash
python -m devtools_signal_engine --list-cohorts
```

This prints the complete 10-account seed set, execution mode, rationale, and next action without calling GitHub.

## Evidence discipline

The cohort feature does not change the engine's evidence contract. A target being present in a benchmark or market cohort is not evidence of engineering pain, budget, buying intent, or a current initiative. GitHub-observable targets can produce `OBSERVED / INFERRED / UNKNOWN` briefs. Enrichment-only targets stay explicitly outside that evidence path until a public GitHub identity is verified.
