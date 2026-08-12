# Technical Decision Log

This log captures decisions that materially affect data trust, GTM relevance, or production behavior.

## D001 — Pagination completeness over partial availability

**Decision:** if any required page fails, fail the acquisition run.

**Rejected alternative:** return successfully acquired earlier pages.

**Why:** a partial repository set can silently distort activity, complexity, and prioritization features.

## D002 — Validate payload shape after HTTP success

**Decision:** treat HTTP status validation and data-contract validation as separate checks.

**Why:** a successful transport response does not guarantee the body has the structure required by downstream logic.

## D003 — GitHub numeric ID is repository identity

**Decision:** `github_id` is the canonical key.

**Rejected alternatives:** `name`, `full_name`.

**Why:** names can change while the logical GitHub repository remains the same.

## D004 — Duplicate stable ID invalidates one snapshot

**Decision:** fail normalization if the same `github_id` appears twice in one acquisition run.

**Rejected alternatives:** keep-first and keep-last.

**Why:** either alternative makes an unsupported freshness/authority assumption. A duplicated canonical identity is treated as an upstream consistency defect that should be investigated.

## D005 — Required evidence fails fast

**Decision:** reject malformed stable identity, source, timestamps, or non-negative metrics rather than silently defaulting them.

**Why:** downstream feature computation should operate on known-valid evidence.

## D006 — Optional descriptive fields may remain unknown

**Decision:** fields such as language/default branch may be `None` when the source does not provide a valid string.

**Why:** absence of optional descriptive data should not invalidate otherwise trustworthy repository identity/provenance.

## D007 — Separate observed, inferred, and unknown

**Decision:** future GTM signals must preserve their epistemic class.

**Why:** repository activity or CI configuration can indicate technical conditions, but cannot by itself prove pain, budget, urgency, or intent.

## D008 — Transparent deterministic scoring before probabilistic inference

**Decision:** initial account prioritization is composed from explicit named feature components. LLM-generated interpretation, if added later, sits above the evidence layer.

**Why:** employers/operators must be able to reconstruct why an account ranked highly and distinguish source facts from model interpretation.

## D009 — Add infrastructure only when a real failure mode requires it

**Decision:** do not add concurrency locks, circuit breakers, distributed queues, caches, or similar primitives merely as portfolio decoration.

**Why:** engineering quality is demonstrated by selecting the smallest mechanism that correctly handles the observed workload and failure model.

## D010 — External effects require separate control-plane guarantees

**Decision:** discovery/ranking never directly authorizes CRM or sequencer writes. External actions must later pass approval, idempotency, retry, and reconciliation boundaries.

**Why:** evidence collection and consequential execution have different risk contracts.
