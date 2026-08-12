# Employer-Visible Proof Map

This file maps conventional engineering/GTM requirements to inspectable implementation evidence in this repository.

| Capability | Evidence | Status |
|---|---|---|
| Python | `src/devtools_signal_engine/` | active |
| REST API consumption | `github.py` | proven |
| HTTP semantics | timeout/status/payload handling in `github.py` | proven |
| Pagination | complete org-repository acquisition | proven |
| Boundary conditions | exact-page termination tests | proven |
| Error handling | domain-level GitHub acquisition errors | proven |
| Data modeling | `RepositoryEvidence` | proven |
| Stable identity | `github_id` contract | proven |
| Provenance | `source_locator`, `observed_at` | proven |
| Deduplication consistency | duplicate-ID rejection | proven |
| Automated testing | `tests/test_github.py`, `tests/test_normalize.py` | proven |
| GitHub/DevTools domain | public engineering-system evidence | active |
| Feature engineering | PR/CI/Actions/CODEOWNERS/activity features | next |
| Browser research | careers/engineering sources via Playwright | next |
| SQL/Postgres | relational persistence + account/evidence queries | next |
| Explainable GTM ranking | component score + evidence refs | next |
| Real account dataset | 30–50 developer-tools/engineering-heavy accounts | next |
| API/output contract | `OpportunityBundle` | next |
| CI | GitHub Actions | next |
| Reproducibility | Docker | next |

## Correctness-critical kernels

The highest-signal implementation decisions are deliberately narrow and inspectable:

1. complete-or-fail pagination;
2. transport vs payload validation;
3. stable `github_id` identity;
4. duplicate-snapshot failure policy;
5. required-field/provenance validation;
6. forthcoming feature definitions and score decomposition;
7. forthcoming relational upsert/SQL identity rules.

These kernels are the points where incorrect logic would materially change downstream business decisions.

## Business proof target

The completed vertical slice should answer:

> Given a real developer-tools company, what public engineering signals are observable, which are merely inferred, how strong is the evidence, and what additional evidence should GTM collect before acting?

The final output should be decision-ready without presenting technical activity as proof of buying intent.
