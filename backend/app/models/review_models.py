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
    severity: Severity = Field(description="Severity level of the issue")
    line: Optional[int] = Field(description="Line number where the issue was found, if any")
    category: Category = Field(description="Category of the issue")
    message: str = Field(description="Brief message about the issue")
    explanation: str = Field(description="Detailed explanation of why this is an issue without providing remediation suggestions")

class ReviewResult(BaseModel):
    findings: List[Finding] = Field(description="List of issue findings from the code review")
    summary: str = Field(description="Brief summary of the review results")