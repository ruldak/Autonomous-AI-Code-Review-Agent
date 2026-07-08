import re
from app.models.review_models import Finding, Severity, Category
from app.utils.logger import logger

PATTERNS = {
    "AWS Access Key": re.compile(r'AKIA[0-9A-Z]{16}'),
    "Generic API Key": re.compile(r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']'),
    "Hardcoded Password": re.compile(r'(?i)(password|passwd|pwd|db_pass)\s*[:=]\s*["\']([^"\']+)["\']'),
    "SQL Injection (Concat)": re.compile(r'(?i)(execute|cursor\.execute|query|raw)\s*\(\s*["\'].*?["\']\s*\+\s*\w+'),
    "Dangerous Eval": re.compile(r'\beval\s*\('),
}

def scan_code_security(filename: str, code: str) -> list[Finding]:
    """Perform pattern-matching-based (Regex) security scanning."""
    findings = []
    lines = code.split('\n')
    
    for line_num, line_text in enumerate(lines, start=1):
        if line_text.strip().startswith('#') or line_text.strip().startswith('//'):
            continue
            
        for pattern_name, pattern in PATTERNS.items():
            if pattern.search(line_text):
                logger.info("Security pattern matched", pattern=pattern_name, filename=filename, line=line_num)
                
                if pattern_name == "SQL Injection (Concat)":
                    severity = Severity.CRITICAL
                    category = Category.SECURITY
                    message = f"Potential SQL Injection via string concatenation"
                    explanation = "Directly concatenating SQL strings with external variables is highly vulnerable to injection. Use parameterized queries."
                elif "Eval" in pattern_name:
                    severity = Severity.CRITICAL
                    category = Category.SECURITY
                    message = "Dangerous use of eval()"
                    explanation = "The eval() function executes a string as code. If the input comes from a user, this is a Remote Code Execution (RCE) vulnerability."
                else:
                    severity = Severity.BLOCKER
                    category = Category.CONFIGURATION
                    message = f"Hardcoded secret detected: {pattern_name}"
                    explanation = "Storing credentials or secret keys hardcoded in source code is a fatal security risk. Secrets can be exposed if the repository leaks or is read in commit history."

                findings.append(Finding(
                    severity=severity,
                    line=line_num,
                    category=category,
                    message=message,
                    explanation=explanation
                ))
                
    return findings