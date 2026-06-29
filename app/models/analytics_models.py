from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ReviewLogResponse(BaseModel):
    id: int
    tenant_id: int
    repo_full_name: str
    pr_number: int
    status: str
    findings_count: int
    ai_metadata: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class ReviewLogListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    data: List[ReviewLogResponse]