from __future__ import annotations

import httpx
import pytest

from devtools_signal_engine.github import GitHubAPIError, GitHubClient


def test_workflow_pages_accumulate(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def fake_get(self, url, *, params):
        page = params["page"]
        calls.append(page)
        chunk = (
            [{"id": i, "name": f"wf-{i}"} for i in range(100)]
            if page == 1
            else [{"id": 100, "name": "release"}]
        )
        return httpx.Response(
            200,
            json={"total_count": 101, "workflows": chunk},
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    result = GitHubClient(per_page=100).list_repository_workflows("acme", "platform")

    assert len(result) == 101
    assert calls == [1, 2]


def test_unexpected_workflow_payload_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(self, url, *, params):
        return httpx.Response(200, json={"total_count": 1}, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", fake_get)

    with pytest.raises(GitHubAPIError, match="expected workflows list"):
        GitHubClient().list_repository_workflows("acme", "platform")


def test_codeowners_probe_falls_through_supported_locations(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_get(self, url, **kwargs):
        calls.append(url)
        if url.endswith("/.github/CODEOWNERS"):
            return httpx.Response(404, request=httpx.Request("GET", url))
        if url.endswith("/CODEOWNERS"):
            return httpx.Response(200, json={"name": "CODEOWNERS"}, request=httpx.Request("GET", url))
        raise AssertionError(f"unexpected request: {url}")

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    found = GitHubClient().find_codeowners_path("acme", "platform")

    assert found == "CODEOWNERS"
    assert len(calls) == 2


def test_codeowners_non_404_failure_is_not_treated_as_absence(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(self, url, **kwargs):
        return httpx.Response(500, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", fake_get)

    with pytest.raises(GitHubAPIError, match="HTTP 500"):
        GitHubClient().find_codeowners_path("acme", "platform")
