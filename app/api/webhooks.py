from fastapi import APIRouter, Request, Depends, HTTPException
from app.core.security import verify_github_webhook_signature
from app.models.github_models import WebhookPayload
from app.services.github_service import fetch_pr_files, fetch_pr_diff, cache_repo_metadata
from app.utils.logger import logger
import json
from app.services.ast_service import parse_code
from app.core.redis_client import get_redis
from app.agents.review_agent import analyze_code_with_ai
from app.services.review_service import post_github_review
from app.services.security_scanner import scan_code_security
from app.models.review_models import ReviewResult
from app.core.github_auth import get_installation_token
from app.db.session import async_session_maker
from app.db.models import Tenant
from sqlalchemy import select
from app.tasks.review_tasks import process_pr_review_task

router = APIRouter()

@router.post("/webhook", dependencies=[Depends(verify_github_webhook_signature)])
async def github_webhook(
    request: Request, 
    payload: WebhookPayload
):
    event = request.headers.get("x-github-event")
    logger.info(
        "Received GitHub webhook", 
        github_event=event,
        action=payload.action, 
        repo=payload.repository.full_name
    )

    if event == "ping":
        return {"message": "Pong! Webhook verified."}

    installation_id = payload.installation.id if payload.installation else None
    if not installation_id:
        raise HTTPException(status_code=400, detail="Missing installation ID in webhook")

    if event == "pull_request" and payload.action in ["opened", "synchronize", "reopened"]:
        pr = payload.pull_request
        if not pr:
            raise HTTPException(status_code=400, detail="Missing pull_request data")

        async with async_session_maker() as session:
            stmt = select(Tenant).where(Tenant.github_installation_id == installation_id)
            result = await session.execute(stmt)
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                tenant = Tenant(github_installation_id=installation_id)
                session.add(tenant)
                await session.commit()
                logger.info("Registered new SaaS tenant", installation_id=installation_id)

        token = await get_installation_token(installation_id)
            
        logger.info(
            "Triggering review for PR", 
            pr_number=pr.number, 
            repo=payload.repository.full_name
        )
        
        # Cache metadata repo ke Redis
        await cache_repo_metadata(
            payload.repository.full_name, 
            payload.repository.id, 
            payload.repository.owner.login
        )
        
        process_pr_review_task.delay(
            pr.url, 
            payload.repository.full_name, 
            pr.number,
            pr.head.sha,
            token,
            installation_id
        )
        
        return {"message": "Review task queued successfully"}

    return {"message": "Event ignored by agent"}