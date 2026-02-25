#!/usr/bin/env python3
"""
Evolution Check Script - Trigger automatic evolutions
Run via cron daily

Checks all pets and evolves if:
- Level threshold met (3, 10, 25, 50)
- Care score thresholds met (for path selection)
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.pet_storage import PetStorage
from core.evolution import EvolutionSystem

def run_evolution_check():
    """Check and apply evolutions"""
    storage = PetStorage()
    all_pets = storage.get_all_pets()
    
    if not all_pets:
        print("No pets to check")
        return
    
    evolved_count = 0
    for pet in all_pets:
        # Check if evolution should happen
        event = EvolutionSystem.evolve_pet(pet)
        
        if event:
            storage.save_pet(pet)
            evolved_count += 1
            
            # Log evolution
            path_str = f" ({event.path.value})" if event.path else ""
            print(f"✨ {event.pet_name} evolved to {event.new_stage.value}{path_str}")
            
            # Log new abilities
            if hasattr(event, 'new_abilities') and event.new_abilities:
                for ability in event.new_abilities:
                    print(f"   ✦ Learned: {ability}")
    
    print(f"✓ Checked {len(all_pets)} pets, {evolved_count} evolved")

if __name__ == "__main__":
    try:
        run_evolution_check()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
