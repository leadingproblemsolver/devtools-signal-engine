from datetime import UTC, datetime, timedelta

from devtools_signal_engine.account_brief import build_account_brief
from devtools_signal_engine.models import RepositoryEvidence


def _repo(*, github_id: int, name: str, stars: int, pushed_days_ago: int | None, language: str = "Python") -> RepositoryEvidence:
    observed_at = datetime(2026, 8, 12, tzinfo=UTC)
    pushed_at = None if pushed_days_ago is None else observed_at - timedelta(days=pushed_days_ago)
    return RepositoryEvidence(
        github_id=github_id,
        name=name,
        full_name=f"acme/{name}",
        owner_login="acme",
        html_url=f"https://github.com/acme/{name}",
        default_branch="main",
        language=language,
        fork=False,
        archived=False,
        stars=stars,
        forks=0,
        open_issues=0,
        created_at=datetime(2025, 1, 1, tzinfo=UTC),
        updated_at=observed_at,
        pushed_at=pushed_at,
        source_locator=f"https://github.com/acme/{name}",
        observed_at=observed_at,
    )


def test_account_brief_separates_observed_derived_and_unknown() -> None:
    observed_at = datetime(2026, 8, 12, tzinfo=UTC)
    repos = [
        _repo(github_id=1, name="active", stars=10, pushed_days_ago=2),
        _repo(github_id=2, name="stale", stars=20, pushed_days_ago=60, language="TypeScript"),
    ]

    brief = build_account_brief("acme", repos, observed_at=observed_at)

    assert brief["observed_evidence"]["repository_count"] == 2
    assert brief["observed_evidence"]["repositories_pushed_within_30d"] == 1
    assert brief["derived_signals"][0]["signal"] == "recent_repository_activity_share"
    assert brief["derived_signals"][0]["value"] == 0.5
    assert brief["derived_signals"][0]["evidence_refs"] == ["https://github.com/acme/active"]
    assert "buyer_intent" in brief["unknowns"]


def test_top_repositories_are_deterministic_and_provenanced() -> None:
    observed_at = datetime(2026, 8, 12, tzinfo=UTC)
    repos = [
        _repo(github_id=1, name="b", stars=100, pushed_days_ago=1),
        _repo(github_id=2, name="a", stars=100, pushed_days_ago=1),
        _repo(github_id=3, name="c", stars=10, pushed_days_ago=None),
    ]

    brief = build_account_brief("acme", repos, observed_at=observed_at)
    top = brief["observed_evidence"]["top_repositories_by_stars"]

    assert [item["full_name"] for item in top] == ["acme/a", "acme/b", "acme/c"]
    assert all(item["source_locator"].startswith("https://github.com/acme/") for item in top)
