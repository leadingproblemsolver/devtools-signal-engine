from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx


class GitHubAPIError(RuntimeError):
    """Safe, domain-level failure while acquiring GitHub data."""


class GitHubClient:
    BASE_URL = "https://api.github.com"
    CODEOWNERS_PATHS = (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS")

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

                if len(chunk) < self.per_page:
                    break

                page += 1

        return repos

    def list_repository_workflows(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Return every GitHub Actions workflow visible for a repository."""
        self._validate_repo_coordinates(owner, repo)
        url = f"{self.BASE_URL}/repos/{owner.strip()}/{repo.strip()}/actions/workflows"
        page = 1
        workflows: list[dict[str, Any]] = []

        with httpx.Client(timeout=self.timeout_seconds, headers=self._headers()) as client:
            while True:
                try:
                    response = client.get(
                        url,
                        params={"per_page": self.per_page, "page": page},
                    )
                except httpx.TimeoutException as exc:
                    raise GitHubAPIError(
                        f"GitHub workflow request timed out after {self.timeout_seconds}s on page {page}"
                    ) from exc
                except httpx.RequestError as exc:
                    raise GitHubAPIError(
                        f"GitHub workflow network request failed on page {page}: {exc.__class__.__name__}"
                    ) from exc

                self._raise_for_response(response, page=page)
                try:
                    payload = response.json()
                except ValueError as exc:
                    raise GitHubAPIError("GitHub returned invalid workflow JSON") from exc

                if not isinstance(payload, dict) or not isinstance(payload.get("workflows"), list):
                    raise GitHubAPIError(
                        "GitHub returned an unexpected workflow payload; expected workflows list"
                    )

                chunk = payload["workflows"]
                workflows.extend(chunk)
                if len(chunk) < self.per_page:
                    break
                page += 1

        return workflows

    def find_codeowners_path(self, owner: str, repo: str) -> str | None:
        """Return the first supported CODEOWNERS path that exists, otherwise None."""
        self._validate_repo_coordinates(owner, repo)

        with httpx.Client(timeout=self.timeout_seconds, headers=self._headers()) as client:
            for path in self.CODEOWNERS_PATHS:
                encoded_path = quote(path, safe="/")
                url = f"{self.BASE_URL}/repos/{owner.strip()}/{repo.strip()}/contents/{encoded_path}"
                try:
                    response = client.get(url)
                except httpx.TimeoutException as exc:
                    raise GitHubAPIError(
                        f"GitHub CODEOWNERS request timed out after {self.timeout_seconds}s"
                    ) from exc
                except httpx.RequestError as exc:
                    raise GitHubAPIError(
                        f"GitHub CODEOWNERS network request failed: {exc.__class__.__name__}"
                    ) from exc

                if response.status_code == 404:
                    continue
                self._raise_for_response(response, page=1)
                return path

        return None

    @staticmethod
    def _validate_repo_coordinates(owner: str, repo: str) -> None:
        if not owner or not owner.strip():
            raise ValueError("owner must be a non-empty string")
        if not repo or not repo.strip():
            raise ValueError("repo must be a non-empty string")

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
