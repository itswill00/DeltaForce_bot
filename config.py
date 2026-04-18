import os
import json
from typing import List, Union, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Explicitly load .env from the current working directory
load_dotenv()

class Settings(BaseSettings):
    bot_token: str
    local_db_path: str = "localdb.json"
    owner_id: int = 0
    admin_ids: Any = []
    log_group_id: int = 0
    loadout_path: str = "data/loadout.json"
    auto_delete_delay: int = 60
    
    # Visual Banners (High Quality Assets)
    banner_main: str = "https://i.ibb.co.com/X4yDqC3G/IMG-20250419-WA0019.jpg"
    banner_profile: str = "https://i.ibb.co.com/X4yDqC3G/IMG-20250419-WA0019.jpg"
    banner_lfg: str = "https://i.ibb.co.com/X4yDqC3G/IMG-20250419-WA0019.jpg"
    banner_shop: str = "https://i.ibb.co.com/X4yDqC3G/IMG-20250419-WA0019.jpg"
    banner_intel: str = "https://i.ibb.co.com/X4yDqC3G/IMG-20250419-WA0019.jpg"

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

# Final validation
settings = Settings()
