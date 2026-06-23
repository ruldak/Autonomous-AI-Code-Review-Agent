import jwt
import time
import httpx
from pathlib import Path
from app.config import settings
from app.core.redis_client import get_redis
from app.utils.logger import logger

def generate_jwt() -> str:
    """Membuat JWT untuk autentikasi GitHub App."""
    now = int(time.time())
    payload = {
        "iat": now - 60,  # Issued at time (60 detik di masa lalu untuk antisipasi clock drift)
        "exp": now + (10 * 60),  # Expire dalam 10 menit (maksimal dari GitHub)
        "iss": settings.GITHUB_APP_ID
    }
    
    private_key_path = Path(settings.GITHUB_PRIVATE_KEY_PATH)
    if not private_key_path.exists():
        raise FileNotFoundError(f"Private key not found at {private_key_path}")
        
    private_key = private_key_path.read_text()
    
    # Sign JWT menggunakan algoritma RS256
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    return encoded_jwt

async def get_installation_token(installation_id: int) -> str:
    """Mendapatkan Installation Access Token (IAT) dengan caching Redis."""
    redis = get_redis()
    cache_key = f"github_token:{installation_id}"
    
    # Cek cache dulu
    if redis:
        cached_token = await redis.get(cache_key)
        if cached_token:
            logger.debug("Using cached installation token", installation_id=installation_id)
            return cached_token

    logger.info("Generating new installation token", installation_id=installation_id)
    jwt_token = generate_jwt()
    
    # Tukar JWT dengan Installation Token
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {jwt_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        token = data["token"]
        
        # Cache token selama 55 menit (Token asli berlaku 60 menit)
        if redis:
            await redis.setex(cache_key, 55 * 60, token)
            
        return token