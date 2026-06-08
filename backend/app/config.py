from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/jobapply"

    gemini_api_key: str = ""
    gemini_scoring_model: str = "gemini-1.5-flash"
    gemini_writing_model: str = "gemini-1.5-pro"
    cover_letter_score_threshold: int = 60

    apify_token: str = ""
    jsearch_api_key: str = ""

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    server_host: str = "0.0.0.0"
    server_port: int = 8000
    frontend_url: str = "http://localhost:5173"


settings = Settings()
