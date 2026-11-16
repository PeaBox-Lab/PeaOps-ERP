from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PeaOps"
    environment: str = "development"
    database_url: str = "sqlite:///./peaops.db"
    secret_key: str = "change-me"
    default_currency: str = "INR"
    model_config = SettingsConfigDict(env_prefix="PEAOPS_", env_file=".env", extra="ignore")


settings = Settings()
