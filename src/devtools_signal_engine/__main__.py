from __future__ import annotations

import argparse
import os
import sys

from .account_summary import build_account_summary, format_account_summary
from .cohorts import COHORTS, enrichment_targets, format_cohort_catalog, runnable_targets
from .github import GitHubAPIError, GitHubClient


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m devtools_signal_engine",
        description="Build evidence-backed account briefs from public GitHub organization signals.",
    )
    parser.add_argument("github_org", nargs="?", help="one GitHub organization to inspect")
    parser.add_argument(
        "--cohort",
        choices=sorted(COHORTS),
        help="run every GitHub-observable organization in a predefined benchmark cohort",
    )
    parser.add_argument(
        "--list-cohorts",
        action="store_true",
        help="print predefined benchmark and enrichment targets without calling GitHub",
    )
    return parser


def _run_one(client: GitHubClient, github_org: str) -> bool:
    try:
        summary = build_account_summary(client, github_org)
    except (GitHubAPIError, ValueError) as exc:
        print(f"error [{github_org}]: {exc}", file=sys.stderr)
        return False

    print(format_account_summary(summary))
    return True


def _run_cohort(client: GitHubClient, cohort_name: str) -> int:
    runnable = runnable_targets(cohort_name)
    enrichment = enrichment_targets(cohort_name)
    failures: list[str] = []

    for index, target in enumerate(runnable, start=1):
        print(f"=== {cohort_name.upper()} {index}/{len(runnable)}: {target.organization} ({target.github_org}) ===")
        if not _run_one(client, target.github_org or ""):
            failures.append(target.github_org or target.organization)
        print()

    if enrichment:
        print("=== ENRICHMENT-ONLY TARGETS (NOT RUN) ===")
        for target in enrichment:
            print(f"- {target.organization}: {target.rationale}")
            print(f"  next: {target.next_action}")
        print()

    if failures:
        print(f"cohort completed with {len(failures)} failure(s): {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    selected_modes = int(args.github_org is not None) + int(args.cohort is not None) + int(args.list_cohorts)
    if selected_modes != 1:
        parser.error("choose exactly one of <github-org>, --cohort, or --list-cohorts")

    if args.list_cohorts:
        print(format_cohort_catalog())
        return 0

    client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
    if args.cohort is not None:
        return _run_cohort(client, args.cohort)

    return 0 if _run_one(client, args.github_org) else 1


if __name__ == "__main__":
    raise SystemExit(main())
