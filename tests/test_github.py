from __future__ import annotations

import httpx
import pytest

from devtools_signal_engine.github import GitHubAPIError, GitHubClient


def _repos(count: int, start: int = 0) -> list[dict[str, object]]:
    return [{"id": i, "name": f"repo-{i}"} for i in range(start, start + count)]


def test_headers_without_token() -> None:
    headers = GitHubClient()._headers()
    assert "Authorization" not in headers
    assert headers["X-GitHub-Api-Version"] == "2022-11-28"


def test_headers_with_token() -> None:
    headers = GitHubClient(token="secret")._headers()
    assert headers["Authorization"] == "Bearer secret"


def test_single_page_fetch(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def fake_get(self, url, *, params):
        calls.append(params["page"])
        return httpx.Response(200, json=_repos(37), request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    result = GitHubClient(per_page=100).list_org_repositories("example")
    assert len(result) == 37
    assert calls == [1]


def test_multiple_pages_accumulate(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def fake_get(self, url, *, params):
        page = params["page"]
        calls.append(page)
        payload = {1: _repos(100, 0), 2: _repos(100, 100), 3: _repos(37, 200)}[page]
        return httpx.Response(200, json=payload, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    result = GitHubClient(per_page=100).list_org_repositories("example")
    assert len(result) == 237
    assert calls == [1, 2, 3]


def test_exact_multiple_requires_terminal_page(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def fake_get(self, url, *, params):
        page = params["page"]
        calls.append(page)
        payload = {1: _repos(100, 0), 2: _repos(100, 100), 3: []}[page]
        return httpx.Response(200, json=payload, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    result = GitHubClient(per_page=100).list_org_repositories("example")
    assert len(result) == 200
    assert calls == [1, 2, 3]


def test_page_two_failure_never_returns_partial_data(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(self, url, *, params):
        if params["page"] == 1:
            return httpx.Response(200, json=_repos(100), request=httpx.Request("GET", url))
        return httpx.Response(500, json={"message": "boom"}, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    with pytest.raises(GitHubAPIError, match="HTTP 500 on page 2"):
        GitHubClient(per_page=100).list_org_repositories("example")


def test_200_with_wrong_payload_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(self, url, *, params):
        return httpx.Response(200, json={"message": "weird"}, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    with pytest.raises(GitHubAPIError, match="expected a list"):
        GitHubClient().list_org_repositories("example")


def test_timeout_becomes_domain_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(self, url, *, params):
        raise httpx.ReadTimeout("slow", request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    with pytest.raises(GitHubAPIError, match="timed out"):
        GitHubClient(timeout_seconds=0.5).list_org_repositories("example")


def test_invalid_per_page_rejected() -> None:
    with pytest.raises(ValueError, match="between 1 and 100"):
        GitHubClient(per_page=101)
