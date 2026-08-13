from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from statistics import median
from typing import Any
from urllib.parse import quote_plus

from .github import GitHubClient


@dataclass(frozen=True, slots=True)
class AccountSummary:
    organization: str
    observed_at: datetime
    repo_count: int
    active_repos_30d: int
    analyzed_repositories: tuple[str, ...]
    github_actions_workflow_count: int
    repos_using_actions: int
    repos_with_codeowners: int
    merged_prs_30d: int
    median_merge_hours_30d: float | None
    median_merge_sample_size: int
    stale_open_prs_14d: int
    observed: tuple[str, ...]
    inferred: tuple[str, ...]
    unknowns: tuple[str, ...]
    evidence_urls: tuple[str, ...]


def _parse_github_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_account_summary(
    client: GitHubClient,
    org: str,
    *,
    observed_at: datetime | None = None,
    repo_sample_limit: int = 10,
    pr_detail_sample_limit: int = 100,
) -> AccountSummary:
    if not org or not org.strip():
        raise ValueError("org must be a non-empty string")
    if not 1 <= repo_sample_limit <= 50:
        raise ValueError("repo_sample_limit must be between 1 and 50")
    if not 1 <= pr_detail_sample_limit <= 100:
        raise ValueError("pr_detail_sample_limit must be between 1 and 100")

    organization = org.strip()
    observed_at = observed_at or datetime.now(timezone.utc)
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=timezone.utc)
    observed_at = observed_at.astimezone(timezone.utc)

    repos = client.list_org_repositories(organization)
    cutoff_30d = observed_at - timedelta(days=30)
    cutoff_14d = observed_at - timedelta(days=14)

    active_repos = []
    for repo in repos:
        pushed_at = _parse_github_datetime(repo.get("pushed_at"))
        if (
            pushed_at is not None
            and cutoff_30d <= pushed_at <= observed_at
            and not bool(repo.get("archived", False))
        ):
            active_repos.append(repo)

    active_repos.sort(
        key=lambda repo: _parse_github_datetime(repo.get("pushed_at"))
        or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    sampled_repos = active_repos[:repo_sample_limit]

    workflow_count = 0
    repos_using_actions = 0
    repos_with_codeowners = 0
    analyzed_names: list[str] = []
    evidence_urls: list[str] = [f"https://github.com/orgs/{organization}/repositories"]

    for repo in sampled_repos:
        repo_name = repo.get("name")
        if not isinstance(repo_name, str) or not repo_name:
            continue
        analyzed_names.append(repo_name)

        workflows = client.list_repository_workflows(organization, repo_name)
        repo_workflow_count = len(workflows)
        workflow_count += repo_workflow_count
        if repo_workflow_count > 0:
            repos_using_actions += 1

        codeowners_path = client.find_codeowners_path(organization, repo_name)
        if codeowners_path is not None:
            repos_with_codeowners += 1

        html_url = repo.get("html_url")
        if isinstance(html_url, str) and html_url:
            evidence_urls.append(html_url)

    cutoff_30d_date = cutoff_30d.date().isoformat()
    cutoff_14d_date = cutoff_14d.date().isoformat()

    merged_query = f"org:{organization} is:pr is:merged merged:>={cutoff_30d_date}"
    stale_query = f"org:{organization} is:pr is:open created:<={cutoff_14d_date}"

    merged_total, merged_items = client.search_pull_requests(
        merged_query,
        max_items=pr_detail_sample_limit,
    )
    stale_total, _ = client.search_pull_requests(stale_query, max_items=1)

    merge_durations_hours: list[float] = []
    sampled_detail_urls: list[str] = []
    for item in merged_items:
        pull_request = item.get("pull_request")
        if not isinstance(pull_request, dict):
            continue
        api_url = pull_request.get("url")
        if not isinstance(api_url, str) or not api_url:
            continue

        detail = client.fetch_pull_request_detail(api_url)
        created_at = _parse_github_datetime(detail.get("created_at"))
        merged_at = _parse_github_datetime(detail.get("merged_at"))
        if (
            created_at is None
            or merged_at is None
            or not (cutoff_30d <= merged_at <= observed_at)
            or merged_at < created_at
        ):
            continue

        merge_durations_hours.append((merged_at - created_at).total_seconds() / 3600)

        html_url = detail.get("html_url")
        if isinstance(html_url, str) and html_url and len(sampled_detail_urls) < 5:
            sampled_detail_urls.append(html_url)

    median_merge_hours = (
        float(median(merge_durations_hours)) if merge_durations_hours else None
    )

    evidence_urls.extend(sampled_detail_urls)
    evidence_urls.extend(
        [
            "https://github.com/search?q=" + quote_plus(merged_query) + "&type=pullrequests",
            "https://github.com/search?q=" + quote_plus(stale_query) + "&type=pullrequests",
        ]
    )

    observed = [
        f"public_repositories={len(repos)}",
        f"active_public_repositories_30d={len(active_repos)}",
        f"merged_public_prs_30d={merged_total}",
        f"stale_open_public_prs_14d={stale_total}",
        f"github_actions_workflows={workflow_count} across_sampled_active_repos={len(analyzed_names)}",
        f"repos_using_actions={repos_using_actions} of_sampled_active_repos={len(analyzed_names)}",
        f"repos_with_codeowners={repos_with_codeowners} of_sampled_active_repos={len(analyzed_names)}",
    ]

    if median_merge_hours is None:
        observed.append("median_merge_hours_30d=UNKNOWN")
    else:
        observed.append(
            f"median_merge_hours_30d={median_merge_hours:.2f} sample_size={len(merge_durations_hours)} of_merged_prs_30d={merged_total}"
        )

    inferred: list[str] = []
    if active_repos:
        inferred.append(
            "Public engineering activity is recent enough to support deeper account research."
        )
    if workflow_count:
        inferred.append(
            "GitHub-native workflow automation is present in the sampled active repositories; this supports deeper workflow investigation but does not prove pain or buying intent."
        )
    if repos_with_codeowners:
        inferred.append(
            "Formal path-ownership rules are visible in the sampled active repositories; this is governance evidence, not evidence of purchasing intent."
        )

    unknowns = [
        "private_repository_activity",
        "private_CI_or_workflow_configuration",
        "actual_CI_spend",
        "whether_merge_or_CI_workflows_create_material_pain",
        "buying_intent",
    ]
    if len(active_repos) > len(analyzed_names):
        unknowns.append(
            f"workflow_and_CODEOWNERS_surface_for_{len(active_repos)-len(analyzed_names)}_unsampled_active_repositories"
        )
    if merged_total > len(merge_durations_hours):
        unknowns.append(
            "exact_org_wide_median_merge_duration_because_merge_duration_is_bounded_to_a_PR_detail_sample"
        )

    return AccountSummary(
        organization=organization,
        observed_at=observed_at,
        repo_count=len(repos),
        active_repos_30d=len(active_repos),
        analyzed_repositories=tuple(analyzed_names),
        github_actions_workflow_count=workflow_count,
        repos_using_actions=repos_using_actions,
        repos_with_codeowners=repos_with_codeowners,
        merged_prs_30d=merged_total,
        median_merge_hours_30d=median_merge_hours,
        median_merge_sample_size=len(merge_durations_hours),
        stale_open_prs_14d=stale_total,
        observed=tuple(observed),
        inferred=tuple(inferred),
        unknowns=tuple(unknowns),
        evidence_urls=tuple(dict.fromkeys(evidence_urls)),
    )


def format_account_summary(summary: AccountSummary) -> str:
    median_text = (
        "UNKNOWN"
        if summary.median_merge_hours_30d is None
        else f"{summary.median_merge_hours_30d:.2f}h (sample {summary.median_merge_sample_size}/{summary.merged_prs_30d})"
    )

    lines = [
        f"company: {summary.organization}",
        f"observed_at: {summary.observed_at.isoformat()}",
        "",
        "engineering_activity:",
        f"- repo_count: {summary.repo_count}",
        f"- active_repos_30d: {summary.active_repos_30d}",
        f"- merged_prs_30d: {summary.merged_prs_30d}",
        f"- median_merge_hours_30d: {median_text}",
        f"- stale_open_prs_14d: {summary.stale_open_prs_14d}",
        "",
        "workflow_surface:",
        f"- github_actions_workflow_count: {summary.github_actions_workflow_count} (sampled {len(summary.analyzed_repositories)} active repos)",
        f"- repos_using_actions: {summary.repos_using_actions} (sampled {len(summary.analyzed_repositories)} active repos)",
        f"- repos_with_CODEOWNERS: {summary.repos_with_codeowners} (sampled {len(summary.analyzed_repositories)} active repos)",
        "",
        "OBSERVED:",
        *[f"- {item}" for item in summary.observed],
        "",
        "INFERRED:",
        *([f"- {item}" for item in summary.inferred] or ["- none"]),
        "",
        "UNKNOWN:",
        *[f"- {item}" for item in summary.unknowns],
        "",
        "EVIDENCE:",
        *[f"- {url}" for url in summary.evidence_urls],
    ]
    return "\n".join(lines)
