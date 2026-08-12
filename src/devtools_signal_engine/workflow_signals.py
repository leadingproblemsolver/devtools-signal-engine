from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RepositoryWorkflowSurface:
    workflow_count: int
    uses_github_actions: bool
    codeowners_path: str | None
    observed_evidence: tuple[str, ...]
    unknowns: tuple[str, ...]


def build_workflow_surface(
    workflows: list[dict],
    *,
    codeowners_path: str | None,
) -> RepositoryWorkflowSurface:
    """Convert raw workflow/governance observations into a transparent signal surface.

    These fields are observations about engineering workflow structure. They are not
    treated as buying intent or proof of CI/merge pain.
    """
    workflow_count = len(workflows)
    observed: list[str] = []
    unknowns: list[str] = []

    if workflow_count:
        observed.append(f"github_actions_workflows={workflow_count}")
    else:
        observed.append("github_actions_workflows=0")

    if codeowners_path:
        observed.append(f"codeowners_path={codeowners_path}")
    else:
        unknowns.append("codeowners_not_observed_in_supported_locations")

    return RepositoryWorkflowSurface(
        workflow_count=workflow_count,
        uses_github_actions=workflow_count > 0,
        codeowners_path=codeowners_path,
        observed_evidence=tuple(observed),
        unknowns=tuple(unknowns),
    )
