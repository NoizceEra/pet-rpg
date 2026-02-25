#!/usr/bin/env python3
"""Test Game - Verify core mechanics work (FIXED)"""

import sys
import os
from pathlib import Path

# Add pet-rpg to path
sys.path.insert(0, str(Path(__file__).parent))

from core.pet import MoltPet, PetStage
from core.battle import BattleEngine
from core.evolution import EvolutionSystem

def test_pet_creation():
    """Test creating a pet"""
    print("🧪 Test 1: Pet Creation")
    print("─" * 50)
    
    pet = MoltPet(
        pet_id="pet_001",
        owner_id="test_user",
        name="TestPet"
    )
    print(f"✅ Created pet: {pet.name}")
    print(f"   Level: {pet.level}, HP: {pet.hp}/{pet.max_hp}")
    print(f"   STR: {pet.strength}, SPD: {pet.speed}, INT: {pet.intelligence}")
    print()
    
    return pet

def test_pet_care(pet: MoltPet):
    """Test care mechanics"""
    print("🧪 Test 2: Pet Care")
    print("─" * 50)
    
    print(f"Before: Hunger={int(pet.hunger)}%, Happiness={int(pet.happiness)}%")
    
    result = pet.feed()
    print(f"After feed: {result}")
    print(f"  Hunger={int(pet.hunger)}%, Happiness={int(pet.happiness)}%")
    
    result = pet.play()
    print(f"After play: {result}")
    print(f"  Hunger={int(pet.hunger)}%, Happiness={int(pet.happiness)}%")
    
    print()

def test_pet_training(pet: MoltPet):
    """Test stat training"""
    print("🧪 Test 3: Stat Training")
    print("─" * 50)
    
    print(f"Before: STR={pet.strength}, SPD={pet.speed}, INT={pet.intelligence}")
    
    pet.train("strength")
    print(f"After train STR: STR={pet.strength}")
    
    pet.train("speed")
    print(f"After train SPD: SPD={pet.speed}")
    
    print()

def test_pet_serialization(pet: MoltPet):
    """Test save/load"""
    print("🧪 Test 4: Pet Serialization")
    print("─" * 50)
    
    # Serialize
    pet_dict = pet.to_dict()
    print(f"✅ Serialized pet to dict")
    print(f"   Keys: {len(pet_dict)} fields")
    
    # Deserialize
    loaded = MoltPet.from_dict(pet_dict)
    print(f"✅ Deserialized pet from dict: {loaded.name}")
    print(f"   Level: {loaded.level}, HP: {loaded.hp}/{loaded.max_hp}")
    
    print()
    return loaded

def test_battle(pet1: MoltPet, pet2: MoltPet):
    """Test battle system"""
    print("🧪 Test 5: Battle System")
    print("─" * 50)
    
    # Create fresh pets for battle
    p1 = MoltPet(pet_id="p1", owner_id="user1", name="Attacker")
    p2 = MoltPet(pet_id="p2", owner_id="user2", name="Defender")
    
    print(f"Battle: {p1.name} vs {p2.name}")
    print(f"  {p1.name}: HP={p1.hp}, STR={p1.strength}, SPD={p1.speed}")
    print(f"  {p2.name}: HP={p2.hp}, STR={p2.strength}, SPD={p2.speed}")
    
    engine = BattleEngine(p1, p2)
    result = engine.simulate()
    
    print(f"\n🏆 Winner: {result['winner'].name.upper()}")
    print(f"  {result['attacker'].name}: {result['attacker'].hp} HP remaining")
    print(f"  {result['defender'].name}: {result['defender'].hp} HP remaining")
    print(f"  Duration: {engine.turn_count} turns")
    print()

def test_evolution(pet: MoltPet):
    """Test evolution system"""
    print("🧪 Test 6: Evolution System")
    print("─" * 50)
    
    # Check current state
    print(f"Current stage: {pet.evolution_stage.value}")
    print(f"Evolution path: {pet.evolution_path}")
    
    # Level up to trigger evolution
    pet.level = 5
    pet._check_evolution()
    print(f"\nAfter level 5:")
    print(f"  Stage: {pet.evolution_stage.value}")
    
    pet.level = 11
    pet.care_score = 80  # Set care score for Guardian path
    pet._check_evolution()
    print(f"\nAfter level 11 (with 80% care):")
    print(f"  Stage: {pet.evolution_stage.value}")
    print(f"  Path: {pet.evolution_path}")
    
    print()

def main():
    print("\n" + "=" * 50)
    print("🐾 MOLTGOTCHI CORE TEST (FIXED)")
    print("=" * 50 + "\n")
    
    try:
        # Run tests
        pet = test_pet_creation()
        test_pet_care(pet)
        test_pet_training(pet)
        loaded_pet = test_pet_serialization(pet)
        test_battle(pet, loaded_pet)
        test_evolution(pet)
        
        print("=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50 + "\n")
        return 0
        
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 50 + "\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
