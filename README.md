# devtools-signal-engine

Evidence-backed technical account intelligence for developer-tools GTM.

The engine takes a real GitHub organization and converts public engineering-system evidence into an inspectable account brief while keeping **observed evidence**, **derived metrics**, **bounded inference**, and **unknowns** explicitly separate.

## Run one real account

```bash
export GITHUB_TOKEN=...
python -m devtools_signal_engine vercel
```

The command reports:

- public repository count;
- active public repositories in the last 30 days;
- merged public PRs in the last 30 days;
- sampled median PR merge duration;
- stale open public PRs older than 14 days;
- GitHub Actions workflow surface across a bounded sample of recent active repos;
- CODEOWNERS presence across the same sample;
- observed facts, cautious implications, unknowns, and evidence URLs.

Where exhaustive acquisition would create hundreds of API calls, the output states its sample scope instead of presenting a sampled result as org-wide fact.

## Current pipeline

```text
GitHub REST API
  -> complete paginated repository acquisition
  -> recent-activity filtering
  -> org-wide PR count queries
  -> bounded PR-detail / workflow / CODEOWNERS acquisition
  -> deterministic metrics
  -> OBSERVED / INFERRED / UNKNOWN account brief
  -> evidence URLs
```

## Correctness contracts

The system treats evidence integrity as a product requirement:

- repository acquisition is complete or fails explicitly; later-page failures never return partial success;
- HTTP success does not imply payload-contract validity;
- GitHub numeric repository `id` is canonical identity because mutable names can change;
- duplicate stable IDs inside one acquisition snapshot fail rather than guessing which record is authoritative;
- recent repository activity uses `pushed_at`, not generic metadata modification time;
- PR recency, staleness, and duration use explicit timestamp semantics;
- sampled metrics disclose their scope;
- missing evidence remains unknown rather than being guessed;
- GitHub workflow/governance evidence is not treated as proof of pain or buying intent.

## Executable proof

```bash
pip install -e ".[dev]"
pytest -q
```

CI runs the same suite on pushes and pull requests.

Regression coverage includes:

- optional GitHub authorization;
- single-page and multi-page acquisition;
- exact-page-boundary pagination;
- later-page server failure -> hard failure;
- malformed JSON and unexpected payload handling;
- timeout/network error conversion to domain-level errors;
- repository rename preserving logical identity;
- duplicate stable ID in one batch -> hard failure;
- malformed required identity, timestamp, and numeric fields -> hard failure;
- PR time-window calculations;
- workflow/CODEOWNERS observation boundaries;
- account-summary scope and archived-repository activity boundaries.

## Output discipline

Every account brief separates:

```text
OBSERVED
- facts directly returned or deterministically computed from public evidence

INFERRED
- cautious implications supported by those facts

UNKNOWN
- facts the public evidence cannot establish
```

This prevents claims such as "high CI spend", "merge pain", or "buying intent" from appearing merely because a company has many workflows or PRs.

## Engineering decisions

See:

- [`docs/engineering-contract.md`](docs/engineering-contract.md)
- [`docs/decision-log.md`](docs/decision-log.md)
- [`docs/proof-map.md`](docs/proof-map.md)

## Next proof step

Run the command across 3-5 real developer-tool organizations, inspect weak/incorrect signals, then persist a 10-30 account dataset before introducing calibrated ranking weights.
