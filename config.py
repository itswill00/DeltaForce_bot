import os
import yaml
import json
from typing import List, Union, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # All defaults are now placeholders or strictly controlled
    bot_token: str
    local_db_path: str = "localdb.json"
    owner_id: int = 0
    admin_ids: Any = []
    log_group_id: int = 0
    loadout_path: str = "data/loadout.json"
    auto_delete_delay: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: Any) -> List[int]:
        if isinstance(v, str):
            if not v.strip(): return []
            try:
                data = json.loads(v)
                if isinstance(data, list): return [int(x) for x in data]
            except (json.JSONDecodeError, ValueError): pass
            return [int(x.strip()) for x in v.split(",") if x.strip().isdigit()]
        return v or []

# Force validation: This will raise an error if BOT_TOKEN is missing from .env
settings = Settings()
