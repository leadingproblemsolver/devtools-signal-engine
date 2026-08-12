from datetime import UTC, datetime

from devtools_signal_engine.pr_metrics import (
    PullRequestEvidence,
    calculate_pr_metrics,
)


def _dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=UTC)


def test_recent_merge_counts_and_duration_is_hours():
    metrics = calculate_pr_metrics(
        [
            PullRequestEvidence(
                created_at=_dt(2026, 7, 28),
                merged_at=_dt(2026, 8, 10),
                state="closed",
            )
        ],
        observed_at=_dt(2026, 8, 12),
    )

    assert metrics.merged_prs_30d == 1
    assert metrics.median_merge_hours_30d == 13 * 24
    assert metrics.stale_open_prs_14d == 0


def test_open_pr_older_than_14_days_is_stale():
    metrics = calculate_pr_metrics(
        [
            PullRequestEvidence(
                created_at=_dt(2026, 7, 20),
                merged_at=None,
                state="open",
            )
        ],
        observed_at=_dt(2026, 8, 12),
    )

    assert metrics.open_prs == 1
    assert metrics.stale_open_prs_14d == 1
    assert metrics.merged_prs_30d == 0
    assert metrics.median_merge_hours_30d is None


def test_future_merge_is_not_counted():
    metrics = calculate_pr_metrics(
        [
            PullRequestEvidence(
                created_at=_dt(2026, 8, 10),
                merged_at=_dt(2026, 8, 13),
                state="closed",
            )
        ],
        observed_at=_dt(2026, 8, 12),
    )

    assert metrics.merged_prs_30d == 0


def test_merge_older_than_30_days_is_not_counted():
    metrics = calculate_pr_metrics(
        [
            PullRequestEvidence(
                created_at=_dt(2026, 6, 1),
                merged_at=_dt(2026, 7, 1),
                state="closed",
            )
        ],
        observed_at=_dt(2026, 8, 12),
    )

    assert metrics.merged_prs_30d == 0
