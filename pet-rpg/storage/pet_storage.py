"""
Pet Storage - Persistence layer for MoltPet data

Handles:
- Loading/saving pets from JSON
- Batch operations
- Migration/backup
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import shutil

from ..core.pet import MoltPet


class PetStorage:
    """Manages persistent pet storage"""
    
    def __init__(self, storage_dir: str = "~/.openclaw/pets"):
        """Initialize storage with directory path"""
        self.storage_dir = Path(storage_dir).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
    
    def save_pet(self, pet: MoltPet) -> None:
        """Save a pet to storage"""
        pet_file = self.storage_dir / f"{pet.pet_id}.json"
        
        # Write pet data
        pet_data = pet.to_dict()
        with open(pet_file, 'w') as f:
            json.dump(pet_data, f, indent=2)
        
        # Update index
        self._update_index(pet.pet_id, pet.owner_id, pet.name)
    
    def load_pet(self, pet_id: str) -> Optional[MoltPet]:
        """Load a pet from storage by ID"""
        pet_file = self.storage_dir / f"{pet_id}.json"
        
        if not pet_file.exists():
            return None
        
        with open(pet_file, 'r') as f:
            pet_data = json.load(f)
        
        return MoltPet.from_dict(pet_data)
    
    def pet_exists(self, pet_id: str) -> bool:
        """Check if a pet exists"""
        pet_file = self.storage_dir / f"{pet_id}.json"
        return pet_file.exists()
    
    def get_pets_by_owner(self, owner_id: str) -> List[MoltPet]:
        """Get all pets owned by an agent"""
        pets = []
        index = self._load_index()
        
        for pet_id, pet_info in index.items():
            if pet_info.get("owner_id") == owner_id:
                pet = self.load_pet(pet_id)
                if pet:
                    pets.append(pet)
        
        return pets
    
    def get_all_pets(self) -> List[MoltPet]:
        """Get all pets in storage"""
        pets = []
        index = self._load_index()
        
        for pet_id in index.keys():
            pet = self.load_pet(pet_id)
            if pet:
                pets.append(pet)
        
        return pets
    
    def delete_pet(self, pet_id: str) -> bool:
        """Delete a pet from storage"""
        pet_file = self.storage_dir / f"{pet_id}.json"
        
        if pet_file.exists():
            pet_file.unlink()
            self._remove_from_index(pet_id)
            return True
        
        return False
    
    def backup_pets(self, backup_dir: str = None) -> str:
        """Backup all pet data"""
        if backup_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = str(self.storage_dir / f"backups" / f"backup_{timestamp}")
        
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copy all pet files
        for pet_file in self.storage_dir.glob("*.json"):
            if pet_file.name != "index.json":
                shutil.copy(pet_file, backup_path / pet_file.name)
        
        # Copy index
        if self.index_file.exists():
            shutil.copy(self.index_file, backup_path / "index.json")
        
        return str(backup_path)
    
    def _load_index(self) -> Dict:
        """Load the index file"""
        if not self.index_file.exists():
            return {}
        
        with open(self.index_file, 'r') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict) -> None:
        """Save the index file"""
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _update_index(self, pet_id: str, owner_id: str, pet_name: str) -> None:
        """Update the index with a pet entry"""
        index = self._load_index()
        index[pet_id] = {
            "owner_id": owner_id,
            "name": pet_name,
            "updated_at": datetime.now().isoformat()
        }
        self._save_index(index)
    
    def _remove_from_index(self, pet_id: str) -> None:
        """Remove a pet from the index"""
        index = self._load_index()
        if pet_id in index:
            del index[pet_id]
            self._save_index(index)


# Global storage instance
_storage = None


def get_storage(storage_dir: str = None) -> PetStorage:
    """Get or create global storage instance"""
    global _storage
    if _storage is None:
        if storage_dir is None:
            storage_dir = "~/.openclaw/pets"
        _storage = PetStorage(storage_dir)
    return _storage


def save_pet(pet: MoltPet) -> None:
    """Convenience function to save pet"""
    get_storage().save_pet(pet)


def load_pet(pet_id: str) -> Optional[MoltPet]:
    """Convenience function to load pet"""
    return get_storage().load_pet(pet_id)


def pet_exists(pet_id: str) -> bool:
    """Convenience function to check pet existence"""
    return get_storage().pet_exists(pet_id)


def get_pets_by_owner(owner_id: str) -> List[MoltPet]:
    """Convenience function to get owner's pets"""
    return get_storage().get_pets_by_owner(owner_id)


def get_all_pets() -> List[MoltPet]:
    """Convenience function to get all pets"""
    return get_storage().get_all_pets()


def delete_pet(pet_id: str) -> bool:
    """Convenience function to delete pet"""
    return get_storage().delete_pet(pet_id)


def backup_pets(backup_dir: str = None) -> str:
    """Convenience function to backup pets"""
    return get_storage().backup_pets(backup_dir)
