from pydantic import BaseModel, Field
from typing import List, Optional

class CodeFinding(BaseModel):
    file_path: str = Field(description="Relative path to the file reviewed")
    line_number: int = Field(description="Line number in the new/modified file where the issue occurs")
    category: str = Field(description="Category of finding: Security, Bug, Performance, or Best Practice")
    severity: str = Field(description="Severity level: HIGH, MEDIUM, or LOW")
    comment: str = Field(description="Concise explanation of the flaw or security risk")
    suggested_fix: Optional[str] = Field(description="Optional exact code replacement snippet")

class PRReviewSummary(BaseModel):
    overall_sentiment: str = Field(description="One of: APPROVE, REQUEST_CHANGES, or COMMENT")
    summary: str = Field(description="High-level markdown summary of the entire PR diff review")
    findings: List[CodeFinding] = Field(default_factory=list, description="List of specific code issues found")
