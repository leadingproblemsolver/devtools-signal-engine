from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RepositoryEvidence:
    """Normalized, provenance-preserving snapshot of one GitHub repository."""

    github_id: int
    name: str
    full_name: str
    owner_login: str
    html_url: str
    default_branch: str | None
    language: str | None
    fork: bool
    archived: bool
    stars: int
    forks: int
    open_issues: int
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime | None
    source_locator: str
    observed_at: datetime
