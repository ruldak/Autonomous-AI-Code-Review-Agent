import httpx
from app.config import settings
from app.models.review_models import ReviewResult
from app.utils.logger import logger

async def post_general_pr_comment(repo_full_name: str, pr_number: int, body: str):
    """Fallback: Memposting komentar umum di kolom diskusi PR (menggunakan Issues API)."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {settings.GITHUB_PAT}"
    }
    
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json={"body": body}, timeout=30.0)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error("Failed to post general PR comment", error=e.response.text)

async def post_github_review(
    repo_full_name: str, 
    pr_number: int, 
    commit_sha: str, 
    ai_results: dict[str, ReviewResult],
    files_valid_lines: dict[str, list[int]]
):
    """Membuat dan memposting Review ke GitHub PR dengan mekanisme Fallback."""
    if not settings.GITHUB_PAT:
        logger.warning("GITHUB_PAT not set. Cannot post review to GitHub.")
        return

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {settings.GITHUB_PAT}"
    }
    
    comments = []
    overall_summary = []
    
    for filename, result in ai_results.items():
        valid_lines_for_file = set(files_valid_lines.get(filename, []))

        if result.findings:
            file_summary = [f"### {filename}\n{result.summary}"]
            for finding in result.findings:
                if finding.line and finding.line in valid_lines_for_file:
                    comments.append({
                        "path": filename,
                        "line": finding.line or 1,
                        "side": "RIGHT",
                        "body": f"**[{finding.severity.value.upper()}] {finding.category.value}**\n\n"
                                f"**Message:** {finding.message}\n\n"
                                f"**Explanation:** {finding.explanation}"
                    })
                else:
                    file_summary.append(f"- **[{finding.severity.value.upper()}] {finding.category.value}** (Line {finding.line}): {finding.message}")
            overall_summary.extend(file_summary)
        else:
            overall_summary.append(f"### {filename}\n✅ No issues found.")

    review_body = "## 🤖 AI Code Review Summary\n\n" + "\n\n".join(overall_summary)
    
    payload = {
        "commit_id": commit_sha,
        "body": review_body,
        "event": "COMMENT",
        "comments": comments
    }
    
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/reviews"
    
    async with httpx.AsyncClient() as client:
        try:
            logger.info("Attempting to post inline review to GitHub", url=url)
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            logger.info("Successfully posted inline GitHub review", pr_number=pr_number)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 422:
                logger.warning(
                    "Inline review rejected by GitHub (Line not in diff). Falling back to general comments.", 
                    error=e.response.text
                )
                
                await post_general_pr_comment(repo_full_name, pr_number, review_body)
                
                for c in comments:
                    fallback_body = f"**File:** `{c['path']}` (Line {c['line']})\n\n{c['body']}"
                    await post_general_pr_comment(repo_full_name, pr_number, fallback_body)
                    
                logger.info("Successfully posted fallback comments to PR", pr_number=pr_number)
            else:
                logger.error(
                    "Failed to post GitHub review", 
                    error=e.response.text, 
                    status_code=e.response.status_code
                )