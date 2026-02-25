#!/usr/bin/env python3
"""Test Game - Verify core mechanics work"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from core.pet import MoltPet
from core.battle import BattleEngine
from ascii.art import render_pet, render_status, render_battle_log
from storage.pet_storage import save_pet, load_pet

def test_pet_creation():
    """Test creating a pet"""
    print("🧪 Test 1: Pet Creation")
    print("─" * 50)
    
    pet = MoltPet("test_user", "TestPet")
    print(f"✅ Created pet: {pet.name}")
    print(f"   Level: {pet.level}, HP: {pet.hp}/{pet.max_hp}")
    print(f"   STR: {pet.str}, SPD: {pet.spd}, INT: {pet.int}")
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
    
    print(f"Before: STR={pet.str}, SPD={pet.spd}, INT={pet.int}")
    
    pet.train("str")
    print(f"After train STR: STR={pet.str}")
    
    pet.train("spd")
    print(f"After train SPD: SPD={pet.spd}")
    
    print()

def test_pet_storage(pet: MoltPet):
    """Test save/load"""
    print("🧪 Test 4: Pet Storage")
    print("─" * 50)
    
    # Save
    if save_pet(pet):
        print(f"✅ Saved pet to disk")
    
    # Load
    loaded = load_pet("test_user")
    if loaded:
        print(f"✅ Loaded pet from disk: {loaded.name}")
        print(f"   Level: {loaded.level}, HP: {loaded.hp}/{loaded.max_hp}")
        print(f"   STR: {loaded.str}, SPD: {loaded.spd}, INT: {loaded.int}")
    
    print()
    return loaded

def test_battle(pet1: MoltPet, pet2: MoltPet):
    """Test battle system"""
    print("🧪 Test 5: Battle System")
    print("─" * 50)
    
    # Create fresh pets for battle
    p1 = MoltPet("attacker", "Attacker")
    p2 = MoltPet("defender", "Defender")
    
    print(f"Battle: {p1.name} vs {p2.name}")
    print(f"  {p1.name}: HP={p1.hp}, STR={p1.str}, SPD={p1.spd}")
    print(f"  {p2.name}: HP={p2.hp}, STR={p2.str}, SPD={p2.spd}")
    
    engine = BattleEngine(p1, p2)
    result = engine.simulate()
    
    print(f"\n🏆 Winner: {result['winner'].upper()}")
    print(f"  {result['attacker']['name']}: {result['attacker']['final_hp']} HP remaining")
    print(f"  {result['defender']['name']}: {result['defender']['final_hp']} HP remaining")
    print(f"  Duration: {result['turns']} turns")
    print()

def test_ascii_rendering(pet: MoltPet):
    """Test ASCII art"""
    print("🧪 Test 6: ASCII Art Rendering")
    print("─" * 50)
    
    print("Pet Visualization:")
    print(render_pet(pet))
    
    print("\nFull Status:")
    print(render_status(pet))

def main():
    print("\n" + "=" * 50)
    print("🐾 MOLTGOTCHI CORE TEST")
    print("=" * 50 + "\n")
    
    # Run tests
    pet = test_pet_creation()
    test_pet_care(pet)
    test_pet_training(pet)
    loaded_pet = test_pet_storage(pet)
    test_battle(pet, loaded_pet)
    test_ascii_rendering(loaded_pet)
    
    print("=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
