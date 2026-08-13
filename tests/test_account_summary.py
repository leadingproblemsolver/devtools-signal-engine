from datetime import datetime, timezone

from devtools_signal_engine.account_summary import build_account_summary


OBSERVED_AT = datetime(2026, 8, 13, 6, 0, tzinfo=timezone.utc)


class FakeClient:
    def list_org_repositories(self, org):
        assert org == "vercel"
        return [
            {
                "name": "repo-a",
                "pushed_at": "2026-08-12T12:00:00Z",
                "archived": False,
                "html_url": "https://github.com/vercel/repo-a",
            },
            {
                "name": "repo-b",
                "pushed_at": "2026-07-01T12:00:00Z",
                "archived": False,
                "html_url": "https://github.com/vercel/repo-b",
            },
            {
                "name": "repo-c",
                "pushed_at": "2026-08-10T12:00:00Z",
                "archived": True,
                "html_url": "https://github.com/vercel/repo-c",
            },
        ]

    def list_repository_workflows(self, owner, repo):
        assert owner == "vercel"
        return [{"id": 1}, {"id": 2}] if repo == "repo-a" else []

    def find_codeowners_path(self, owner, repo):
        return ".github/CODEOWNERS" if repo == "repo-a" else None

    def search_pull_requests(self, query, *, max_items=100):
        if "is:merged" in query:
            return (
                2,
                [
                    {
                        "pull_request": {
                            "url": "https://api.github.com/repos/vercel/repo-a/pulls/1"
                        }
                    },
                    {
                        "pull_request": {
                            "url": "https://api.github.com/repos/vercel/repo-a/pulls/2"
                        }
                    },
                ],
            )
        if "is:open" in query:
            return 4, []
        raise AssertionError(query)

    def fetch_pull_request_detail(self, api_url):
        if api_url.endswith("/1"):
            return {
                "created_at": "2026-08-01T00:00:00Z",
                "merged_at": "2026-08-01T12:00:00Z",
                "html_url": "https://github.com/vercel/repo-a/pull/1",
            }
        return {
            "created_at": "2026-08-02T00:00:00Z",
            "merged_at": "2026-08-03T00:00:00Z",
            "html_url": "https://github.com/vercel/repo-a/pull/2",
        }


def test_build_account_summary_is_explicit_about_scope():
    summary = build_account_summary(
        FakeClient(),
        "vercel",
        observed_at=OBSERVED_AT,
        repo_sample_limit=10,
        pr_detail_sample_limit=100,
    )

    assert summary.repo_count == 3
    assert summary.active_repos_30d == 1
    assert summary.github_actions_workflow_count == 2
    assert summary.repos_using_actions == 1
    assert summary.repos_with_codeowners == 1
    assert summary.merged_prs_30d == 2
    assert summary.median_merge_hours_30d == 18.0
    assert summary.median_merge_sample_size == 2
    assert summary.stale_open_prs_14d == 4
    assert summary.analyzed_repositories == ("repo-a",)


def test_archived_recent_repo_does_not_count_as_active():
    summary = build_account_summary(
        FakeClient(),
        "vercel",
        observed_at=OBSERVED_AT,
    )
    assert "repo-c" not in summary.analyzed_repositories
    assert summary.active_repos_30d == 1
