"""
Battle Storage - Persistence layer for battle history

Handles:
- Saving battle results
- Loading battle history
- Leaderboard data
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class BattleStorage:
    """Manages persistent battle storage"""
    
    def __init__(self, storage_dir: str = "~/.openclaw/battles"):
        """Initialize storage with directory path"""
        self.storage_dir = Path(storage_dir).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_battle(self, battle_result: Dict) -> str:
        """
        Save a battle result
        Returns the battle ID
        """
        battle_id = f"battle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        battle_file = self.storage_dir / f"{battle_id}.json"
        
        # Format battle data for storage
        battle_data = {
            "battle_id": battle_id,
            "timestamp": datetime.now().isoformat(),
            "winner_name": battle_result.get("winner_name"),
            "winner_owner": battle_result.get("winner_owner"),
            "loser_name": battle_result.get("loser_name"),
            "loser_owner": battle_result.get("loser_owner"),
            "turns": battle_result.get("turns"),
            "winner_final_hp": battle_result.get("winner_final_hp"),
            "loser_final_hp": battle_result.get("loser_final_hp"),
            "xp_reward": battle_result.get("xp_reward"),
            "usdc_reward": battle_result.get("usdc_reward"),
            "wager": battle_result.get("wager"),
            "log": [
                {
                    "turn": turn.turn_number,
                    "actor": turn.actor_name,
                    "damage": turn.damage,
                    "is_crit": turn.is_crit,
                    "target_hp_before": turn.target_hp_before,
                    "target_hp_after": turn.target_hp_after,
                }
                for turn in battle_result.get("log", [])
            ]
        }
        
        with open(battle_file, 'w') as f:
            json.dump(battle_data, f, indent=2)
        
        return battle_id
    
    def load_battle(self, battle_id: str) -> Optional[Dict]:
        """Load a battle from storage by ID"""
        battle_file = self.storage_dir / f"{battle_id}.json"
        
        if not battle_file.exists():
            return None
        
        with open(battle_file, 'r') as f:
            return json.load(f)
    
    def get_battles_by_pet(self, pet_name: str, limit: int = 20) -> List[Dict]:
        """Get recent battles for a pet"""
        battles = []
        
        for battle_file in sorted(self.storage_dir.glob("*.json"), reverse=True):
            if len(battles) >= limit:
                break
            
            with open(battle_file, 'r') as f:
                battle = json.load(f)
            
            if battle.get("winner_name") == pet_name or battle.get("loser_name") == pet_name:
                battles.append(battle)
        
        return battles
    
    def get_battles_by_owner(self, owner_id: str, limit: int = 50) -> List[Dict]:
        """Get recent battles for an owner"""
        battles = []
        
        for battle_file in sorted(self.storage_dir.glob("*.json"), reverse=True):
            if len(battles) >= limit:
                break
            
            with open(battle_file, 'r') as f:
                battle = json.load(f)
            
            if battle.get("winner_owner") == owner_id or battle.get("loser_owner") == owner_id:
                battles.append(battle)
        
        return battles
    
    def get_all_battles(self, limit: int = 100) -> List[Dict]:
        """Get most recent battles"""
        battles = []
        
        for battle_file in sorted(self.storage_dir.glob("*.json"), reverse=True):
            if len(battles) >= limit:
                break
            
            with open(battle_file, 'r') as f:
                battles.append(json.load(f))
        
        return battles
    
    def get_head_to_head(self, pet1_name: str, pet2_name: str) -> Dict:
        """Get head-to-head record between two pets"""
        pet1_wins = 0
        pet2_wins = 0
        
        for battle_file in self.storage_dir.glob("*.json"):
            with open(battle_file, 'r') as f:
                battle = json.load(f)
            
            if (battle.get("winner_name") == pet1_name and 
                battle.get("loser_name") == pet2_name):
                pet1_wins += 1
            elif (battle.get("winner_name") == pet2_name and 
                  battle.get("loser_name") == pet1_name):
                pet2_wins += 1
        
        return {
            "pet1": pet1_name,
            "pet1_wins": pet1_wins,
            "pet2": pet2_name,
            "pet2_wins": pet2_wins,
            "total_battles": pet1_wins + pet2_wins,
        }


# Global storage instance
_storage = None


def get_storage(storage_dir: str = None) -> BattleStorage:
    """Get or create global storage instance"""
    global _storage
    if _storage is None:
        if storage_dir is None:
            storage_dir = "~/.openclaw/battles"
        _storage = BattleStorage(storage_dir)
    return _storage


def save_battle(battle_result: Dict) -> str:
    """Convenience function to save battle"""
    return get_storage().save_battle(battle_result)


def load_battle(battle_id: str) -> Optional[Dict]:
    """Convenience function to load battle"""
    return get_storage().load_battle(battle_id)


def get_battles_by_pet(pet_name: str, limit: int = 20) -> List[Dict]:
    """Convenience function to get pet's battles"""
    return get_storage().get_battles_by_pet(pet_name, limit)


def get_battles_by_owner(owner_id: str, limit: int = 50) -> List[Dict]:
    """Convenience function to get owner's battles"""
    return get_storage().get_battles_by_owner(owner_id, limit)


def get_all_battles(limit: int = 100) -> List[Dict]:
    """Convenience function to get all battles"""
    return get_storage().get_all_battles(limit)


def get_head_to_head(pet1_name: str, pet2_name: str) -> Dict:
    """Convenience function for head-to-head"""
    return get_storage().get_head_to_head(pet1_name, pet2_name)
