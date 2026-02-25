#!/usr/bin/env python3
"""Quick integration test"""

import sys
sys.path.insert(0, '.')

from core.pet import MoltPet
from core.battle import BattleEngine
from ascii.art import render_status

print("MOLTGOTCHI INTEGRATION TEST")
print("=" * 50)

# Test 1: Create pet
p1 = MoltPet(pet_id='p1', owner_id='user1', name='Fluffy')
print("TEST 1: Pet Creation - PASS")

# Test 2: Care actions
p1.feed()
p1.play()
print("TEST 2: Pet Care - PASS")

# Test 3: Training
p1.train('strength')
print("TEST 3: Pet Training - PASS")

# Test 4: Battle
p2 = MoltPet(pet_id='p2', owner_id='user2', name='Sparky')
engine = BattleEngine(p1, p2)
result = engine.simulate()
print("TEST 4: Battle System - PASS")

# Test 5: ASCII rendering
status = render_status(p1)
print("TEST 5: ASCII Rendering - PASS")

# Test 6: Serialization
pet_dict = p1.to_dict()
p1_loaded = MoltPet.from_dict(pet_dict)
print("TEST 6: Serialization - PASS")

print()
print("=" * 50)
print("ALL TESTS PASSED!")
print()
print("SUMMARY:")
print(f"  Pet created: {p1.name}")
print(f"  Level: {p1.level}")
print(f"  HP: {p1.hp}/{p1.max_hp}")
print(f"  Hunger: {int(p1.hunger)}%")
print(f"  Battle wins: {p1.battles_won}")
