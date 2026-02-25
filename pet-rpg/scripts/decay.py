#!/usr/bin/env python3
"""
Decay Script - Time-based pet deterioration
Run via cron every 4 hours

Applies:
- Hunger degradation (6% per hour)
- Happiness degradation (4% per hour)
- Health damage if starving (<25% hunger)
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.pet_storage import PetStorage

def run_decay():
    """Apply time decay to all pets"""
    storage = PetStorage()
    all_pets = storage.get_all_pets()
    
    if not all_pets:
        print("No pets to decay")
        return
    
    decayed_count = 0
    for pet in all_pets:
        # Apply 4 hours of decay
        pet.apply_decay(hours_elapsed=4)
        storage.save_pet(pet)
        decayed_count += 1
        
        # Log if pet is in critical condition
        if pet.hunger < 25:
            print(f"⚠️  {pet.name} is starving! Hunger: {int(pet.hunger)}%")
        elif pet.happiness < 25:
            print(f"😢 {pet.name} is very unhappy. Happiness: {int(pet.happiness)}%")
    
    print(f"✓ Decayed {decayed_count} pets (4 hours elapsed)")

if __name__ == "__main__":
    try:
        run_decay()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
