"""Battle Log Storage"""

import os
import json
from pathlib import Path
from datetime import datetime
import uuid

BATTLES_DIR = Path.home() / ".openclaw" / "battles"
BATTLES_DIR.mkdir(parents=True, exist_ok=True)

def save_battle(result: dict) -> str:
    """Save a battle result, return battle_id"""
    battle_id = str(uuid.uuid4())[:8]
    
    battle_record = {
        "battle_id": battle_id,
        "timestamp": datetime.now().isoformat(),
        **result
    }
    
    try:
        path = BATTLES_DIR / f"{battle_id}.json"
        with open(path, 'w') as f:
            json.dump(battle_record, f, indent=2)
        return battle_id
    except Exception as e:
        print(f"Error saving battle: {e}")
        return None

def get_battle(battle_id: str) -> dict:
    """Load a battle record"""
    try:
        path = BATTLES_DIR / f"{battle_id}.json"
        if not path.exists():
            return None
        
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading battle: {e}")
        return None

def get_battles_for_owner(owner_id: str, limit: int = 10) -> list[dict]:
    """Get recent battles for an owner"""
    battles = []
    for battle_file in sorted(BATTLES_DIR.glob("*.json"), reverse=True)[:limit * 2]:
        try:
            with open(battle_file, 'r') as f:
                data = json.load(f)
            
            if data['attacker']['owner_id'] == owner_id or data['defender']['owner_id'] == owner_id:
                battles.append(data)
                if len(battles) >= limit:
                    break
        except:
            pass
    
    return battles
