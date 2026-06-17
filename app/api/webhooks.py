from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
from app.core.security import verify_github_webhook_signature
from app.models.github_models import WebhookPayload
from app.services.github_service import fetch_pr_diff, cache_repo_metadata
from app.utils.logger import logger

router = APIRouter()

@router.post("/webhook", dependencies=[Depends(verify_github_webhook_signature)])
async def github_webhook(
    request: Request, 
    payload: WebhookPayload, 
    background_tasks: BackgroundTasks
):
    event = request.headers.get("x-github-event")
    logger.info(
        "Received GitHub webhook", 
        github_event=event,
        action=payload.action, 
        repo=payload.repository.full_name
    )

    # GitHub selalu mengirim event 'ping' saat webhook pertama kali dibuat
    if event == "ping":
        return {"message": "Pong! Webhook verified."}

    # Kita hanya peduli pada PR yang baru dibuat, di-update, atau di-reopen
    if event == "pull_request" and payload.action in ["opened", "synchronize", "reopened"]:
        pr = payload.pull_request
        if not pr:
            raise HTTPException(status_code=400, detail="Missing pull_request data")
            
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
        
        # Proses diff di background agar webhook langsung response 200 OK ke GitHub
        background_tasks.add_task(
            process_pr_review, 
            pr.url,
            payload.repository.full_name, 
            pr.number
        )
        
        return {"message": "Review task queued successfully"}

    return {"message": "Event ignored by agent"}

async def process_pr_review(api_url: str, repo_full_name: str, pr_number: int):
    """Background task untuk memproses diff (Akan terhubung ke AST & AI di Phase 3 & 4)"""
    try:
        diff_content = await fetch_pr_diff(api_url)
        lines_count = len(diff_content.splitlines())
        
        logger.info(
            "Successfully fetched and processed PR diff", 
            repo=repo_full_name, 
            pr_number=pr_number, 
            diff_lines=lines_count
        )
        # TODO: Phase 3 - Kirim diff_content ke Tree-sitter AST Parser
        # TODO: Phase 4 - Kirim hasil AST ke LangChain Agent
        
    except Exception as e:
        logger.error("Failed to process PR review", error=str(e))