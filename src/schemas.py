from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class Vulnerability(BaseModel):
    file_path: str
    line_number: Optional[int] = None
    issue_description: str
    severity: Severity

class AnalysisResult(BaseModel):
    vulnerabilities: List[Vulnerability] = []
    has_critical: bool = False