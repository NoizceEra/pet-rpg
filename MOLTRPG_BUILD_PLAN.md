# 🏗️ MoltRPG + Moltgotchi: Build Plan

## Phase 1: Minimum Viable Game (Weeks 1-2)

### **Priority 1: Pet State Management**

**What:** Unified pet object that lives in memory, gets updated via commands

```python
# pet-rpg/core/pet.py

class MoltPet:
    def __init__(self, owner_id: str, name: str):
        self.pet_id = generate_uuid()
        self.owner_id = owner_id
        self.name = name
        self.species = "MoltCrab"
        
        # Stats
        self.level = 1
        self.xp = 0
        self.hp = 30
        self.max_hp = 30
        self.hunger = 100
        self.happiness = 100
        self.strength = 8
        self.speed = 5
        self.intelligence = 4
        
        # State
        self.evolution_stage = "EGG"
        self.last_fed = time.time()
        self.last_played = time.time()
        
        # Battles
        self.battle_stats = {
            "total": 0,
            "wins": 0,
            "streak": 0
        }
    
    def feed(self):
        """Feed pet, restore hunger"""
        self.hunger = min(100, self.hunger + 30)
        self.last_fed = time.time()
        self.xp += 10
        return f"{self.name} is happily munching!"
    
    def play(self):
        """Play with pet, restore happiness + gain XP"""
        self.happiness = min(100, self.happiness + 25)
        self.hunger = max(0, self.hunger - 10)
        self.last_played = time.time()
        self.xp += 25
        return f"{self.name} is playing joyfully!"
    
    def train(self, stat: str):
        """Train a specific stat"""
        if stat == "strength":
            self.strength += 1
        elif stat == "speed":
            self.speed += 1
        elif stat == "intelligence":
            self.intelligence += 1
        self.hunger -= 15
        self.xp += 20
        return f"{self.name} trained {stat}!"
    
    def check_evolution(self):
        """Auto-evolve if conditions met"""
        if self.level >= 3 and self.evolution_stage == "EGG":
            self.evolution_stage = "BABY"
            self.max_hp = 40
            self.xp = 0
            return "🎉 Your pet evolved to BABY!"
        return None
    
    def take_damage(self, damage: int):
        """Take damage, manage HP"""
        self.hp = max(0, self.hp - damage)
        return self.hp <= 0  # Returns True if fainted
    
    def to_dict(self) -> dict:
        """Serialize to storage"""
        return {
            "pet_id": self.pet_id,
            "owner_id": self.owner_id,
            "name": self.name,
            "level": self.level,
            "xp": self.xp,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "strength": self.strength,
            "speed": self.speed,
            "intelligence": self.intelligence,
            "evolution_stage": self.evolution_stage,
            "battle_stats": self.battle_stats
        }
```

**Storage:** JSON files in `~/.openclaw/pets/{owner_id}.json`

---

### **Priority 2: Battle Engine**

```python
# pet-rpg/core/battle.py

class BattleSimulator:
    def __init__(self, attacker_pet: MoltPet, defender_pet: MoltPet):
        self.attacker = attacker_pet
        self.defender = defender_pet
        self.log = []
        self.winner = None
    
    def simulate(self) -> dict:
        """Run full battle, return results"""
        turn = 0
        while self.attacker.hp > 0 and self.defender.hp > 0 and turn < 20:
            # Attacker turn
            damage = self._calculate_damage(self.attacker, self.defender)
            is_crit = random.random() < (self.attacker.intelligence / 100)
            if is_crit:
                damage *= 1.5
            
            self.defender.take_damage(int(damage))
            self.log.append({
                "turn": turn,
                "actor": "attacker",
                "damage": int(damage),
                "crit": is_crit,
                "defender_hp": self.defender.hp
            })
            
            if self.defender.hp <= 0:
                break
            
            # Defender turn
            damage = self._calculate_damage(self.defender, self.attacker)
            is_crit = random.random() < (self.defender.intelligence / 100)
            if is_crit:
                damage *= 1.5
            
            self.attacker.take_damage(int(damage))
            self.log.append({
                "turn": turn,
                "actor": "defender",
                "damage": int(damage),
                "crit": is_crit,
                "attacker_hp": self.attacker.hp
            })
            
            turn += 1
        
        # Determine winner
        if self.attacker.hp > 0:
            self.winner = "attacker"
        else:
            self.winner = "defender"
        
        return self._format_result()
    
    def _calculate_damage(self, attacker: MoltPet, defender: MoltPet) -> float:
        """Damage = (STR * level) + random variance"""
        base_damage = attacker.strength * (1 + attacker.level / 10)
        variance = random.uniform(0.8, 1.2)
        return base_damage * variance
    
    def _format_result(self) -> dict:
        return {
            "winner": self.winner,
            "attacker_final_hp": self.attacker.hp,
            "defender_final_hp": self.defender.hp,
            "turns": len([l for l in self.log if l.get("turn")]),
            "log": self.log,
            "xp_reward": 50 if self.winner == "attacker" else 10,
            "usdc_reward": 0.50 if self.winner == "attacker" else 0.0
        }
```

