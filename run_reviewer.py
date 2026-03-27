import sys
import asyncio
from app.services.jarvis.code_reviewer import JARVISCodeReviewer
from app.services.jarvis.personality_engine import JARVISPersonalityEngine

async def main():
    files_to_review = sys.argv[1:]
    if not files_to_review:
        print("No Python files to review.")
        return

    personality = JARVISPersonalityEngine()
    reviewer = JARVISCodeReviewer(personality)
    all_findings = []

    for file_path in files_to_review:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        findings = await reviewer.review_code(code, file_path)
        all_findings.extend(findings)

        if findings:
            print(f"--- Review for {file_path} ---")
            for finding in findings:
                print(f"  - [L{finding['line']}] {finding['severity'].upper()}: {finding['message']}")

    if any(f["severity"] == "critical" for f in all_findings):
        print("\nCritical issues found. Build failed.")
        sys.exit(1)
    else:
        print("\nCode review completed. No critical issues found.")

if __name__ == "__main__":
    asyncio.run(main())
