#!/usr/bin/env python3
"""PR Status Checker — fetches status of our submitted PRs."""
import subprocess, json, sys

REPO = "Hmbown/DeepSeek-TUI"

def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  (failed: {result.stderr.strip()[:100]})")
        return None
    return result.stdout.strip()

def check_pr(pr_number):
    data = run(["gh", "pr", "view", str(pr_number), "--repo", REPO, "--json", "number,title,state,mergeable,reviews,createdAt,updatedAt"])
    if not data:
        return None
    return json.loads(data)

# Get all PRs authored by us
list_data = run(["gh", "pr", "list", "--repo", REPO, "--author", "tyouter", "--state", "all", "--limit", "20", "--json", "number,title,state,updatedAt"])
if not list_data:
    print("No PRs found or gh not available.")
    sys.exit(0)

prs = json.loads(list_data)
print(f"{'=' * 60}")
print(f"  PR Status — {len(prs)} PR(s)")
print(f"{'=' * 60}")
print()

for pr in prs:
    num = pr["number"]
    state = pr["state"]
    title = pr["title"]
    updated = pr["updatedAt"][:10]
    
    icon = {"OPEN": "🟢", "MERGED": "✅", "CLOSED": "❌"}.get(state, "❓")
    print(f"  {icon} #{num}: {title}")
    print(f"     State: {state} | Updated: {updated}")
    
    # Get review details
    detail = check_pr(num)
    if detail:
        reviews = detail.get("reviews", [])
        if reviews:
            for r in reviews[-3:]:
                print(f"     Review: {r['state']} by {r['author']['login']}")
        if detail.get("mergeable") == "MERGEABLE":
            print(f"     Mergeable: ✅")
    print()

print(f"{'=' * 60}")
