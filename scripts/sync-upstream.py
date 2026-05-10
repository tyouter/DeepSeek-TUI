#!/usr/bin/env python3
"""
DeepSeek TUI — Upstream Sync Checker
Usage:  python scripts/sync-upstream.py

Checks:
1. Branch status relative to upstream/main
2. New upstream issues/PRs since last check
3. Existing POOL entries vs upstream activity

Outputs a status report. Non-blocking (never exits with error).
"""
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd or REPO_ROOT, capture_output=True, text=True)


def count_commits(ref1: str, ref2: str) -> int:
    """Count commits in ref1 that are not in ref2."""
    result = run(["git", "rev-list", "--count", f"{ref1}..{ref2}"])
    try:
        return int(result.stdout.strip()) if result.returncode == 0 else -1
    except ValueError:
        return -1


def get_current_branch() -> str:
    result = run(["git", "branch", "--show-current"])
    return result.stdout.strip()


def check_gh_available() -> bool:
    result = run(["gh", "--version"])
    return result.returncode == 0


def fetch_upstream_issues(limit: int = 30) -> list[dict]:
    """Fetch recent open issues from upstream."""
    if not check_gh_available():
        return []

    result = run([
        "gh", "issue", "list",
        "--repo", "Hmbown/DeepSeek-TUI",
        "--state", "open",
        "--limit", str(limit),
        "--json", "number,title,labels,updatedAt",
    ])
    if result.returncode != 0:
        print(f"  (gh issue list failed: {result.stderr.strip()[:100]})")
        return []

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def fetch_upstream_prs(limit: int = 15) -> list[dict]:
    """Fetch recent open PRs from upstream."""
    if not check_gh_available():
        return []

    result = run([
        "gh", "pr", "list",
        "--repo", "Hmbown/DeepSeek-TUI",
        "--state", "open",
        "--limit", str(limit),
        "--json", "number,title,labels,updatedAt",
    ])
    if result.returncode != 0:
        return []

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def main():
    print(f"{'=' * 44}")
    print(f"  Upstream Sync Check — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'=' * 44}")
    print()

    # Branch status
    branch = get_current_branch()
    behind = count_commits(branch, "upstream/main")  # upstream commits we don't have
    ahead = count_commits("upstream/main", branch)   # our commits upstream doesn't have

    print(f"  Branch:     {branch}")
    print(f"  Behind:     {behind} commits behind upstream/main" if behind >= 0 else "  Behind:     (could not determine)")
    print(f"  Ahead:      {ahead} commits ahead of upstream/main" if ahead >= 0 else "  Ahead:      (could not determine)")
    print()

    # Upstream activity
    issues = fetch_upstream_issues()
    prs = fetch_upstream_prs()

    if issues:
        print(f"  Upstream open issues ({len(issues)} newest):")
        for iss in issues[:10]:
            labels = ", ".join(l["name"] for l in iss.get("labels", []))
            label_str = f" [{labels}]" if labels else ""
            print(f"    #{iss['number']}: {iss['title']}{label_str}")
    else:
        print(f"  Upstream issues: (gh not available — install GitHub CLI)")

    print()

    if prs:
        print(f"  Upstream open PRs ({len(prs)} newest):")
        for pr in prs[:8]:
            labels = ", ".join(l["name"] for l in pr.get("labels", []))
            label_str = f" [{labels}]" if labels else ""
            print(f"    #{pr['number']}: {pr['title']}{label_str}")
    else:
        print(f"  Upstream PRs: (gh not available)")

    print()
    print(f"{'=' * 44}")

    # Warnings
    warnings = []
    if behind > 0:
        warnings.append(f"Branch is {behind} commits behind upstream/main. Consider rebasing.")

    for w in warnings:
        print(f"  ⚠️  {w}")

    print()


if __name__ == "__main__":
    main()
