# devtools-signal-engine

Evidence-backed technical account intelligence for developer-tools GTM.

The engine takes a real GitHub organization and converts public engineering-system evidence into an inspectable account brief while keeping **observed evidence**, **derived metrics**, **bounded inference**, and **unknowns** explicitly separate.

## Proof surface

- [`docs/index.html`](docs/index.html) — static flagship proof surface using checked-in Vercel/Next.js evidence
- [`docs/sqlite-utils-841.html`](docs/sqlite-utils-841.html) — external-repository bug reproduction + source localization receipt

The `docs/` directory is intentionally zero-dependency and GitHub-Pages-ready. The static page labels precomputed evidence explicitly instead of pretending to make a live browser-side GitHub API call.

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

## Run benchmark cohorts

The repository includes a reproducible seed set for the next proof step: five developer-tool organizations with verified public GitHub handles plus a separate Qatar market cohort.

```bash
# Inspect the complete 10-account seed set without API calls.
python -m devtools_signal_engine --list-cohorts

# Run the five GitHub-observable global benchmark organizations.
export GITHUB_TOKEN=...
python -m devtools_signal_engine --cohort global

# Run QCRI and print the other Qatar organizations as enrichment-only targets.
python -m devtools_signal_engine --cohort qatar
```

The Qatar cohort deliberately does **not** invent GitHub handles for ecosystem-relevant organizations whose public engineering identity has not been verified. See [`docs/account-cohorts.md`](docs/account-cohorts.md) and [`examples/account_cohorts.csv`](examples/account_cohorts.csv).

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
- account-summary scope and archived-repository activity boundaries;
- cohort separation between GitHub-observable and enrichment-only targets.

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
- [`docs/account-cohorts.md`](docs/account-cohorts.md)

## Next proof step

Run the checked-in global and Qatar cohorts, inspect weak/incorrect signals, then persist observed outputs into a 10-30 account dataset before introducing calibrated ranking weights.
