from datetime import UTC, datetime

import pytest

from devtools_signal_engine.normalize import (
    RepositoryNormalizationError,
    normalize_repositories,
    normalize_repository,
)


def _repo(**overrides):
    raw = {
        "id": 123,
        "name": "sales-engine",
        "full_name": "acme/sales-engine",
        "html_url": "https://github.com/acme/sales-engine",
        "owner": {"login": "acme"},
        "default_branch": "main",
        "language": "Python",
        "fork": False,
        "archived": False,
        "stargazers_count": 10,
        "forks_count": 2,
        "open_issues_count": 3,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2026-08-01T00:00:00Z",
        "pushed_at": "2026-08-10T00:00:00Z",
    }
    raw.update(overrides)
    return raw


def test_normalizes_required_identity_and_provenance():
    observed = datetime(2026, 8, 12, tzinfo=UTC)
    repo = normalize_repository(_repo(), observed_at=observed)

    assert repo.github_id == 123
    assert repo.full_name == "acme/sales-engine"
    assert repo.owner_login == "acme"
    assert repo.source_locator == "https://github.com/acme/sales-engine"
    assert repo.observed_at == observed


def test_repo_rename_does_not_change_identity():
    before = normalize_repository(_repo())
    after = normalize_repository(
        _repo(name="revenue-engine", full_name="acme/revenue-engine")
    )

    assert before.github_id == after.github_id == 123
    assert before.name != after.name


def test_duplicate_id_in_same_batch_fails():
    with pytest.raises(RepositoryNormalizationError, match="duplicate GitHub repository id"):
        normalize_repositories([
            _repo(),
            _repo(name="revenue-engine", full_name="acme/revenue-engine"),
        ])


def test_missing_required_identity_field_fails():
    raw = _repo()
    del raw["id"]

    with pytest.raises(RepositoryNormalizationError, match="required identity fields"):
        normalize_repository(raw)


def test_non_positive_id_fails():
    with pytest.raises(RepositoryNormalizationError, match="positive integer"):
        normalize_repository(_repo(id=0))


def test_invalid_required_datetime_fails():
    with pytest.raises(RepositoryNormalizationError, match="invalid datetime"):
        normalize_repository(_repo(created_at="not-a-date"))


def test_negative_numeric_metric_fails():
    with pytest.raises(RepositoryNormalizationError, match="non-negative integer"):
        normalize_repository(_repo(stargazers_count=-1))
