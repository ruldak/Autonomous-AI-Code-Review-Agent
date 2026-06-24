import asyncio
import redis.asyncio as aioredis
from app.core.celery_app import celery_app
from app.config import settings
from app.utils.logger import setup_logger, logger
from app.services.github_service import fetch_pr_files
from app.services.ast_service import parse_code
from app.services.review_service import post_github_review
from app.services.security_scanner import scan_code_security
from app.agents.review_agent import analyze_code_with_ai
from app.models.review_models import ReviewResult

async def _run_review(pr_api_url: str, repo_full_name: str, pr_number: int, commit_sha: str, token: str):
    """Fungsi async inti yang menjalankan alur review."""
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    
    try:
        changed_files = await fetch_pr_files(pr_api_url, token)
        logger.info("Fetched changed files", count=len(changed_files), pr_number=pr_number)
        
        ai_results = {}
        files_valid_lines = {}
        
        for file in changed_files:
            valid_lines = file.get("valid_lines", [])
            code_bytes = file["raw_content"].encode('utf-8')
            ast_result = parse_code(file["filename"], code_bytes)
            
            if ast_result.get("supported"):
                ai_result = await analyze_code_with_ai(
                    filename=file["filename"],
                    code=file["raw_content"],
                    ast_info=ast_result
                )
                
                security_findings = scan_code_security(file["filename"], file["raw_content"])
                combined_findings = ai_result.findings + security_findings
                
                ai_results[file["filename"]] = ReviewResult(
                    findings=combined_findings,
                    summary=ai_result.summary
                )
                files_valid_lines[file["filename"]] = valid_lines
                
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
        logger.error("Review process failed", error=str(e))
    finally:
        await redis.close()

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_pr_review_task(self, pr_api_url: str, repo_full_name: str, pr_number: int, commit_sha: str, token: str):
    """Celery Task Wrapper."""
    setup_logger()
    logger.info("Starting Celery task", pr_number=pr_number, repo=repo_full_name)
    try:
        asyncio.run(_run_review(pr_api_url, repo_full_name, pr_number, commit_sha, token))
    except Exception as exc:
        logger.error("Celery task crashed, retrying...", error=str(exc))
        raise self.retry(exc=exc)