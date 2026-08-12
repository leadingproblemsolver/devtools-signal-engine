# devtools-signal-engine

Evidence-backed technical account intelligence for developer-tools GTM.

The engine converts public engineering-system data into inspectable account signals while keeping **observed evidence**, **derived features**, and **unknowns** explicitly separate.

## Current pipeline

```text
GitHub REST API
  -> complete paginated acquisition
  -> typed RepositoryEvidence
  -> identity + provenance validation
  -> duplicate-safe acquisition snapshot
  -> technical feature extraction
  -> transparent account scoring
  -> OpportunityBundle
```

## Correctness contracts

The system treats evidence integrity as a product requirement:

- acquisition is complete or fails explicitly; later-page failures never return partial success;
- HTTP success does not imply payload-contract validity;
- GitHub numeric repository `id` is canonical identity because mutable names can change;
- duplicate stable IDs inside one acquisition snapshot fail rather than guessing which record is authoritative;
- malformed required identity or provenance fields fail at the normalization boundary;
- raw observations are never promoted into stronger claims without an explicit derived-feature layer.

## Executable proof

Regression coverage currently includes:

- optional GitHub authorization;
- single-page and multi-page acquisition;
- exact-page-boundary pagination;
- later-page server failure -> hard failure;
- malformed JSON and unexpected payload handling;
- timeout/network error conversion to domain-level errors;
- repository rename preserving logical identity;
- duplicate stable ID in one batch -> hard failure;
- malformed required identity, timestamp, and numeric fields -> hard failure.

Run:

```bash
pytest -q
```

## Data contract

`RepositoryEvidence` preserves the minimum fields required for downstream technical analysis:

- stable GitHub repository ID;
- mutable repository naming attributes;
- owner and source locator;
- language/activity metadata;
- created/updated/pushed timestamps;
- observation timestamp.

## Engineering decisions

The implementation is intentionally explicit about the few decisions that determine trustworthiness: completeness, identity, schema validity, duplicate policy, provenance, and later score explainability.

See:

- [`docs/engineering-contract.md`](docs/engineering-contract.md)
- [`docs/decision-log.md`](docs/decision-log.md)
- [`docs/proof-map.md`](docs/proof-map.md)

## Next vertical slice

The immediate build path is tied directly to developer-tools GTM research:

```text
repository evidence
  -> PR / CI / GitHub Actions / CODEOWNERS / activity features
  -> careers + engineering-source evidence
  -> Postgres + SQL
  -> transparent component score
  -> 30-50 real accounts
  -> OpportunityBundle output
```

Every downstream signal is classified as:

```text
OBSERVED
INFERRED
UNKNOWN
```

No probabilistic inference is treated as raw evidence.
