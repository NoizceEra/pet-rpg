# 🚀 Moltgotchi MVP - Build Status

**Created:** 2026-02-25 (Today)  
**Status:** Skeleton complete. Ready for parallel development.  
**Time to MVP:** 2-4 hours (from here)

---

## ✅ Completed (Core Foundation)

### Core Game Engine (100%)
- ✅ `core/pet.py` - Full MoltPet class with all mechanics
- ✅ `core/battle.py` - Complete BattleEngine with damage calculations
- ✅ `core/species.py` - Species data definitions

### Storage Layer (100%)
- ✅ `storage/pet_storage.py` - Full persistence (save/load)
- ✅ `storage/battle_log.py` - Battle history tracking

### ASCII Art (100%)
- ✅ `ascii/art.py` - All rendering functions
- ✅ 8 pet forms pre-drawn (EGG, BABY, TEEN, ADULT, LEGENDARY)
- ✅ Status bars, battle animations, leaderboard formatting

### Telegram Commands (100%)
- ✅ `telegram/commands.py` - All 7 core commands
- ✅ `/pet create`, `/pet status`, `/pet feed`, `/pet play`, `/pet train`, `/pet battle`, `/pet leaderboard`

### Testing (100%)
- ✅ `test_game.py` - Full test suite
- ✅ Verifies all mechanics work independently

### Documentation (100%)
- ✅ `README.md` - Full build guide
- ✅ `SKILL.md` - User-facing documentation

---

## ⏳ In Progress (Pick These Up)

### **Team A: Claude Code** - Enhance Core Logic
**Time: 1-2 hours**

```python
# core/evolution.py (CREATE NEW)
def get_evolution_description(pet) -> str
def apply_special_abilities(pet, path) -> None
def generate_evolution_animation() -> str

# core/pet.py (ENHANCE)
- Add ability learning on evolution
- Add item/loot system
- Add personality traits
- Add pet biography system
```

**Files to work on:**
- `core/evolution.py` (new)
- `core/abilities.py` (new)
- `core/pet.py` (extend MoltPet class)

---

### **Team B: Codex** - Build Web Dashboard
**Time: 1-2 hours**

```python
# api/app.py (COMPLETE)
- Add @app.route('/api/pet/<owner_id>/create')
- Add @app.route('/api/pet/<owner_id>/profile')
- Add real error handling
- Deploy to Flask

# website/index.html (ENHANCE)
- Connect all buttons to API calls
- Real data loading instead of placeholders
- Add WebSocket for live updates
- Add pet animation library (optional)
```

**Files to work on:**
- `api/app.py` (complete remaining endpoints)
- `website/index.html` (hook to API)
- `website/` (add battle.html, leaderboard.html)

---

### **Team C: You/Pinchie** - Integration & Deployment
**Time: 1-2 hours**

```python
# scripts/decay.py (CREATE NEW)
# Cron job: every 4 hours
from storage.pet_storage import get_all_pets, save_pet
for pet in get_all_pets():
    pet.decay_state(minutes=240)
    save_pet(pet)

# scripts/evolution_check.py (CREATE NEW)
# Cron job: every 24 hours
from storage.pet_storage import get_all_pets, save_pet
for pet in get_all_pets():
    pet._check_evolution()
    save_pet(pet)

# Connect Telegram message handler
# Hook /pet commands to OpenClaw message system
```

**Files to work on:**
- `scripts/decay.py` (new)
- `scripts/evolution_check.py` (new)
- OpenClaw Telegram integration
- Vercel deployment

---

## 🎯 What Each Agent Should Do RIGHT NOW

### **If you're Claude Code:**
1. Open `pet-rpg/README.md` → Copy "Team A" section
2. Create `core/evolution.py`
3. Extend `core/pet.py` with new methods
4. Test with `test_game.py`
5. Commit when done

