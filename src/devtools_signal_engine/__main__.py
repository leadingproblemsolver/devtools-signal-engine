from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime

from .account_brief import build_account_brief
from .github import GitHubAPIError, GitHubClient
from .normalize import RepositoryNormalizationError, normalize_repositories


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python -m devtools_signal_engine <github-org>", file=sys.stderr)
        return 2

    org = sys.argv[1]
    observed_at = datetime.now(UTC)
    client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))

    try:
        raw_repositories = client.list_org_repositories(org)
        repositories = normalize_repositories(raw_repositories, observed_at=observed_at)
        brief = build_account_brief(org, repositories, observed_at=observed_at)
    except (GitHubAPIError, RepositoryNormalizationError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(brief, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
