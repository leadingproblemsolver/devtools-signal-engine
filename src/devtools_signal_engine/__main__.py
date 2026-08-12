from __future__ import annotations

import os
import sys

from .github import GitHubAPIError, GitHubClient


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python -m devtools_signal_engine <github-org>", file=sys.stderr)
        return 2

    client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
    try:
        repos = client.list_org_repositories(sys.argv[1])
    except (GitHubAPIError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"organization: {sys.argv[1]}")
    print(f"repositories: {len(repos)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
