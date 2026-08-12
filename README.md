# devtools-signal-engine

Provenance-first technical account signal engine for developer-tools GTM.

The system turns public engineering-system data into trustworthy, inspectable account intelligence while preserving the distinction between **observed evidence**, **derived signals**, and **unknowns**.

## Current vertical slice

```text
GitHub REST API
  -> complete paginated acquisition
  -> typed RepositoryEvidence
  -> identity + provenance validation
  -> duplicate-safe acquisition snapshot
```

## Why this matters

A GTM signal engine is only useful if downstream scoring can trust the evidence it receives. The current implementation therefore treats completeness and identity as correctness contracts:

- later-page acquisition failure invalidates the run rather than returning partial data;
- HTTP success does not imply payload/schema validity;
- GitHub numeric repository `id` is canonical identity because names can change;
- duplicate stable IDs inside one acquisition snapshot fail explicitly rather than guessing first/last freshness;
- malformed required identity/provenance fields fail at the normalization boundary.

## Candidate-owned engineering kernels

The repository is intentionally built with AI assistance for commodity implementation speed. The engineering claim is not that every line was manually typed. The correctness-critical decisions below are explicitly owned, documented, tested, and defensible:

1. Pagination completeness and termination semantics.
2. Transport success vs payload-contract validity.
3. Stable repository identity using GitHub numeric `id`.
4. Duplicate-identity policy: fail the inconsistent snapshot.
5. Malformed evidence policy: fail required identity/provenance fields explicitly.
6. Next: evidence-backed technical feature definitions and transparent scoring.
7. Next: relational identity/upsert semantics and SQL.

See GitHub issues `PROOF-001`, `ADR-001`, and `DOC-003` for the reasoning ledger.

## Executable proof

Current regression coverage includes:

- optional authorization headers;
- single-page and multi-page acquisition;
- exact-page-boundary pagination;
- later-page server failure -> hard failure, never partial success;
- malformed JSON / unexpected payload handling;
- timeout/network error conversion to domain-level errors;
- repository rename preserves identity;
- duplicate stable ID in one batch fails;
- missing/invalid required identity and metric fields fail.

Run:

```bash
pytest -q
```

## Current data contract

`RepositoryEvidence` preserves stable identity and provenance, including:

- `github_id`
- mutable repository naming attributes
- owner
- source URL
- activity/metadata fields
- source/observation timestamps

## Next employer-facing proof

The immediate roadmap is deliberately tied to developer-tools GTM work:

```text
GitHub repository evidence
  -> GitHub Actions / PR / DevEx-relevant features
  -> Playwright careers / engineering-source evidence
  -> Postgres + SQL
  -> transparent component score
  -> 30-50 real account dataset
  -> OpportunityBundle output
```

Every signal will explicitly distinguish:

```text
OBSERVED
INFERRED
UNKNOWN
```

No model inference will be promoted into raw evidence.

## Proof standard

A correctness-critical kernel is only considered proven when all are true:

1. the decision/rationale is documented;
2. production-valid code enforces it;
3. an adversarial/regression test proves it;
4. the candidate can explain what it does, the boundary, the dangerous failure, and the tradeoff.

The larger portfolio goal is to connect this trustworthy signal layer into a real GTM control plane with CRM, enrichment/orchestration, approved execution, and measurable outcomes.