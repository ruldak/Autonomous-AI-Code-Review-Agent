from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKER = "blocker"

class Category(str, Enum):
    LOGIC_BUG = "Logic Bug"
    SECURITY = "Security"
    ERROR_HANDLING = "Error Handling"
    TYPE_SAFETY = "Type Safety"
    RESOURCE_LEAK = "Resource Leak"
    CONCURRENCY = "Concurrency"
    API_CONTRACT = "API Contract"
    PERFORMANCE = "Performance"
    DATA_INTEGRITY = "Data Integrity"
    CONFIGURATION = "Configuration"

class Finding(BaseModel):
    severity: Severity = Field(description="Tingkat keparahan issue")
    line: Optional[int] = Field(description="Nomor baris di mana issue ditemukan, jika ada")
    category: Category = Field(description="Kategori issue")
    message: str = Field(description="Pesan singkat tentang issue")
    explanation: str = Field(description="Penjelasan detail mengapa ini adalah issue tanpa memberikan saran perbaikan")

class ReviewResult(BaseModel):
    findings: List[Finding] = Field(description="Daftar temuan issue dari code review")
    summary: str = Field(description="Ringkasan singkat dari hasil review")