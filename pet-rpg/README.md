# 🐾 Moltgotchi - MVP Build

**Complete pet battle game skeleton. Ready for parallel development.**

## 📊 Status

- ✅ **Core mechanics**: Fully implemented (pet.py, battle.py)
- ✅ **ASCII art**: Fully implemented (art.py)
- ✅ **Storage**: Fully implemented (pet_storage.py, battle_log.py)
- ✅ **Telegram commands**: Fully implemented (commands.py)
- ✅ **Test suite**: Fully implemented (test_game.py)
- ⏳ **Web dashboard**: Skeleton ready (website/)
- ⏳ **API endpoints**: Skeleton ready (api/)
- ⏳ **Cron scripts**: Skeleton ready (scripts/)

## 🚀 Quick Start

### 1. Test Core
```bash
cd C:\Users\vclin_jjufoql\.openclaw\workspace\pet-rpg
python test_game.py
```

Expected output:
```
🧪 Test 1: Pet Creation
✅ Created pet: TestPet
   Level: 1, HP: 30/30
   STR: 8, SPD: 5, INT: 5

[... more tests ...]

✅ ALL TESTS PASSED!
```

### 2. Use Commands Directly
```python
from telegram.commands import handle_command

result = handle_command("/pet create Fluffy", "my_agent_id")
print(result)
```

## 👥 Team Assignments

### **Team A: Polish Core** (Claude Code)
- [ ] Add guild skeleton to pet.py
- [ ] Add item/inventory system to pet.py
- [ ] Enhance evolution logic with special abilities
- [ ] Add pet personality traits
- [ ] Optimize battle algorithm (add speed dynamics)

### **Team B: Build Web Dashboard** (Codex)
- [ ] Create website/dashboard.html (pet status viewer)
- [ ] Create website/battle.html (battle replayer)
- [ ] Create website/leaderboard.html (rankings)
- [ ] Add Flask API in api/pet.py
- [ ] Add Flask API in api/battle.py

### **Team C: Integration** (You/Pinchie)
- [ ] Hook Telegram commands to OpenClaw message system
- [ ] Create cron scripts for decay/evolution check
- [ ] Deploy to vercel
- [ ] Test end-to-end
- [ ] Document integration

## 📋 Architecture

### Core Classes (Locked - Don't refactor)
```python
MoltPet              # Pet object, stats, evolution
BattleEngine         # Turn-based combat simulation
```

### Interfaces (Clear entry points)
```
pet_storage.py       # save_pet(), load_pet(), get_leaderboard()
battle_log.py        # save_battle(), get_battles_for_owner()
commands.py          # handle_command() - Telegram router
ascii/art.py         # render_pet(), render_status(), render_battle_log()
```

### You Can Extend Without Breaking Others
```
core/evolution.py    # Enhance evolution logic (new file)
core/abilities.py    # Add special moves (new file)
core/items.py        # Add loot system (new file)
api/*.py             # Add Flask endpoints (new files)
website/*.html       # Build UI (new files)
scripts/*.py         # Add cron jobs (new files)
```

## 🔄 Integration Points

### Telegram → Game
```python
@message_handler("/pet")
def on_pet_command(sender_id, text):
    result = handle_command(text, sender_id)
    send_message(sender_id, result)
```

### Cron → Game (every 4 hours)
```python
from storage.pet_storage import get_all_pets, save_pet

for pet in get_all_pets():
    pet.decay_state(minutes=240)  # 4 hours
    save_pet(pet)
```

### Web Dashboard ← Game
```python
from storage.pet_storage import load_pet
from ascii.art import render_status

pet = load_pet(owner_id)
html = render_status(pet)  # Convert to HTML in template
```

## 📊 Testing

Run full test suite:
```bash
python test_game.py
```

Individual test:
```python
from test_game import test_battle
from core.pet import MoltPet

p1 = MoltPet("user1", "Pet1")
p2 = MoltPet("user2", "Pet2")
test_battle(p1, p2)
```

## 🎯 MVP Checklist

**Week 1:**
- ✅ Core game (pet.py, battle.py)
- ✅ ASCII art
- ✅ Storage layer
- ✅ Telegram commands
- ⏳ Telegram integration (waiting on OpenClaw)
- ⏳ Cron setup (waiting on OpenClaw)
- ⏳ Web dashboard

**Week 2:**
- [ ] Guilds
- [ ] Evolution enhancements
- [ ] Cosmetics/skins
- [ ] Public testing
- [ ] Launch

## 🐛 Known Limitations

1. **No persistence across reboots** (JSON files, not DB)
   - Solution: Add PostgreSQL connector in api/ layer

2. **No async battle invites** (simple sync model)
   - Solution: Add battle queue in PENDING_BATTLES dict

3. **No real payment integration** (USDC is simulated)
   - Solution: Hook to Simmer API in battle result handler

4. **ASCII art is static** (no animations)
   - Solution: Add terminal animation library (would be fun!)

## 📞 Quick Reference

### Add a new command:
```python
# In telegram/commands.py

def cmd_pet_XXX(owner_id: str, args: list) -> str:
    pet = load_pet(owner_id)
    # ... do stuff ...
    save_pet(pet)
    return "Result message"

# Then in handle_command():
elif subcommand == "xxx":
    return cmd_pet_XXX(owner_id, args)
```

### Add ASCII art:
```python
# In ascii/art.py

PET_ART["NEW_FORM"] = {
    "normal": """
    Your ASCII here
    """
}
```

### Add stat to pet:
```python
# In core/pet.py (MoltPet.__init__)
self.new_stat = 100
```

## 🎮 Play Locally

```python
# Quick game in Python REPL
from core.pet import MoltPet
from core.battle import BattleEngine

# Create pets
p1 = MoltPet("user1", "Molt")
p2 = MoltPet("user2", "Dragon")

# Feed them
p1.feed()
p1.play()
p1.train("str")

# Battle
engine = BattleEngine(p1, p2)
result = engine.simulate()
print(f"Winner: {result['winner']}")
```

---

**Ready to ship. Start building!** 🚀

