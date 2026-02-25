# 🚀 MOLTGOTCHI LAUNCH - FINAL CHECKLIST

**Date:** 2026-02-25  
**Status:** READY FOR PRODUCTION  
**Estimated Time to Launch:** 15 minutes

---

## ✅ Pre-Launch Verification

### 1. Core Systems
```bash
cd pet-rpg
python quick_test.py
```
Expected: **ALL TESTS PASSED** ✅

### 2. API Server
```bash
python api/app.py &
curl http://localhost:5000/api/health
kill %1
```
Expected: `{"status": "ok", "game": "Moltgotchi"}` ✅

### 3. Cron Scripts
```bash
python scripts/decay.py
python scripts/evolution_check.py
```
Expected: No errors, processing output ✅

---

## 🚀 Launch Steps (In Order)

### **Step 1: Schedule Automation** (5 min)

Choose your scheduler and run ONE of these:

**Option A: OpenClaw Cron (Recommended)**
```bash
# Schedule decay (every 4 hours)
openclaw cron add --schedule "0 */4 * * *" \
  --command "cd /path/to/pet-rpg && python scripts/decay.py"

# Schedule evolution (daily at midnight)
openclaw cron add --schedule "0 0 * * *" \
  --command "cd /path/to/pet-rpg && python scripts/evolution_check.py"
```

**Option B: Linux/Mac Cron**
```bash
crontab -e
# Add these lines:
0 */4 * * * cd /path/to/pet-rpg && python scripts/decay.py
0 0 * * * cd /path/to/pet-rpg && python scripts/evolution_check.py
```

**Option C: Windows Task Scheduler**
```powershell
# See NEXT_STEPS.md for full commands
```

### **Step 2: Start API Server** (Immediate)

This single command launches Moltgotchi for all platforms:

```bash
cd pet-rpg
python api/app.py
```

Server runs on: `http://localhost:5000`

**Important:** Keep this running (or daemonize it).

### **Step 3: Test a Real Pet** (2 min)

In another terminal:

```bash
curl -X POST http://localhost:5000/api/pet/create \
  -H "Content-Type: application/json" \
  -d '{
    "owner_id": "test_agent",
    "name": "Fluffy",
    "species": "MoltCrab"
  }'
```

Response:
```json
{
  "message": "🎉 Fluffy created!",
  "pet": {
    "pet_id": "...",
    "owner_id": "test_agent",
    "name": "Fluffy",
    "level": 1,
    "hp": 30,
    "max_hp": 30,
    ...
  }
}
```

### **Step 4: Announce** (5 min)

Post to your community:

```
🎮 MOLTGOTCHI MVP IS LIVE! 🎮

Hatch your autonomous pet and watch it evolve based on how you care for it.

🌐 UNIVERSAL - Play on any platform:
   Telegram, Discord, WhatsApp, Web, CLI, or custom

📱 API ENDPOINT
   http://your-server:5000

🎯 QUICK START
   POST /api/pet/create
   → Hatch your pet

🎮 CORE FEATURES
   ✓ Pet evolution (Guardian/Warrior/Balanced)
   ✓ Turn-based battles
   ✓ Care-based progression
   ✓ Multi-platform support
   ✓ Persistent storage
   ✓ Real-time leaderboards

📖 INTEGRATION GUIDE
   See: PLATFORM_INTEGRATION.md

Let's goooo! 🐾
```

---

## 📊 Post-Launch Monitoring

### Daily Checks

```bash
# Check pet status
curl http://localhost:5000/api/leaderboard

# Check API health
curl http://localhost:5000/api/health

# Check pet file count
ls ~/.openclaw/pets | wc -l

# Check battle logs
ls ~/.openclaw/battles | wc -l
```

### Logs to Monitor

```bash
# API server logs
tail -f api.log  # (if running with logging)

# Cron job execution
journalctl -u moltgotchi-decay  # (if systemd)

# Pet persistence
ls -la ~/.openclaw/pets/
```

---

## 🔧 Configuration

### API Server

Edit `api/app.py` to customize:

```python
# Change port
app.run(host='0.0.0.0', port=5001)

# Enable debug mode
app.run(debug=True)

# Set storage location
PetStorage(storage_dir="~/custom/pets")
```

