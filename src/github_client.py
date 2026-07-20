import os
import logging
from github import Github, GithubException
from src.schemas import PRReviewSummary

logger = logging.getLogger(__name__)

class GitHubPRHandler:
    def __init__(self, repo_name: str, pr_number: int):
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is not set.")
        
        self.gh = Github(token)
        self.repo = self.gh.get_repo(repo_name)
        self.pr = self.repo.get_pull(pr_number)

    def get_pull_request_diff(self) -> str:
        """Retrieves raw diff for the specified pull request."""
        files = self.pr.get_files()
        diff_chunks = []
        
        # Ignored extensions/files to save tokens
        ignored_exts = ('.lock', '.json', '.min.js', '.min.css', '.png', '.jpg', '.svg')
        
        for file in files:
            if file.filename.endswith(ignored_exts):
                continue
            
            diff_chunks.append(f"File: {file.filename}\nStatus: {file.status}\nPatch:\n{file.patch}\n")
        
        return "\n---\n".join(diff_chunks)

    def post_review(self, review: PRReviewSummary):
        """Posts top-level summary comment and inline comments to the PR."""
        body = f"## 🤖 AI PR Security & Code Review\n\n"
        body += f"**Overall Status:** `{review.overall_sentiment}`\n\n"
        body += f"### Summary\n{review.summary}\n\n"

        if not review.findings:
            body += "✅ **No security issues or critical bugs detected.**"
            self.pr.create_issue_comment(body)
            logger.info("Posted clean review comment to PR.")
            return

        body += f"### Key Findings ({len(review.findings)})\n"
        body += "Detailed inline comments have been added directly to the code diff below."
        
        # Post top-level PR comment
        self.pr.create_issue_comment(body)

        # Post inline diff comments
        commit = self.pr.get_commits().reversed[0]  # Latest commit
        
        for finding in review.findings:
            comment_body = (
                f"**[{finding.severity}] {finding.category}**\n"
                f"{finding.comment}\n"
            )
            if finding.suggested_fix:
                comment_body += f"\n```suggestion\n{finding.suggested_fix}\n```"

            try:
                self.pr.create_review_comment(
                    body=comment_body,
                    commit=commit,
                    path=finding.file_path,
                    line=finding.line_number
                )
            except GithubException as e:
                # If inline line matching fails, log warning and continue
                logger.warning(f"Could not post inline comment on {finding.file_path}:{finding.line_number} - {e}")