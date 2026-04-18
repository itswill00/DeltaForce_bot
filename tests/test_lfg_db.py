import pytest
import json
import os
from database.lfg_db import LFGDB
from jsonschema import ValidationError

@pytest.fixture
def temp_lfg_db(tmp_path):
    db_file = tmp_path / "test_lfg.json"
    # Create empty db
    with open(db_file, "w") as f:
        json.dump({}, f)
    
    from config import settings
    original_path = settings.lfg_path
    settings.lfg_path = str(db_file)
    
    db = LFGDB()
    yield db
    
    settings.lfg_path = original_path

@pytest.mark.asyncio
async def test_lfg_validation_success(temp_lfg_db):
    session_id = "test_123"
    session_data = {
        "host_id": 123,
        "host_name": "TestHost",
        "players": [123],
        "max_players": 4,
        "status": "open",
        "timestamp": 123456789.0
    }
    await temp_lfg_db.update_session(session_id, session_data)
    
    loaded = await temp_lfg_db.get_session(session_id)
    assert loaded["host_name"] == "TestHost"

@pytest.mark.asyncio
async def test_lfg_validation_failure(temp_lfg_db):
    session_id = "test_fail"
    # Missing required field 'status'
    session_data = {
        "host_id": 123,
        "host_name": "TestHost",
        "players": [123],
        "max_players": 4,
        "timestamp": 123456789.0
    }
    with pytest.raises(ValueError, match="Invalid LFG data"):
        await temp_lfg_db.update_session(session_id, session_data)