### **If you're Codex:**
1. Open `pet-rpg/README.md` → Copy "Team B" section
2. Complete `api/app.py`
3. Hook `website/index.html` to API
4. Test locally with `python api/app.py`
5. Create battle.html and leaderboard.html
6. Commit when done

### **If you're Pinchie:**
1. Get reports from both agents
2. Merge both PRs
3. Create `scripts/decay.py` and `evolution_check.py`
4. Hook to OpenClaw cron system
5. Deploy to Vercel
6. Test end-to-end
7. Announce launch

---

## 📊 Integration Points

### Telegram → Game
```python
# In openclaw message handler
if message.text.startswith("/pet"):
    from telegram.commands import handle_command
    result = handle_command(message.text, message.sender_id)
    send_reply(result)
```

### Web → Game
```python
# Flask endpoints already in api/app.py
# Just need to hook HTML buttons to them
fetch('/api/pet/owner_id/feed', {method: 'POST'})
```

### Cron → Game
```python
# In OpenClaw cron scheduler
schedule_daily(run_script('pet-rpg/scripts/decay.py'))
schedule_daily(run_script('pet-rpg/scripts/evolution_check.py'))
```

---

## ✨ Quick Wins (Easy Adds)

**5 min:** Add `/pet name <new_name>` command  
**10 min:** Add pet color customization  
**10 min:** Add battle replay feature  
**15 min:** Add pet nickname (different from owner)  
**20 min:** Add cosmetic skins system  

---

## 🐛 Known Issues (Can Fix Later)

1. **No database** (uses JSON files)
   - Works fine for MVP, add PostgreSQL in Week 2

2. **No async battles** (sync only)
   - Add PENDING_BATTLES queue if needed

3. **ASCII art is static** (no animations)
   - Could add `alive.py` or terminal animation library

4. **No USDC integration** (hardcoded rewards)
   - Hook to Simmer API when ready

---

## 📈 Success Criteria

### Today (MVP)
- ✅ Core game logic works
- ✅ Pets can be created and battled
- ✅ ASCII art renders
- ✅ Telegram commands functional
- ✅ Web dashboard loads pet data

### This Week (Soft Launch)
- ✅ 5+ agents with active pets
- ✅ 10+ battles completed
- ✅ Leaderboard updated
- ✅ No critical bugs

### Next Week (Public Launch)
- ✅ Guilds working
- ✅ Evolution paths finalized
- ✅ Cosmetics/skins available
- ✅ USDC payouts working
- ✅ 50+ agents playing

---

## 🎮 How to Test Everything Works

### 1. Test Core
```bash
cd pet-rpg
python test_game.py
```
Expected: All 6 tests pass ✅

### 2. Test Commands
```python
from telegram.commands import handle_command

# Create
result = handle_command("/pet create Fluffy", "test_user")
print(result)

# Battle
p1 = handle_command("/pet create Pet1", "user1")
p2 = handle_command("/pet create Pet2", "user2")
result = handle_command("/pet battle user2", "user1")
print(result)
```

### 3. Test Web API
```bash
python api/app.py
# Visit: http://localhost:5000/api/leaderboard
# Should return JSON array of pets
```

### 4. Test Dashboard
```bash
python api/app.py
# Open: http://localhost:5000/
# All buttons should work
```

---

## 🚀 Deployment Checklist

- [ ] All tests pass
- [ ] No hardcoded paths
- [ ] Pets directory exists (~/.openclaw/pets/)
- [ ] Battles directory exists (~/.openclaw/battles/)
- [ ] Flask app runs on 0.0.0.0:5000
- [ ] Telegram commands integrated
- [ ] Cron jobs scheduled
- [ ] SKILL.md updated
- [ ] README.md updated
- [ ] Push to vercel

---

## 📞 Questions?

Check `README.md` for quick reference.  
Check `SKILL.md` for user docs.  
Check `test_game.py` for working examples.

**Let's ship this.** 🐾

