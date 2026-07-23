from typing import List, Optional
from pydantic import BaseModel, Field

class Finding(BaseModel):
    file_path: str = Field(description="Relative path of the file reviewed.")
    line_number: int = Field(description="Line number where the issue or recommendation applies.")
    severity: str = Field(description="Severity level: CRITICAL, HIGH, MEDIUM, LOW, or INFO.")
    category: str = Field(description="Category: SECURITY, BUG, PERFORMANCE, or BEST_PRACTICE.")
    comment: str = Field(description="Detailed explanation of the issue.")
    suggested_fix: Optional[str] = Field(None, description="Suggested code replacement or fix.")

class PRReviewSummary(BaseModel):
    overall_sentiment: str = Field(description="APPROVE, REQUEST_CHANGES, or COMMENT.")
    summary: str = Field(description="High-level overview of the pull request changes and security posture.")
    findings: List[Finding] = Field(default_factory=list, description="List of specific code findings.")