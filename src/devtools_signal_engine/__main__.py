from __future__ import annotations

import os
import sys

from .account_summary import build_account_summary, format_account_summary
from .github import GitHubAPIError, GitHubClient


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python -m devtools_signal_engine <github-org>", file=sys.stderr)
        return 2

    client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
    try:
        summary = build_account_summary(client, sys.argv[1])
    except (GitHubAPIError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(format_account_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
