from github import Github, Auth
import httpx
import json
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import settings
from app.core.redis_client import get_redis
from app.utils.logger import logger
import re

def extract_valid_lines(patch: str) -> set[int]:
    """Extracting the line numbers in the new file (RIGHT side) that actually appear in the diff."""
    valid_lines = set()
    if not patch:
        return valid_lines
        
    lines = patch.split('\n')
    current_new_line = 0
    
    for line in lines:
        header_match = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', line)
        if header_match:
            current_new_line = int(header_match.group(1))
            continue
            
        if line.startswith('+') and not line.startswith('+++'):
            valid_lines.add(current_new_line)
            current_new_line += 1
        elif line.startswith('-') and not line.startswith('---'):
            pass
        elif not line.startswith('\\'):
            current_new_line += 1
            
    return valid_lines

def get_github_client() -> Github:
    # Using PAT for development.
    if settings.GITHUB_PAT:
        logger.info("Using GitHub Personal Access Token")
        return Github(auth=Auth.Token(settings.GITHUB_PAT))
    
    logger.warning("No GitHub PAT configured. Using unauthenticated client (Rate limits apply).")
    return Github()

async def cache_repo_metadata(repo_full_name: str, repo_id: int, owner: str):
    """Store repository metadata in Redis for fast access."""
    redis = get_redis()
    if not redis: return
    
    cache_key = f"repo_metadata:{repo_full_name}"
    metadata = {
        "repo_id": repo_id,
        "owner": owner,
        "last_webhook": time.time()
    }

    await redis.setex(cache_key, 86400, json.dumps(metadata))
    logger.debug("Cached repo metadata in Redis", repo=repo_full_name)

async def fetch_pr_files(pr_api_url: str, token: str) -> list[dict]:
    """Fetch the list of changed files in the PR, along with their raw content, via the Contents API."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.GITHUB_PAT:
        headers["Authorization"] = f"token {token}"

    files_url = f"{pr_api_url}/files"
    
    async with httpx.AsyncClient() as client:
        logger.info("Fetching PR changed files", url=files_url)
        response = await client.get(files_url, headers=headers, timeout=30.0)
        response.raise_for_status()
        files_data = response.json()
        
        processed_files = []
        for file in files_data:
            if file["status"] in ["added", "modified", "renamed"]:
                contents_url = file.get("contents_url")
                if contents_url:
                    raw_headers = headers.copy()
                    raw_headers["Accept"] = "application/vnd.github.raw+json"
                    
                    raw_res = await client.get(contents_url, headers=raw_headers, timeout=30.0)
                    raw_res.raise_for_status()

                    patch = file.get("patch", "")
                    valid_lines = extract_valid_lines(patch)
                    
                    processed_files.append({
                        "filename": file["filename"],
                        "status": file["status"],
                        "additions": file["additions"],
                        "deletions": file["deletions"],
                        "raw_content": raw_res.text,
                        "valid_lines": list(valid_lines)
                    })
        return processed_files