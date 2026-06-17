from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # GitHub
    GITHUB_APP_ID: str = ""
    GITHUB_PRIVATE_KEY_PATH: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    GITHUB_PAT: str = ""
    
    # Groq
    GROQ_API_KEY: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()