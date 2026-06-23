import re
from app.models.review_models import Finding, Severity, Category
from app.utils.logger import logger

# Kumpulan Regex untuk mendeteksi vulnerability umum
PATTERNS = {
    "AWS Access Key": re.compile(r'AKIA[0-9A-Z]{16}'),
    "Generic API Key": re.compile(r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']'),
    "Hardcoded Password": re.compile(r'(?i)(password|passwd|pwd|db_pass)\s*[:=]\s*["\']([^"\']+)["\']'),
    "SQL Injection (Concat)": re.compile(r'(?i)(execute|cursor\.execute|query|raw)\s*\(\s*["\'].*?["\']\s*\+\s*\w+'),
    "Dangerous Eval": re.compile(r'\beval\s*\('),
}

def scan_code_security(filename: str, code: str) -> list[Finding]:
    """Melakukan scanning keamanan berbasis pattern matching (Regex)."""
    findings = []
    lines = code.split('\n')
    
    for line_num, line_text in enumerate(lines, start=1):
        # Abaikan baris yang merupakan komentar (opsional, bisa disesuaikan per bahasa)
        if line_text.strip().startswith('#') or line_text.strip().startswith('//'):
            continue
            
        for pattern_name, pattern in PATTERNS.items():
            if pattern.search(line_text):
                logger.info("Security pattern matched", pattern=pattern_name, filename=filename, line=line_num)
                
                # Tentukan Severity dan Kategori berdasarkan pola yang cocok
                if pattern_name == "SQL Injection (Concat)":
                    severity = Severity.CRITICAL
                    category = Category.SECURITY
                    message = f"Potential SQL Injection via string concatenation"
                    explanation = "Menggabungkan string SQL dengan variabel eksternal secara langsung (concatenation) sangat rentan terhadap injeksi. Gunakan parameterized queries."
                elif "Eval" in pattern_name:
                    severity = Severity.CRITICAL
                    category = Category.SECURITY
                    message = "Dangerous use of eval()"
                    explanation = "Fungsi eval() mengeksekusi string sebagai kode. Jika input berasal dari user, ini adalah celah Remote Code Execution (RCE)."
                else:
                    severity = Severity.BLOCKER
                    category = Category.CONFIGURATION
                    message = f"Hardcoded secret detected: {pattern_name}"
                    explanation = "Menyimpan kredensial atau secret key secara hardcoded di dalam source code adalah risiko keamanan fatal. Secret dapat terekspos jika repository bocor atau terbaca di history commit."

                findings.append(Finding(
                    severity=severity,
                    line=line_num,
                    category=category,
                    message=message,
                    explanation=explanation
                ))
                
    return findings