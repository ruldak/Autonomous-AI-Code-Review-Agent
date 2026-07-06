import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
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
from app.db.models import Tenant, ReviewLog
import dataclasses

def serialize_finding(f):
    """
    Helper to safely serialize Finding objects into native Python dictionaries.
    Handles Pydantic V1/V2, standard dataclasses, and Enums.
    """
    if hasattr(f, "model_dump"):
        return f.model_dump(mode="json")
    elif hasattr(f, "dict"):
        return f.dict()
    elif dataclasses.is_dataclass(f):
        return dataclasses.asdict(f)
    elif isinstance(f, dict):
        return f
    else:
        return str(f)

async def _run_review(pr_api_url: str, repo_full_name: str, pr_number: int, commit_sha: str, token: str, installation_id: int):
    """The core async function that executes the review workflow."""
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    status = "SUCCESS"
    total_findings = 0
    ai_results = {}
    
    try:
        changed_files = await fetch_pr_files(pr_api_url, token)
        logger.info("Fetched changed files", count=len(changed_files), pr_number=pr_number)
        
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

        for res in ai_results.values():
            total_findings += len(res.findings)
                
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

        try:
            engine = create_async_engine(settings.DATABASE_URL, echo=False)
            local_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            
            async with local_session_maker() as session:
                async with session.begin():
                    stmt = select(Tenant).where(Tenant.github_installation_id == installation_id)
                    result = await session.execute(stmt)
                    tenant = result.scalar_one_or_none()
                    
                    if tenant:
                        log = ReviewLog(
                            tenant_id=tenant.id,
                            repo_full_name=repo_full_name,
                            pr_number=pr_number,
                            status=status,
                            findings_count=total_findings,
                            ai_metadata={"model": "openai/gpt-oss-120b", "engine": "groq", "findings": serialize_finding(combined_findings)}
                        )
                        session.add(log)
                        logger.info("Saved review log", status=status, findings=total_findings)
            
            await engine.dispose()
        except Exception as db_err:
            logger.error("Failed to save review log", error=str(db_err))

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_pr_review_task(self, pr_api_url: str, repo_full_name: str, pr_number: int, commit_sha: str, token: str, installation_id: int):
    """Celery Task Wrapper."""
    setup_logger()
    logger.info("Starting Celery task", pr_number=pr_number, repo=repo_full_name)
    try:
        asyncio.run(_run_review(pr_api_url, repo_full_name, pr_number, commit_sha, token, installation_id))
    except Exception as exc:
        logger.error("Celery task crashed, retrying...", error=str(exc))
        raise self.retry(exc=exc)