
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name: str = "PeaOps"
    environment: str = "development"
    database_url: str = "sqlite:///./peaops.db"
    secret_key: str = "change-me"
    default_currency: str = "INR"
    access_token_minutes: int = 15
    allowed_origins: str = "http://localhost:5173"
    trust_proxy_headers: bool = False
    auto_create_schema: bool = True
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_tls: bool = True
    model_config = SettingsConfigDict(env_prefix="PEAOPS_", env_file=".env", extra="ignore")
settings = Settings()
