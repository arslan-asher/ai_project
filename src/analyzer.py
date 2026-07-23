import os
import logging
from google import genai
from google.genai import types
from src.schemas import PRReviewSummary

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """
You are a Staff Security & Software Engineer conducting an automated code review on a GitHub Pull Request or Commit.
Analyze the provided Git Diff and look for:
1. Security Vulnerabilities (e.g., exposed API keys, credentials, SQL injection, unsafe dependencies, unvalidated inputs).
2. Logic bugs, race conditions, or unhandled exceptions.
3. Severe performance bottlenecks.

Guidelines:
- Ignore trivial formatting, whitespace, or lockfiles.
- Be precise with file paths and line numbers based strictly on the diff.
- Return output strictly matching the requested JSON schema.
"""

def analyze_diff(diff_text: str) -> PRReviewSummary:
    """Analyzes git diff text using Google Gemini Flash model and returns structured analysis."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    client = genai.Client(api_key=api_key)

    max_chars = 100_000
    if len(diff_text) > max_chars:
        logger.warning("Diff size exceeds limit. Truncating for AI review.")
        diff_text = diff_text[:max_chars] + "\n...[Diff Truncated]"

    prompt = f"Please review the following Git Diff:\n\n{diff_text}"

    logger.info("Sending diff to Gemini for analysis...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=PRReviewSummary,
            temperature=0.1,
        ),
    )

    try:
        review_data = PRReviewSummary.model_validate_json(response.text)
        return review_data
    except Exception as e:
        logger.error(f"Failed to parse Gemini response into schema: {e}")
        logger.debug(f"Raw response was: {response.text}")
        raise