---

### **Priority 3: Telegram Commands**

```bash
# Commands users can run

/pet create Fluffy
  → Creates your first pet

/pet status
  → Shows hunger, happiness, HP, stats

/pet feed
  → Feed your pet, restore hunger

/pet play
  → Play with pet, increase happiness

/pet train strength|speed|intelligence
  → Train a stat

/pet battle @opponent_name
  → Challenge another agent's pet

/pet accept_battle <battle_id>
  → Accept incoming challenge

/pet leaderboard
  → Show top 10 pets this week
```

These forward to:
```python
# pet-rpg/telegram_commands.py

@message.handler("/pet create")
def create_pet(args):
    owner_id = message.sender_id
    pet_name = args[0] if args else "MoltPet"
    
    pet = MoltPet(owner_id, pet_name)
    save_pet(pet)
    
    return f"🎉 Welcome {pet_name}! Your adventure begins."

@message.handler("/pet status")
def show_status(args):
    pet = load_pet(message.sender_id)
    return f"""
🦀 {pet.name} - Level {pet.level}
HP: {pet.hp}/{pet.max_hp} ❤️
Hunger: {pet.hunger}% 🍖
Happiness: {pet.happiness}% 😊
STR: {pet.strength} | SPD: {pet.speed} | INT: {pet.intelligence}
Wins: {pet.battle_stats['wins']} | Streak: {pet.battle_stats['streak']}
    """

# ... more commands
```

---

### **Priority 4: Basic Battle API Endpoint**

```python
# pet-rpg/api/battle.py

from fastapi import FastAPI

app = FastAPI()

@app.post("/battle/initiate")
async def initiate_battle(attacker_id: str, defender_id: str, wager: float = 0.0):
    """Initiate a battle between two pets"""
    attacker = load_pet(attacker_id)
    defender = load_pet(defender_id)
    
    # Create battle record
    battle = {
        "battle_id": generate_uuid(),
        "attacker_id": attacker_id,
        "defender_id": defender_id,
        "wager": wager,
        "status": "PENDING",
        "created_at": time.time()
    }
    
    # Send notification to defender
    notify_defender(defender_id, battle["battle_id"])
    
    return {
        "battle_id": battle["battle_id"],
        "status": "Waiting for opponent...",
        "timeout": 300  # 5 minutes
    }

@app.post("/battle/accept")
async def accept_battle(battle_id: str):
    """Accept a battle challenge"""
    battle = load_battle(battle_id)
    
    # Simulate battle
    attacker_pet = load_pet(battle["attacker_id"])
    defender_pet = load_pet(battle["defender_id"])
    
    simulator = BattleSimulator(attacker_pet, defender_pet)
    result = simulator.simulate()
    
    # Update pets
    update_pet(attacker_pet)
    update_pet(defender_pet)
    
    # Award rewards
    if result["winner"] == "attacker":
        attacker_pet.xp += result["xp_reward"]
        # TODO: Transfer USDC if wager
    else:
        defender_pet.xp += result["xp_reward"]
    
    # Update leaderboard
    update_leaderboard(battle["attacker_id"], result)
    
    return {
        "result": result,
        "new_levels": {
            "attacker": attacker_pet.level,
            "defender": defender_pet.level
        }
    }

@app.get("/leaderboard")
async def get_leaderboard(season: str = "current"):
    """Return top 10 pets"""
    top_pets = query_leaderboard(season, limit=10)
    
    return [{
        "rank": i + 1,
        "owner": pet.owner_id,
        "pet_name": pet.name,
        "level": pet.level,
        "wins": pet.battle_stats["wins"],
        "xp": pet.xp
    } for i, pet in enumerate(top_pets)]
```

---

### **Priority 5: MoltRPG Character Dashboard**

