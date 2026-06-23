from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
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
        
        # Proses diff di background agar webhook langsung response 200 OK ke GitHub
        background_tasks.add_task(
            process_pr_review, 
            pr.url,
            payload.repository.full_name, 
            pr.number,
            pr.head.sha,
            token
        )
        
        return {"message": "Review task queued successfully"}

    return {"message": "Event ignored by agent"}

async def process_pr_review(pr_api_url: str, repo_full_name: str, pr_number: int, commit_sha: str, token: str):
    """Background task untuk memproses AST dan AI Analysis."""
    try:
        changed_files = await fetch_pr_files(pr_api_url, token)
        logger.info("Fetched changed files", count=len(changed_files), pr_number=pr_number)
        
        redis = get_redis()
        ai_results = {}
        files_valid_lines = {}

        for file in changed_files:
            code_bytes = file["raw_content"].encode('utf-8')
            ast_result = parse_code(file["filename"], code_bytes)
            
            if ast_result.get("supported"):
                logger.info("AST Parsed Successfully", filename=file["filename"])
                
                # Cache AST
                if redis:
                    cache_key = f"ast:{repo_full_name}:{file['filename']}"
                    await redis.setex(cache_key, 3600, json.dumps(ast_result))
                
                # --- PHASE 4: AI ANALYSIS ---
                ai_result = await analyze_code_with_ai(
                    filename=file["filename"],
                    code=file["raw_content"],
                    ast_info=ast_result
                )

                security_findings = scan_code_security(file["filename"], file["raw_content"])

                combined_findings = ai_result.findings + security_findings
                final_result = ReviewResult(
                    findings=combined_findings,
                    summary=ai_result.summary
                )

                ai_results[file["filename"]] = final_result
                files_valid_lines[file["filename"]] = file.get("valid_lines", [])
                
                # Cache hasil AI ke Redis (Akan dipakai di Phase 5 untuk post comment ke GitHub)
                if redis:
                    ai_cache_key = f"ai_review:{repo_full_name}:{pr_number}:{file['filename']}"
                    await redis.setex(ai_cache_key, 86400, ai_result.model_dump_json())
                    
                # Log temuan AI ke terminal
                if ai_result.findings:
                    for finding in ai_result.findings:
                        logger.warning(
                            "AI Finding Detected",
                            filename=file["filename"],
                            severity=finding.severity.value,
                            category=finding.category.value,
                            line=finding.line,
                            message=finding.message
                        )
                else:
                    logger.info("No issues found by AI", filename=file["filename"])
                    
            else:
                logger.debug("Skipped AST & AI", filename=file["filename"], reason=ast_result.get("reason"))

        if ai_results:
            await post_github_review(
                repo_full_name=repo_full_name,
                pr_number=pr_number,
                commit_sha=commit_sha,
                ai_results=ai_results,
                files_valid_lines=files_valid_lines,
                token=token
            )
                
    except Exception as e:
        logger.error("Failed to process PR review", error=str(e))