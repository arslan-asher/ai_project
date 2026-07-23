import os
import sys
import logging
from src.github_client import get_pull_request_diff, post_review_comments, get_commit_diff
from src.analyzer import analyze_diff

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    repo_name = os.getenv("REPOSITORY")
    pr_number_str = os.getenv("PR_NUMBER")
    commit_sha = os.getenv("COMMIT_SHA")

    if not repo_name:
        logger.error("REPOSITORY environment variable is missing.")
        sys.exit(1)

    # Scenario A: Triggered by Pull Request
    if pr_number_str and pr_number_str.isdigit():
        pr_number = int(pr_number_str)
        logger.info(f"Initializing PR Handler for {repo_name} #PR-{pr_number}")
        
        diff_text = get_pull_request_diff(repo_name, pr_number)
        if not diff_text:
            logger.info("No diff found or PR is empty.")
            return

        review_results = analyze_diff(diff_text)
        logger.info("AI Analysis complete. Posting review comments on PR...")
        post_review_comments(repo_name, pr_number, review_results)
        logger.info("Successfully completed PR security review!")

    # Scenario B: Triggered by Direct Push / Commit
    elif commit_sha:
        logger.info(f"Initializing Commit Handler for {repo_name} @ {commit_sha[:7]}")
        
        diff_text = get_commit_diff(repo_name, commit_sha)
        if not diff_text:
            logger.info("No diff found for this commit.")
            return

        review_results = analyze_diff(diff_text)
        
        # Display results directly in GitHub Actions logs
        print("\n==================================================")
        print(f"🔒 AI SECURITY REVIEW FOR COMMIT: {commit_sha[:7]}")
        print(f"Overall Sentiment: {review_results.overall_sentiment}")
        print("==================================================\n")
        print(f"Summary:\n{review_results.summary}\n")
        
        if review_results.findings:
            print("🚨 FINDINGS DETECTED:")
            for finding in review_results.findings:
                print(f" File: {finding.file_path} (Line {finding.line_number})")
                print(f" Severity: {finding.severity} | Category: {finding.category}")
                print(f" Comment: {finding.comment}")
                if finding.suggested_fix:
                    print(f" Fix:\n{finding.suggested_fix}\n")
                print("-" * 40)
        else:
            print(" No security issues found in this commit!")
            
    else:
        logger.error("Neither PR_NUMBER nor COMMIT_SHA was provided.")
        sys.exit(1)

if __name__ == "__main__":
    main()