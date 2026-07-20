from pydantic import BaseModel, Field
from typing import List, Optional

class CodeFinding(BaseModel):
    file_path: str = Field(description="Relative path to the file reviewed")
    line_number: int Field(description="Line number where the issue occurs in the diff")
    category: str = Field(description="Category: Security, Bug, Performance, or Style")
    severity: str = Field(description="HIGH, MEDIUM, or LOW")
    comment: str = Field(description="Clear explanation of the issue")
    suggested_fix: Optional[str] = Field(description="Exact code replacement snippet, if applicable")

class PRReviewSummary(BaseModel):
    overall_sentiment: str = Field(description="APPROVE, REQUEST_CHANGES, or COMMENT")
    summary: str = Field(description="High-level markdown summary of the PR review")
    findings: List[CodeFinding]