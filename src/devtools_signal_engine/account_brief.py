from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any, Iterable

from .models import RepositoryEvidence


def build_account_brief(
    org: str,
    repositories: Iterable[RepositoryEvidence],
    *,
    observed_at: datetime | None = None,
) -> dict[str, Any]:
    """Build a deterministic, provenance-backed organization brief.

    The brief separates observed repository facts from derived signals and
    explicitly records what public GitHub evidence cannot establish.
    """
    repos = list(repositories)
    timestamp = observed_at or (repos[0].observed_at if repos else datetime.now(UTC))
    active_cutoff = timestamp - timedelta(days=30)

    active = [
        repo
        for repo in repos
        if repo.pushed_at is not None and repo.pushed_at >= active_cutoff
    ]
    non_forks = [repo for repo in repos if not repo.fork]
    languages = Counter(repo.language for repo in repos if repo.language)
    top_repositories = sorted(
        repos,
        key=lambda repo: (-repo.stars, repo.full_name),
    )[:5]

    observed_evidence = {
        "repository_count": len(repos),
        "non_fork_repository_count": len(non_forks),
        "archived_repository_count": sum(repo.archived for repo in repos),
        "repositories_pushed_within_30d": len(active),
        "languages_by_repository_count": dict(sorted(languages.items())),
        "top_repositories_by_stars": [
            {
                "github_id": repo.github_id,
                "full_name": repo.full_name,
                "stars": repo.stars,
                "source_locator": repo.source_locator,
            }
            for repo in top_repositories
        ],
    }

    derived_signals: list[dict[str, Any]] = []
    if repos:
        derived_signals.append(
            {
                "signal": "recent_repository_activity_share",
                "value": len(active) / len(repos),
                "evidence_refs": [repo.source_locator for repo in active],
                "interpretation": (
                    "Share of observed public repositories with a push timestamp "
                    "within 30 days of observation."
                ),
                "limitations": (
                    "Public repository activity is not equivalent to company-wide "
                    "engineering activity or buying intent."
                ),
            }
        )

    return {
        "organization": org,
        "observed_at": timestamp.isoformat(),
        "observed_evidence": observed_evidence,
        "derived_signals": derived_signals,
        "unknowns": [
            "private_repository_activity",
            "internal_ci_or_merge_pain",
            "engineering_budget",
            "buyer_intent",
        ],
        "provenance": {
            "source": "GitHub REST API organization repositories",
            "repository_source_locators": [repo.source_locator for repo in repos],
        },
    }
