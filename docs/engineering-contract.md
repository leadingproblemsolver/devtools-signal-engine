# Engineering Contract

This document defines the correctness-critical behaviors that the implementation must preserve as the signal engine grows.

## 1. Acquisition completeness

**Contract:** a repository acquisition run is either complete for the requested pagination strategy or it fails explicitly.

A later-page transport/server failure must never return an earlier successful prefix as if it were complete evidence.

**Reason:** downstream features and rankings are only as trustworthy as the evidence set they summarize. Silent truncation is worse than explicit failure because it can produce confident but wrong prioritization.

## 2. Transport success is not schema success

**Contract:** HTTP success and payload validity are separate boundaries.

A `200` response is accepted only after its body satisfies the expected data contract. For repository-list acquisition, the top-level payload must be a list.

## 3. Stable repository identity

**Contract:** GitHub numeric repository `id` is canonical logical identity.

Repository `name` and `full_name` are attributes, not keys, because a repository may be renamed without becoming a different logical repository.

## 4. Duplicate identity policy

**Contract:** two records with the same stable GitHub ID inside one acquisition snapshot invalidate the snapshot.

The engine does not guess that the first or last record is authoritative.

**Reason:** a duplicate stable identity inside one run indicates an upstream/acquisition consistency problem. Guessing creates untraceable data mutation.

## 5. Boundary validation

**Contract:** required identity/provenance fields fail fast when missing or malformed.

The normalizer validates stable identity, names, source locator, owner, required timestamps, and non-negative numeric metrics before constructing trusted internal evidence.

## 6. Provenance preservation

**Contract:** normalized evidence retains enough source metadata to trace any downstream feature back to its public origin and observation time.

At minimum this includes source locator, stable source ID, and `observed_at`.

## 7. Observation vs inference

Every downstream signal must belong to one of three classes:

- **OBSERVED** — directly supported by acquired source data.
- **INFERRED** — deterministic or probabilistic interpretation of observations.
- **UNKNOWN** — information not supported by the current evidence set.

An inferred claim may never overwrite or masquerade as an observation.

## 8. Explainable scoring

Account scores must decompose into named components that point back to features/evidence. No opaque lead score is permitted in the deterministic core.

The score represents prioritization evidence, not proof of buyer pain or purchase intent.

## 9. External-write safety (control-plane handoff)

When this engine later hands opportunities to a CRM/control plane, external mutation must remain downstream of explicit approval and idempotency controls. Evidence discovery itself does not authorize outbound action.

## 10. Proof requirement

A correctness-critical decision is considered implemented only when:

1. production code enforces it;
2. a focused regression/adversarial test proves it;
3. the decision and dangerous failure are documented;
4. the implementation can be traced to observable runtime behavior.
