import json
import os
from jsonschema import validate, ValidationError
from pathlib import Path

from config import settings

# Path to the JSON schema for LFG entries
_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "lfg_schema.json"

def _load_schema():
    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

_SCHEMA = _load_schema()

def _lfg_file_path() -> Path:
    return Path(settings.lfg_path)

def load_lfg() -> dict:
    """Load the entire LFG database and validate against the schema.
    Returns a dictionary mapping entry keys to entry objects.
    Raises ValueError if validation fails.
    """
    path = _lfg_file_path()
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    try:
        validate(instance=data, schema=_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"LFG data validation error: {e.message}")
    return data

def save_lfg(data: dict) -> None:
    """Write the LFG data back to disk after validation."""
    validate(instance=data, schema=_SCHEMA)
    path = _lfg_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_entry(key: str, entry: dict) -> None:
    """Add a new LFG entry after validating the entry.
    Raises ValueError if the entry does not conform to the schema.
    """
    data = load_lfg()
    data[key] = entry
    save_lfg(data)

def remove_entry(key: str) -> None:
    """Remove an LFG entry by key. No error if key does not exist."""
    data = load_lfg()
    data.pop(key, None)
    save_lfg(data)