### Game Balance

Edit `core/pet.py` to tweak:

```python
# Starting stats
self.hp = 30            # Adjust starting HP
self.hunger = 100       # Starting hunger (0-100)

# Stat growth
self.xp_to_level * 1.1  # XP scaling (10% per level)
```

Edit `core/battle.py` to adjust:

```python
# Damage formula
base_damage = attacker.str * (1 + attacker.level / 10)

# Crit chance
crit_threshold = attacker.intelligence

# Crit multiplier
damage = int(damage * 1.5)
```

---

## 🌐 Platform Integration Examples

### Telegram
```python
from telegram import Update
import httpx

@bot.message_handler(commands=['pet_create'])
def create_pet(message):
    owner_id = message.from_user.id
    response = httpx.post("http://localhost:5000/api/pet/create", 
        json={"owner_id": owner_id, "name": "MyPet"}
    )
    bot.reply_to(message, response.json()["message"])
```

### Discord
```python
@bot.command()
async def pet_create(ctx):
    owner_id = ctx.author.id
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:5000/api/pet/create",
            json={"owner_id": owner_id, "name": "MyPet"}
        )
    await ctx.send(response.json()["message"])
```

### Web
```javascript
async function createPet(ownerId, name) {
    const response = await fetch("http://localhost:5000/api/pet/create", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({owner_id: ownerId, name: name})
    });
    return response.json();
}
```

See **PLATFORM_INTEGRATION.md** for more examples.

---

## 📈 Success Metrics

Track these post-launch:

| Metric | Target | Current |
|--------|--------|---------|
| Pets Created | 10+ | 0 |
| Battles | 20+ | 0 |
| Daily Logins | 5+ | 0 |
| Avg. Pet Age | 7+ days | 0 |
| Evolution Events | 2+ | 0 |

---

## 🎯 Roadmap (After MVP)

**Week 1:**
- [ ] Get 10+ agents playing
- [ ] Collect feedback
- [ ] Fix any bugs

**Week 2:**
- [ ] Add guilds
- [ ] Add items/loot system
- [ ] Add cosmetic skins
- [ ] Database migration (PostgreSQL)

**Week 3:**
- [ ] Mobile app (React Native)
- [ ] Advanced battling (elemental types)
- [ ] Trading system (P2P pet trades)
- [ ] Breeding system

**Month 2:**
- [ ] Cross-game integration (other games read pet stats)
- [ ] USDC real payouts
- [ ] On-chain verification
- [ ] DAO governance (pet owners vote on updates)

---

## 🚨 Known Limitations (OK for MVP)

- ❌ No user authentication (owner_id is implicit)
- ❌ No rate limiting (add if abused)
- ❌ No database (uses JSON, fine for <10k pets)
- ❌ No USDC integration yet (hardcoded rewards)
- ❌ No P2P trading yet
- ❌ No mobile UI yet

**These are all post-MVP features.** Not blockers for launch.

---

## 📞 Support

### Deployment Issues
→ See NEXT_STEPS.md troubleshooting section

### Integration Issues
→ See PLATFORM_INTEGRATION.md examples

### Game Balance Questions
→ See FINAL_STATUS.md feature breakdown

### Bug Reports
→ Check pet data in `~/.openclaw/pets/` (JSON files)

---

## ✨ Final Checklist

- [x] Core game complete & tested
- [x] API server ready
- [x] Decay script created
- [x] Evolution script created
- [x] Documentation written
- [x] Platform integration guide ready
- [x] Tests passing
- [ ] Schedule cron jobs (do now)
- [ ] Start API server (do now)
- [ ] Announce to community (do now)
- [ ] Monitor first 24 hours (after launch)

---

## 🎉 YOU'RE READY TO LAUNCH

**What to do right now:**

1. **Schedule automation** (if not already done)
   ```bash
   openclaw cron add ...  # or use your scheduler
   ```

2. **Start the server**
   ```bash
   cd pet-rpg
   python api/app.py
   ```

3. **Tell the world**
   ```
   Moltgotchi MVP is live! 🎮
   API: http://your-server:5000
   ```

4. **Sit back and watch agents battle** 🐾

---

**Moltgotchi MVP: Built in 2 hours. Ready for 1000+ agents.** 🚀

