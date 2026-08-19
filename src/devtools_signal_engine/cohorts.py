from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ExecutionMode = Literal["github", "enrichment"]


@dataclass(frozen=True, slots=True)
class CohortTarget:
    cohort: str
    organization: str
    github_org: str | None
    execution_mode: ExecutionMode
    rationale: str
    next_action: str

    @property
    def runnable(self) -> bool:
        return self.execution_mode == "github" and self.github_org is not None


GLOBAL_TARGETS: tuple[CohortTarget, ...] = (
    CohortTarget(
        cohort="global",
        organization="Sentry",
        github_org="getsentry",
        execution_mode="github",
        rationale="Developer-first observability company with a broad public repository and SDK surface.",
        next_action="Inspect workflow density, CODEOWNERS coverage, SDK/release complexity, and active engineering surface.",
    ),
    CohortTarget(
        cohort="global",
        organization="Grafana Labs",
        github_org="grafana",
        execution_mode="github",
        rationale="Large observability and infrastructure engineering surface spanning multiple major projects.",
        next_action="Inspect workflow standardization, ownership structure, release surface, and platform-team indicators.",
    ),
    CohortTarget(
        cohort="global",
        organization="HashiCorp",
        github_org="hashicorp",
        execution_mode="github",
        rationale="Infrastructure/devtools benchmark with many providers, shared automation, and governance surfaces.",
        next_action="Inspect CI proliferation, provider scale, reusable automation, and governance complexity.",
    ),
    CohortTarget(
        cohort="global",
        organization="PostHog",
        github_org="PostHog",
        execution_mode="github",
        rationale="Developer-first product company with core product, SDK, integration, and tooling repositories.",
        next_action="Inspect SDK coordination, product-versus-satellite repositories, and ownership/review signals.",
    ),
    CohortTarget(
        cohort="global",
        organization="Cloudflare",
        github_org="cloudflare",
        execution_mode="github",
        rationale="Enterprise-scale developer platform with public SDK, IaC, agents, and platform repositories.",
        next_action="Inspect platform engineering scale, IaC footprint, CI surface, and repo governance maturity.",
    ),
)

QATAR_TARGETS: tuple[CohortTarget, ...] = (
    CohortTarget(
        cohort="qatar",
        organization="Qatar Computing Research Institute (QCRI)",
        github_org="qcri",
        execution_mode="github",
        rationale="Qatar-based technical research organization with a substantial public GitHub footprint.",
        next_action="Run the signal engine directly and inspect research/software governance and workflow signals.",
    ),
    CohortTarget(
        cohort="qatar",
        organization="Qatar Science & Technology Park (QSTP)",
        github_org=None,
        execution_mode="enrichment",
        rationale="Technology ecosystem multiplier; better used to discover portfolio companies than as one GitHub account.",
        next_action="Resolve portfolio companies to verified GitHub organizations, then run those organizations through the engine.",
    ),
    CohortTarget(
        cohort="qatar",
        organization="Qatar Development Bank (QDB)",
        github_org=None,
        execution_mode="enrichment",
        rationale="Startup and digital-transformation ecosystem source rather than a verified public engineering account.",
        next_action="Use QDB programs and portfolio data to build a Qatar account universe, then resolve GitHub identities.",
    ),
    CohortTarget(
        cohort="qatar",
        organization="Ooredoo Qatar",
        github_org=None,
        execution_mode="enrichment",
        rationale="Strategically relevant cloud, AI, cybersecurity, and infrastructure account without a verified org handle in this seed set.",
        next_action="Enrich subsidiaries and engineering entities first; only run verified public GitHub organizations.",
    ),
    CohortTarget(
        cohort="qatar",
        organization="Qatar Financial Centre (QFC)",
        github_org=None,
        execution_mode="enrichment",
        rationale="Digital/FinTech/AI ecosystem node useful for account discovery rather than direct GitHub evidence collection.",
        next_action="Discover Qatar-based technology companies in the ecosystem and resolve their public GitHub organizations.",
    ),
)

COHORTS: dict[str, tuple[CohortTarget, ...]] = {
    "global": GLOBAL_TARGETS,
    "qatar": QATAR_TARGETS,
}


def get_cohort(name: str) -> tuple[CohortTarget, ...]:
    normalized = name.strip().lower()
    try:
        return COHORTS[normalized]
    except KeyError as exc:
        available = ", ".join(sorted(COHORTS))
        raise ValueError(f"unknown cohort {name!r}; available cohorts: {available}") from exc


def runnable_targets(name: str) -> tuple[CohortTarget, ...]:
    return tuple(target for target in get_cohort(name) if target.runnable)


def enrichment_targets(name: str) -> tuple[CohortTarget, ...]:
    return tuple(target for target in get_cohort(name) if not target.runnable)


def format_cohort_catalog() -> str:
    lines: list[str] = []
    for cohort_name in sorted(COHORTS):
        lines.append(f"{cohort_name.upper()}")
        for target in COHORTS[cohort_name]:
            identity = target.github_org if target.github_org is not None else "no verified GitHub org"
            lines.append(
                f"- {target.organization}: {identity} [{target.execution_mode}]\n"
                f"  rationale: {target.rationale}\n"
                f"  next: {target.next_action}"
            )
        lines.append("")
    return "\n".join(lines).rstrip()
