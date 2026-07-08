from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.db.session import get_db
from app.db.models import ReviewLog
from app.models.analytics_models import ReviewLogResponse, ReviewLogListResponse
from app.utils.logger import logger

router = APIRouter()

@router.get("/reviews/logs", response_model=ReviewLogListResponse, tags=["Analytics"])
async def get_review_logs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    repo_full_name: Optional[str] = Query(None, description="Filter by repository name"),
    status: Optional[str] = Query(None, description="Filter by status (SUCCESS/FAILED)"),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a list of review logs with pagination and filtering."""
    
    query = select(ReviewLog)
    count_query = select(func.count(ReviewLog.id))
    
    if repo_full_name:
        query = query.where(ReviewLog.repo_full_name == repo_full_name)
        count_query = count_query.where(ReviewLog.repo_full_name == repo_full_name)
    if status:
        query = query.where(ReviewLog.status == status.upper())
        count_query = count_query.where(ReviewLog.status == status.upper())
        
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    offset = (page - 1) * per_page
    query = query.order_by(ReviewLog.created_at.desc()).offset(offset).limit(per_page)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    logger.info("Fetched review logs", page=page, total=total)
    
    return ReviewLogListResponse(
        total=total,
        page=page,
        per_page=per_page,
        data=logs
    )


@router.get("/reviews/stats", response_model=dict, tags=["Analytics"])
async def get_review_stats(
    repo_full_name: Optional[str] = Query(None, description="Filter stats by repository"),
    db: AsyncSession = Depends(get_db)
):
    """Analytical endpoints: total reviews, success rate, and total findings."""
    
    query = select(ReviewLog)
    if repo_full_name:
        query = query.where(ReviewLog.repo_full_name == repo_full_name)
        
    result = await db.execute(query)
    logs = result.scalars().all()
    
    total_reviews = len(logs)
    successful_reviews = sum(1 for log in logs if log.status == "SUCCESS")
    total_findings = sum(log.findings_count or 0 for log in logs)
    
    return {
        "total_reviews": total_reviews,
        "successful_reviews": successful_reviews,
        "failed_reviews": total_reviews - successful_reviews,
        "success_rate_percent": round((successful_reviews / total_reviews * 100), 2) if total_reviews > 0 else 0,
        "total_bugs_detected": total_findings
    }