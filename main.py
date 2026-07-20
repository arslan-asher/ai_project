import os
import sys
import logging
from src.github_client import GitHubPRHandler
from src.analyzer import analyze_diff

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    repo_name = os.getenv("REPOSITORY")
    pr_number_str = os.getenv("PR_NUMBER")

    if not repo_name or not pr_number_str:
        logging.error("Missing REPOSITORY or PR_NUMBER environment variables.")
        sys.exit(1)

    try:
        pr_number = int(pr_number_str)
        logging.info(f"Initializing PR Handler for {repo_name} #PR-{pr_number}")
        
        handler = GitHubPRHandler(repo_name=repo_name, pr_number=pr_number)
        
        logging.info("Fetching PR diff...")
        diff_text = handler.get_pull_request_diff()
        
        if not diff_text.strip():
            logging.info("Diff is empty or only contained ignored files. Skipping analysis.")
            sys.exit(0)

        logging.info("Analyzing diff with AI Security Engine...")
        review_results = analyze_diff(diff_text)

        logging.info("Posting results to GitHub...")
        handler.post_review(review_results)
        
        logging.info("AI PR Review successfully completed!")

    except Exception as e:
        logging.error(f"Execution failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()