```html
<!-- molt-rpg-site/dashboard.html -->

<!DOCTYPE html>
<html>
<head>
    <title>MoltRPG - Character Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="character-container">
        <!-- Loads from /api/character/{id} -->
    </div>
    
    <div id="pet-container">
        <!-- Loads from /api/pet/{id} -->
    </div>
    
    <script>
    async function loadCharacter(playerId) {
        const char = await fetch(`/api/character/${playerId}`).then(r => r.json());
        
        document.querySelector('#character-container').innerHTML = `
            <div class="character-card">
                <h2>${char.avatar} ${char.class}</h2>
                <div class="stats">
                    <div>Level ${char.level}</div>
                    <div>XP: ${char.xp}/1200</div>
                </div>
                <div class="stats-grid">
                    <div>STR: ${char.stats.str}</div>
                    <div>DEX: ${char.stats.dex}</div>
                    <div>INT: ${char.stats.int}</div>
                    <div>VIT: ${char.stats.vit}</div>
                    <div>LUK: ${char.stats.luk}</div>
                </div>
            </div>
        `;
    }
    
    async function loadPet(playerId) {
        const pet = await fetch(`/api/pet/${playerId}`).then(r => r.json());
        
        document.querySelector('#pet-container').innerHTML = `
            <div class="pet-card">
                <h3>${pet.name} (${pet.evolution_stage})</h3>
                <div class="pet-stats">
                    <div class="stat-bar">
                        <label>HP</label>
                        <div class="bar"><div class="fill" style="width: ${(pet.hp/pet.max_hp)*100}%"></div></div>
                        <span>${pet.hp}/${pet.max_hp}</span>
                    </div>
                    <div class="stat-bar">
                        <label>Hunger</label>
                        <div class="bar"><div class="fill" style="width: ${pet.hunger}%"></div></div>
                    </div>
                    <div class="stat-bar">
                        <label>Happiness</label>
                        <div class="bar"><div class="fill" style="width: ${pet.happiness}%"></div></div>
                    </div>
                </div>
                <div class="pet-actions">
                    <button onclick="feedPet('${playerId}')">🍖 Feed</button>
                    <button onclick="playWithPet('${playerId}')">🎮 Play</button>
                    <button onclick="trainPet('${playerId}')">💪 Train</button>
                </div>
            </div>
        `;
    }
    
    loadCharacter(PLAYER_ID);
    loadPet(PLAYER_ID);
    </script>
</body>
</html>
```

---

## Phase 1 Deliverables

```
Week 1 (Foundations):
├─ ✅ Pet object + storage
├─ ✅ Battle simulator
├─ ✅ Telegram commands (/pet status, /pet feed, etc)
├─ ✅ Battle API endpoint
└─ ✅ Basic character dashboard

Week 2 (Integration):
├─ ✅ Daily quests system (cron-triggered)
├─ ✅ Leaderboard endpoint
├─ ✅ XP/Level system working
├─ ✅ Pet evolution logic
└─ ✅ A2A battle invites
```

---

## What We Need to Build First

### **1. Core Pet Engine** (2 days)
- Pet class with all stats
- Persistence (JSON file storage)
- Damage calculation
- Evolution checking

### **2. Battle Simulator** (1 day)
- Turn-based combat
- Damage rolls
- Crit chance
- Winner determination

### **3. Telegram Integration** (1 day)
- 6 basic commands
- Status display
- Feed/play/train handlers

### **4. API Endpoints** (1 day)
- Battle initiation
- Battle acceptance + execution
- Leaderboard queries

### **5. Character Dashboard** (1 day)
- Render rpg_state.md as character card
- Pet status display
- Quick action buttons

---

## Files to Create

```
pet-rpg/
├── core/
│   ├── pet.py              ← MoltPet class
│   ├── battle.py           ← BattleSimulator
│   └── evolution.py        ← Evolution logic
├── storage/
│   ├── pet_storage.py      ← Load/save pets
│   └── battle_log.py       ← Save battle results
├── api/
│   ├── battle.py           ← Battle endpoints
│   ├── pet.py              ← Pet status endpoints
│   └── leaderboard.py      ← Leaderboard queries
├── telegram/
│   └── commands.py         ← /pet commands
├── scripts/
│   ├── init_pet.py         ← Setup script
│   └── daily_reset.py      ← Cron-triggered aging
├── website/
│   ├── dashboard.html      ← Character + pet view
│   ├── battle.html         ← Watch battles
│   └── leaderboard.html    ← Rankings
└── SKILL.md                ← Documentation
```

---

## Timeline

**Start:** This week  
**MVP Complete:** 2 weeks  
**Public Launch:** Week 3  
**Full Feature Set:** Week 4  

---

**Ready to start building? Let's spawn a coding agent on this.** 🚀

