import json
import os
from google import genai
from google.genai import types
from src.schemas import AnalysisResult, Vulnerability, Severity

SYSTEM_INSTRUCTION = """
You are a Senior Security Engineer and Code Auditor performing an automated code review.

YOUR MISSION:
Analyze the provided code contents for bugs, code quality, and security vulnerabilities.

RULES & CATEGORIES:
1. Classify every issue into one of three Severities:
   - CRITICAL: Severe security risks (e.g., SQL Injection, Remote Code Execution, Hardcoded Secret/Token/Password, unsafe eval/exec).
   - WARNING: Non-breaking bugs, inefficient logic, poor error handling, or performance bottlenecks.
   - INFO: Code style, formatting, readability improvements, or missing comments.

2. Strict Guidelines:
   - Be accurate and precise. Do not invent false positives.
   - Focus heavily on security risks that could compromise the application or data.

3. Output Format:
   Return the result strictly as a valid JSON object matching this schema:
   {
     "vulnerabilities": [
       {
         "file_path": "path/to/file.py",
         "line_number": 12,
         "issue_description": "Detailed explanation of the flaw",
         "severity": "CRITICAL" | "WARNING" | "INFO"
       }
     ]
   }
"""

def analyze_code_with_gemini(code_content: str):
    # Picks up GEMINI_API_KEY from environment variables automatically
    client = genai.Client()
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Please review this code:\n\n{code_content}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
        )
    )
    return response.text

def analyze_code() -> AnalysisResult:
    all_vulnerabilities = []
    
    # Read project Python files and submit them to Gemini
    for root, _, files in os.walk("."):
        if ".git" in root or ".github" in root or "venv" in root:
            continue
        for file in files:
            if file.endswith(".py") and file != "main.py":
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code_content = f.read()
                        
                    # Call Gemini API
                    ai_response_text = analyze_code_with_gemini(code_content)
                    data = json.loads(ai_response_text)
                    
                    # Parse issues from Gemini JSON response
                    for item in data.get("vulnerabilities", []):
                        severity_str = item.get("severity", "WARNING").upper()
                        severity = Severity[severity_str] if severity_str in Severity.__members__ else Severity.WARNING
                        
                        all_vulnerabilities.append(
                            Vulnerability(
                                file_path=item.get("file_path", file_path),
                                line_number=item.get("line_number"),
                                issue_description=item.get("issue_description"),
                                severity=severity
                            )
                        )
                except Exception as e:
                    print(f"⚠️ Error analyzing {file_path}: {e}")

    has_critical = any(v.severity == Severity.CRITICAL for v in all_vulnerabilities)
    return AnalysisResult(vulnerabilities=all_vulnerabilities, has_critical=has_critical)