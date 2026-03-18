from pydantic_settings import BaseSettings
from urllib.parse import quote_plus


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database configuration
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Environment
    ENVIRONMENT: str = "development"

    # API Configuration
    API_TITLE: str = "Metadata Management Service"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = (
        "Production-grade metadata management and lineage tracking system"
    )

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def database_url(self) -> str:
        encoded_password = quote_plus(self.DB_PASSWORD)

        return (
        f"mysql+pymysql://{self.DB_USER}:{encoded_password}"
        f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()