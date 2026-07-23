import os
import logging
from github import Github, GithubException
from src.schemas import PRReviewSummary

logger = logging.getLogger(__name__)

def get_github_client() -> Github:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is missing.")
    return Github(token)

def get_pull_request_diff(repo_name: str, pr_number: int) -> str:
    """Fetches the unified git diff for a pull request."""
    g = get_github_client()
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    diff_chunks = []
    for file in pr.get_files():
        if file.patch:
            diff_chunks.append(f"--- a/{file.filename}\n+++ b/{file.filename}\n{file.patch}")
            
    return "\n\n".join(diff_chunks)

def get_commit_diff(repo_name: str, commit_sha: str) -> str:
    """Fetches the git diff for a specific commit SHA."""
    g = get_github_client()
    repo = g.get_repo(repo_name)
    commit = repo.get_commit(commit_sha)
    
    diff_chunks = []
    for file in commit.files:
        if file.patch:
            diff_chunks.append(f"--- a/{file.filename}\n+++ b/{file.filename}\n{file.patch}")
            
    return "\n\n".join(diff_chunks)

def post_review_comments(repo_name: str, pr_number: int, review_summary: PRReviewSummary):
    """Posts general summary comment and inline review comments on the PR."""
    g = get_github_client()
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    commit = repo.get_commits().reversed[0]

    # Post general PR comment summary
    body = f"## 🤖 AI PR Security Review\n\n"
    body += f"**Overall Sentiment:** `{review_summary.overall_sentiment}`\n\n"
    body += f"### Summary\n{review_summary.summary}\n"
    
    pr.create_issue_comment(body)

    # Post inline comments on specific lines
    for finding in review_summary.findings:
        try:
            comment_text = f"**[{finding.severity}] {finding.category}**\n\n{finding.comment}"
            if finding.suggested_fix:
                comment_text += f"\n\n**Suggested Fix:**\n```python\n{finding.suggested_fix}\n```"

            pr.create_review_comment(
                body=comment_text,
                commit=commit,
                path=finding.file_path,
                line=finding.line_number
            )
        except GithubException as e:
            logger.warning(f"Could not post inline comment on {finding.file_path}:{finding.line_number}: {e}")