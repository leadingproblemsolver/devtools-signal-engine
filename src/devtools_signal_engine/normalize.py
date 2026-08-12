from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Iterable

from .models import RepositoryEvidence


class RepositoryNormalizationError(ValueError):
    """Raised when a GitHub repository payload cannot satisfy our evidence contract."""


def _parse_github_datetime(value: Any, *, field: str, required: bool) -> datetime | None:
    if value is None:
        if required:
            raise RepositoryNormalizationError(f"missing required datetime field: {field}")
        return None
    if not isinstance(value, str):
        raise RepositoryNormalizationError(f"{field} must be an ISO-8601 string")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RepositoryNormalizationError(f"invalid datetime in {field}") from exc


def normalize_repository(
    raw: dict[str, Any],
    *,
    observed_at: datetime | None = None,
) -> RepositoryEvidence:
    """Map a raw GitHub repository object into our stable internal evidence contract."""

    observed_at = observed_at or datetime.now(UTC)

    try:
        github_id = raw["id"]
        name = raw["name"]
        full_name = raw["full_name"]
        html_url = raw["html_url"]
        owner = raw["owner"]
        owner_login = owner["login"]
    except (KeyError, TypeError) as exc:
        raise RepositoryNormalizationError("repository payload is missing required identity fields") from exc

    if not isinstance(github_id, int) or github_id <= 0:
        raise RepositoryNormalizationError("id must be a positive integer")
    for field_name, value in {
        "name": name,
        "full_name": full_name,
        "html_url": html_url,
        "owner.login": owner_login,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise RepositoryNormalizationError(f"{field_name} must be a non-empty string")

    def _integer(field: str) -> int:
        value = raw.get(field, 0)
        if not isinstance(value, int) or value < 0:
            raise RepositoryNormalizationError(f"{field} must be a non-negative integer")
        return value

    return RepositoryEvidence(
        github_id=github_id,
        name=name,
        full_name=full_name,
        owner_login=owner_login,
        html_url=html_url,
        default_branch=raw.get("default_branch") if isinstance(raw.get("default_branch"), str) else None,
        language=raw.get("language") if isinstance(raw.get("language"), str) else None,
        fork=bool(raw.get("fork", False)),
        archived=bool(raw.get("archived", False)),
        stars=_integer("stargazers_count"),
        forks=_integer("forks_count"),
        open_issues=_integer("open_issues_count"),
        created_at=_parse_github_datetime(raw.get("created_at"), field="created_at", required=True),
        updated_at=_parse_github_datetime(raw.get("updated_at"), field="updated_at", required=True),
        pushed_at=_parse_github_datetime(raw.get("pushed_at"), field="pushed_at", required=False),
        source_locator=html_url,
        observed_at=observed_at,
    )


def normalize_repositories(
    raw_repositories: Iterable[dict[str, Any]],
    *,
    observed_at: datetime | None = None,
) -> list[RepositoryEvidence]:
    """Normalize one acquisition run and reject duplicate logical repository identities."""

    timestamp = observed_at or datetime.now(UTC)
    seen_ids: set[int] = set()
    normalized: list[RepositoryEvidence] = []

    for raw in raw_repositories:
        repo = normalize_repository(raw, observed_at=timestamp)
        if repo.github_id in seen_ids:
            raise RepositoryNormalizationError(
                f"duplicate GitHub repository id in one acquisition run: {repo.github_id}"
            )
        seen_ids.add(repo.github_id)
        normalized.append(repo)

    return normalized
