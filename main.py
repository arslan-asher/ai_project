import sys
from src.analyzer import analyze_code

def main():
    print("🔍 Running AI Security Review...")
    
    result = analyze_code()
    
    if not result.vulnerabilities:
        print("✅ No security issues detected.")
        sys.exit(0)
        
    print(f"\n⚠️  Found {len(result.vulnerabilities)} potential issue(s):\n")
    
    for issue in result.vulnerabilities:
        location = f"{issue.file_path}:{issue.line_number}" if issue.line_number else issue.file_path
        print(f"  [{issue.severity.value}] {location} - {issue.issue_description}")
    
    print("-" * 50)
    
    if result.has_critical:
        print("❌ CRITICAL SECURITY RISK DETECTED!")
        print("Push/Merge blocked. Resolve critical vulnerabilities to pass.")
        sys.exit(1)  # Triggers GitHub Action job failure
        
    print("⚠️  Only non-critical warnings found. Proceeding with build.")
    sys.exit(0)

if __name__ == "__main__":
    main()