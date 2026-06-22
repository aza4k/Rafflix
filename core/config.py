import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    BOT_TOKEN: str
    WEBHOOK_URL: str
    WEBAPP_URL: str
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    ADMIN_IDS_STR: str = ""
    CHANNEL_ID: int
    BOT_USERNAME: str = "RafflixBot"

    @property
    def ADMIN_IDS(self) -> List[int]:
        if not self.ADMIN_IDS_STR:
            return []
        return [int(id_.strip()) for id_ in self.ADMIN_IDS_STR.split(",") if id_.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings(_env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
