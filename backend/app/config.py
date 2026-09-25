from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    llm_provider: str = "none"  # none | anthropic | openai | ollama
    llm_model: str = "claude-sonnet-5"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434/v1"

    database_url: str = f"sqlite:///{(BASE_DIR / 'autoflow.db').as_posix()}"
    checkpoint_db: str = str(BASE_DIR / "checkpoints.db")

    admin_token: str = "change-me-admin"
    cors_origins: str = "http://localhost:5173"
    seed_demo: bool = True
    auto_seed_workbook: bool = False

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def llm_enabled(self) -> bool:
        return self.llm_provider.lower() not in ("", "none", "off", "false")


@lru_cache
def get_settings() -> Settings:
    return Settings()
