from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import median
from typing import Iterable


@dataclass(frozen=True, slots=True)
class PullRequestEvidence:
    created_at: datetime
    merged_at: datetime | None
    state: str


@dataclass(frozen=True, slots=True)
class PullRequestMetrics:
    merged_prs_30d: int
    median_merge_hours_30d: float | None
    open_prs: int
    stale_open_prs_14d: int


def calculate_pr_metrics(
    prs: Iterable[PullRequestEvidence],
    *,
    observed_at: datetime,
) -> PullRequestMetrics:
    """Calculate bounded, explainable PR workflow metrics from normalized evidence."""

    cutoff_30d = observed_at - timedelta(days=30)
    cutoff_14d = observed_at - timedelta(days=14)

    prs_list = list(prs)

    merged_recently = [
        pr
        for pr in prs_list
        if pr.merged_at is not None
        and cutoff_30d <= pr.merged_at <= observed_at
    ]

    merge_durations_hours = [
        (pr.merged_at - pr.created_at).total_seconds() / 3600
        for pr in merged_recently
        if pr.merged_at is not None
    ]

    open_prs = [pr for pr in prs_list if pr.state == "open"]
    stale_open_prs = [
        pr
        for pr in open_prs
        if pr.created_at <= cutoff_14d
    ]

    return PullRequestMetrics(
        merged_prs_30d=len(merged_recently),
        median_merge_hours_30d=(
            float(median(merge_durations_hours))
            if merge_durations_hours
            else None
        ),
        open_prs=len(open_prs),
        stale_open_prs_14d=len(stale_open_prs),
    )
