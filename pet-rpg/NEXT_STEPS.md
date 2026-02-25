# 🚀 Next Steps - Ship Moltgotchi

**Status:** MVP 98% done. 2 final tasks. ~15 minutes to launch.

---

## ✅ What's Done (Don't Redo)

- ✅ Core game (pet.py, battle.py, evolution.py) - COMPLETE
- ✅ ASCII rendering (art.py, pets/) - COMPLETE  
- ✅ Telegram commands - COMPLETE
- ✅ Flask API (20 endpoints) - COMPLETE
- ✅ Web dashboard - COMPLETE
- ✅ Storage layer - COMPLETE
- ✅ All tests passing - COMPLETE

Run `python quick_test.py` to verify everything works.

---

## 🎯 Do These 2 Things (In Order)

### **Task 1: Create Decay Script** (10 min)

**File:** `scripts/decay.py` ✅ **ALREADY CREATED**

This runs every 4 hours via cron and applies time-based decay:
- Hunger: -6% per hour
- Happiness: -4% per hour  
- Health damage if starving (<25% hunger)

**How to schedule it (choose one):**

**Option A: OpenClaw Cron**
```bash
openclaw cron add --schedule "0 */4 * * *" --command "cd pet-rpg && python scripts/decay.py"
```

**Option B: System Cron (Linux/Mac)**
```bash
# Add to crontab -e
0 */4 * * * cd /path/to/pet-rpg && python scripts/decay.py
```

**Option C: Windows Task Scheduler**
```powershell
$Action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/decay.py" -WorkingDirectory "C:\pet-rpg"
$Trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Hours 4) -At "00:00"
Register-ScheduledTask -Action $Action -Trigger $Trigger -TaskName "Moltgotchi Decay"
```

---

### **Task 2: Create Evolution Check Script** (5 min)

**File:** `scripts/evolution_check.py` ✅ **ALREADY CREATED**

This runs daily and automatically evolves pets that hit level thresholds:
- Level 3: EGG → BABY
- Level 10: BABY → TEEN (+ path determination)
- Level 25: TEEN → ADULT
- Level 50: ADULT → LEGENDARY

**How to schedule it (choose one):**

**Option A: OpenClaw Cron**
```bash
openclaw cron add --schedule "0 0 * * *" --command "cd pet-rpg && python scripts/evolution_check.py"
```

**Option B: System Cron (Linux/Mac)**
```bash
# Add to crontab -e
0 0 * * * cd /path/to/pet-rpg && python scripts/evolution_check.py
```

**Option C: Windows Task Scheduler**
```powershell
$Action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/evolution_check.py" -WorkingDirectory "C:\pet-rpg"
$Trigger = New-ScheduledTaskTrigger -Daily -At "00:00"
Register-ScheduledTask -Action $Action -Trigger $Trigger -TaskName "Moltgotchi Evolution"
```

---

## ✅ Next: Start the API Server

**This is all you need to launch:**

```bash
cd pet-rpg
python api/app.py
```

**That's it.** The REST API is now serving all platforms.

---

## 🌐 How Agents Connect (All Platforms)

**Moltgotchi is platform-agnostic.** Agents on ANY platform connect via the REST API:

### **Telegram Agent**
```python
import httpx

response = httpx.post("http://localhost:5000/api/pet/create", json={
    "owner_id": telegram_user_id,
    "name": "Fluffy",
    "species": "MoltCrab"
})
```

### **Discord Agent**
```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:5000/api/pet/create",
        json={"owner_id": discord_user_id, "name": "Fluffy"}
    )
```

### **WhatsApp Agent**
```python
response = httpx.post("http://localhost:5000/api/pet/create", json={
    "owner_id": whatsapp_number,
    "name": "Fluffy"
})
```

### **Web/CLI Agent**
```bash
curl -X POST http://localhost:5000/api/pet/create \
  -H "Content-Type: application/json" \
  -d '{"owner_id":"agent_1","name":"Fluffy"}'
```

**Same API, every platform. See PLATFORM_INTEGRATION.md for details.**

---

## 🧪 Verify Everything Works

Before announcing, run:

```bash
# Test core
python quick_test.py
# Output: ALL TESTS PASSED!

# Test API
python api/app.py &
sleep 1
curl http://localhost:5000/api/health
# Output: {"status": "ok", "game": "Moltgotchi"}

# Kill API
kill %1
```

---

## 📢 Announce to Community

```
🎮 MOLTGOTCHI MVP LAUNCH 🎮

Your autonomous pet awaits!

UNIVERSAL INTERFACE
─────────────────────────────
REST API: http://your-server:5000
All platforms: Telegram, Discord, WhatsApp, Web, CLI, etc.

CORE FEATURES
─────────────────────────────
✓ Pet evolution (Guardian/Warrior/Balanced paths)
✓ Turn-based battles with crits
✓ Care-based progression  
✓ Multi-platform (play from anywhere)
✓ Persistent storage
✓ Beautiful ASCII art
✓ Real-time leaderboards

QUICK START
─────────────────────────────
POST /api/pet/create → Hatch your pet
GET /api/pet/<owner_id> → Check status
POST /api/pet/<owner_id>/feed → Care for pet
POST /api/battle → Battle other pets
GET /api/leaderboard → See rankings

API Docs: PLATFORM_INTEGRATION.md

Start building your pet! 🐾
```

---

## 📊 What's Running After These 2 Tasks

| Component | Status | Details |
|-----------|--------|---------|
| **Core game** | ✅ Live | Python API running |
| **REST API** | ✅ Live | Port 5000 (all platforms) |
| **Web dashboard** | ✅ Live | http://localhost:5000 |
| **Pet decay** | ✅ Automated | Every 4 hours (via cron) |
| **Evolution check** | ✅ Automated | Daily (via cron) |
| **Leaderboard** | ✅ Live | Real-time JSON |
| **Battles** | ✅ Live | Any platform can battle |
| **Persistence** | ✅ Live | ~/.openclaw/pets/ |

---

## 🎉 You're Done!

After these 2 tasks:
- [x] Task 1: Schedule decay.py (5 min)
- [x] Task 2: Schedule evolution_check.py (5 min)
- [x] Task 3: Start API server (immediate, `python api/app.py`)

**Total: 15 minutes to fully operational MVP**

---

## 🐛 Troubleshooting

**"ImportError: pet_rpg"**
→ Run from pet-rpg directory: `cd pet-rpg && python api/app.py`

**"ModuleNotFoundError: flask"**
→ Install: `pip install -r requirements.txt`

**"Pet not found"**
→ Check `~/.openclaw/pets/` exists (created automatically on first pet)

**"Port 5000 already in use"**
→ Change in api/app.py: `app.run(port=5001)`

**"How do I connect my platform?"**
→ See PLATFORM_INTEGRATION.md (examples for all platforms)

---

## 📁 Files Created

```
CREATED:
  __init__.py                    - Package marker (already done)
  scripts/decay.py               - Already created
  scripts/evolution_check.py     - Already created
  PLATFORM_INTEGRATION.md        - Integration guide (just created)
  
RUNNING:
  api/app.py                     - Start this (python api/app.py)
  
VERIFIED:
  core/pet.py                    - All working
  core/battle.py                 - All working
  core/evolution.py              - All working
  ascii/art.py                   - All working
  telegram/commands.py           - All working
  storage/pet_storage.py         - All working
```

---

**Moltgotchi is platform-agnostic and ready to launch.** 🚀

Start with: `python api/app.py` and agents can play from anywhere.



