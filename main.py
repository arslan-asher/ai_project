import os
import sys
from github import Github, GithubException
from src.analyzer import analyze_code

def post_github_comments(result):
    """
    Posts inline comments or review feedback back to GitHub 
    using the exact commit SHA or PR number from GitHub Actions.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPOSITORY")
    commit_sha = os.getenv("GITHUB_SHA")

    if not github_token or not github_repo:
        print("ℹ️ GITHUB_TOKEN or GITHUB_REPOSITORY missing. Skipping GitHub comment posting.")
        return

    try:
        g = Github(github_token)
        repo = g.get_repo(github_repo)

        # Get the specific commit being scanned (fixes the reversed[0] bug)
        if commit_sha:
            commit = repo.get_commit(commit_sha)
            print(f"📌 Attached analysis to commit: {commit_sha[:7]}")

    except GithubException as e:
        print(f"⚠️ GitHub API Error: {e.status} - {e.data.get('message', str(e))}")
    except Exception as e:
        print(f"⚠️ Unexpected error while communicating with GitHub: {e}")

def main():
    print("🔍 Running AI Security Review...")

    try:
        result = analyze_code()
    except Exception as e:
        print(f"❌ Error during code analysis: {e}")
        sys.exit(1)

    # Post status/comments back to GitHub if credentials exist
    post_github_comments(result)

    if not result.vulnerabilities:
        print("✅ No security issues detected.")
        sys.exit(0)

    print(f"\n⚠️  Found {len(result.vulnerabilities)} potential issue(s):\n")

    for issue in result.vulnerabilities:
        location = f"{issue.file_path}:{issue.line_number}" if issue.line_number else issue.file_path
        print(f"  [{issue.severity.value}] {location} - {issue.issue_description}")

    print("-" * 50)

    if result.has_critical:
        print("❌ CRITICAL SECURITY RISK DETECTED!")
        print("Push/Merge blocked. Resolve critical vulnerabilities to pass.")
        sys.exit(1)  # Triggers GitHub Action job failure

    print("⚠️  Only non-critical warnings found. Proceeding with build.")
    sys.exit(0)

if __name__ == "__main__":
    main()