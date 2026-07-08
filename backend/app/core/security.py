import hmac
import hashlib
from fastapi import Request, HTTPException, status
from app.config import settings
from app.utils.logger import logger

async def verify_github_webhook_signature(request: Request):
    if not settings.GITHUB_WEBHOOK_SECRET:
        logger.warning("GITHUB_WEBHOOK_SECRET not set. Skipping verification (Dev mode).")
        return
        
    signature_header = request.headers.get("x-hub-signature-256")
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing signature header"
        )

    body = await request.body()
    hash_object = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode('utf-8'), 
        msg=body, 
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()

    if not hmac.compare_digest(expected_signature, signature_header):
        logger.warning("Invalid webhook signature received")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid signature"
        )