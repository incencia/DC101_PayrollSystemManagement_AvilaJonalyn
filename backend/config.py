import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).resolve().parent / 'payroll.db'}",
    )
    secret_key: str = os.getenv("SECRET_KEY", "payroll-dev-secret")
    page_size: int = int(os.getenv("PAGE_SIZE", "10"))
    flask_env: str = os.getenv("FLASK_ENV", "development")


settings = Settings()

