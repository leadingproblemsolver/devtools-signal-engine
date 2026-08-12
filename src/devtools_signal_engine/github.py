from __future__ import annotations

from typing import Any

import httpx


class GitHubAPIError(RuntimeError):
    """Safe, domain-level failure while acquiring GitHub data."""


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        token: str | None = None,
        timeout_seconds: float = 10.0,
        per_page: int = 100,
    ) -> None:
        if not 1 <= per_page <= 100:
            raise ValueError("per_page must be between 1 and 100")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")
        self.token = token
        self.timeout_seconds = timeout_seconds
        self.per_page = per_page

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def list_org_repositories(self, org: str) -> list[dict[str, Any]]:
        if not org or not org.strip():
            raise ValueError("org must be a non-empty string")

        url = f"{self.BASE_URL}/orgs/{org.strip()}/repos"
        page = 1
        repos: list[dict[str, Any]] = []

        with httpx.Client(timeout=self.timeout_seconds, headers=self._headers()) as client:
            while True:
                try:
                    response = client.get(
                        url,
                        params={"per_page": self.per_page, "page": page},
                    )
                except httpx.TimeoutException as exc:
                    raise GitHubAPIError(
                        f"GitHub request timed out after {self.timeout_seconds}s on page {page}"
                    ) from exc
                except httpx.RequestError as exc:
                    raise GitHubAPIError(
                        f"GitHub network request failed on page {page}: {exc.__class__.__name__}"
                    ) from exc

                self._raise_for_response(response, page=page)

                try:
                    chunk = response.json()
                except ValueError as exc:
                    raise GitHubAPIError(
                        f"GitHub returned invalid JSON on page {page}"
                    ) from exc

                if not isinstance(chunk, list):
                    raise GitHubAPIError(
                        f"GitHub returned an unexpected payload on page {page}; expected a list"
                    )

                repos.extend(chunk)

                # Exact multiples require one terminal empty request. This is
                # intentional: it prevents silent truncation without relying on
                # a separate total-count contract.
                if len(chunk) < self.per_page:
                    break

                page += 1

        return repos

    def _raise_for_response(self, response: httpx.Response, *, page: int) -> None:
        status = response.status_code
        if status < 400:
            return
        if status == 401:
            message = "GitHub authentication failed"
        elif status == 403:
            message = "GitHub request forbidden or rate-limited"
        elif status == 404:
            message = "GitHub organization/resource not found"
        elif status == 429:
            message = "GitHub rate limit exceeded"
        elif status >= 500:
            message = "GitHub server error"
        else:
            message = "GitHub request rejected"
        raise GitHubAPIError(f"{message}: HTTP {status} on page {page}")
