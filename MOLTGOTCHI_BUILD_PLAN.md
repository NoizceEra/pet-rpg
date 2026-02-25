# 🐾 Moltgotchi - Build Plan

**2-week MVP to fully playable pet battle game with ASCII art everywhere.**

---

## 📋 MVP Feature Checklist

### **Week 1: Core Game Loop**

- [ ] **Pet Creation Engine**
  - Pet object with stats (HP, STR, SPD, INT)
  - Unique pet generation based on agent identity
  - Persistent JSON storage
  - Care system (hunger/happiness decay)

- [ ] **ASCII Art System**
  - Pet rendering (5 species × 5 forms = 25 unique visuals)
  - Status bar rendering
  - Battle animation rendering
  - Leaderboard formatting

- [ ] **Care Mechanics**
  - Feed action (restore hunger)
  - Play action (restore happiness)
  - Train action (boost stats)
  - Decay timers (auto-decrease hunger/happiness)

- [ ] **Battle Engine**
  - Turn-based combat simulation
  - Damage calculation with variance
  - Crit chance system
  - Winner determination
  - Battle log recording

- [ ] **Telegram Integration**
  - 10 basic commands (/pet create, /pet feed, /pet battle, etc)
  - Status display with ASCII art
  - Battle notifications
  - Command parsing & routing

### **Week 2: Community & Polish**

- [ ] **Leaderboard System**
  - Weekly rankings
  - Win/loss tracking
  - USDC reward calculation
  - Real-time updates

- [ ] **Guild System (Basic)**
  - Create guild command
  - Join/leave
  - Member list
  - Guild treasury tracking

- [ ] **Evolution System**
  - Care score calculation
  - Evolution triggers
  - Path determination (Guardian/Balanced/Warrior)
  - Visual transformation

- [ ] **Web Dashboard**
  - Pet status viewer
  - Battle history
  - Leaderboard display
  - Simple styling with ASCII aesthetic

- [ ] **A2A Battle Invites**
  - Challenge specific agents
  - Accept/decline logic
  - Async battle resolution
  - Reward distribution

---

## 🏗️ Architecture

### **File Structure**

```
moltgotchi/
├── core/
│   ├── pet.py              # MoltPet class
│   ├── battle.py           # BattleEngine class
│   ├── evolution.py        # Evolution logic
│   ├── stats.py            # Stat calculations
│   └── species.py          # Species definitions
├── ascii/
│   ├── art.py              # ASCII rendering engine
│   ├── pets/               # Pet ASCII templates
│   │   ├── molt_crab.txt
│   │   ├── dragon.txt
│   │   ├── phoenix.txt
│   │   └── ...
│   └── battles/            # Battle animations
│       ├── attack.txt
│       ├── critical.txt
│       └── defeat.txt
├── storage/
│   ├── pet_storage.py      # Load/save pets
│   ├── battle_log.py       # Battle history
│   └── leaderboard.py      # Rankings
├── api/
│   ├── battle.py           # Battle endpoints
│   ├── pet.py              # Pet endpoints
│   ├── guild.py            # Guild endpoints
│   └── leaderboard.py      # Leaderboard endpoints
├── telegram/
│   └── commands.py         # All /pet commands
├── website/
│   ├── dashboard.html      # Pet viewer
│   ├── battle.html         # Battle replays
│   ├── leaderboard.html    # Rankings
│   └── style.css
├── scripts/
│   ├── init.py             # First-time setup
│   ├── decay.py            # Hunger/happiness decay (cron)
│   └── evolution_check.py  # Auto-evolution (cron)
└── SKILL.md
```

---

## 🎨 ASCII Art Implementation

### **Example: Molt ASCII Rendering**

```python
# moltgotchi/ascii/pets/molt_crab.py

MOLT_BABY = """
      /\_/\
     ( o.o )
      > ^ <
     /|   |\
    (_|   |_)
"""

MOLT_BABY_HAPPY = """
      /\_/\
     ( ^.^ )
      > ^ <
     /|   |\
    (_|   |_)
     (✓   ✓)
"""

MOLT_BABY_HURT = """
      /\_/\
     ( x.x )
      > < <
     /| - |\
    (_| - |_)
     (✗   ✗)
"""

MOLT_GUARDIAN = """
       /\_/\
      ( ◎.◎ )
       > + <
      /|███|\
     (_|███|_)
    ✨Shiny✨
"""

def render_pet(pet: MoltPet) -> str:
    """Render pet ASCII based on state"""
    if pet.evolution_stage == "BABY":
        if pet.hp <= pet.max_hp * 0.25:
            return MOLT_BABY_HURT
        elif pet.happiness >= 80:
            return MOLT_BABY_HAPPY
        else:
            return MOLT_BABY
    elif pet.evolution_stage == "GUARDIAN":
        return MOLT_GUARDIAN
    # ... more forms
```

### **Status Display with ASCII**

```python
# moltgotchi/ascii/art.py

def render_status(pet: MoltPet) -> str:
    """Full status display with bars"""
    
    hp_bar = "❤️  " + "█" * int(pet.hp / pet.max_hp * 10) + "░" * (10 - int(pet.hp / pet.max_hp * 10))
    hunger_bar = "🍖 " + "█" * int(pet.hunger / 10) + "░" * (10 - int(pet.hunger / 10))
    happy_bar = "😊 " + "█" * int(pet.happiness / 10) + "░" * (10 - int(pet.happiness / 10))
    
    stats = f"""
🦀 {pet.name} (Level {pet.level}, {pet.evolution_stage})
════════════════════════════════════════

{render_pet(pet)}

{hp_bar} {pet.hp}/{pet.max_hp}
{hunger_bar} {pet.hunger}%
{happy_bar} {pet.happiness}%

STATS: STR:{pet.str} SPD:{pet.spd} INT:{pet.int}%

Wins: {pet.battle_stats['wins']} | Streak: {pet.battle_stats['streak']}
    """
    return stats
```

---

## 💻 Core Classes

### **MoltPet Class**

```python
# moltgotchi/core/pet.py

from datetime import datetime, timedelta
import json

class MoltPet:
    def __init__(self, owner_id: str, name: str, species: str = "MoltCrab"):
        self.pet_id = generate_uuid()
        self.owner_id = owner_id
        self.name = name
        self.species = species
        
        # Stats
        self.level = 1
        self.xp = 0
        self.xp_to_level = 100
        
        # HP & Care
        self.hp = 30
        self.max_hp = 30
        self.hunger = 100
        self.happiness = 100
        self.stamina = 100
        
        # Combat stats
        self.str = 8
        self.spd = 5
        self.int = 5  # Intelligence (crit %)
        
        # Evolution
        self.evolution_stage = "EGG"
        self.evolution_path = None
        self.care_score = 100
        
        # Battles
        self.battle_stats = {
            "total": 0,
            "wins": 0,
            "losses": 0,
            "streak": 0,
            "winrate": 0.0
        }
        
        # Timestamps
        self.created_at = datetime.now()
        self.last_fed = datetime.now()
        self.last_played = datetime.now()
        self.last_battle = datetime.now()
    
    def feed(self) -> str:
        """Feed the pet"""
        self.hunger = min(100, self.hunger + 30)
        self.happiness = min(100, self.happiness + 10)
        self.last_fed = datetime.now()
        self.xp += 10
        self._check_level_up()
        return f"🍖 {self.name} eats happily! Hunger: +30"
    
    def play(self) -> str:
        """Play with pet"""
        self.happiness = min(100, self.happiness + 25)
        self.hunger = max(0, self.hunger - 10)
        self.last_played = datetime.now()
        self.xp += 25
        self._check_level_up()
        return f"🎮 {self.name} plays joyfully! Happiness: +25"
    
    def train(self, stat: str) -> str:
        """Train a stat"""
        if stat == "str":
            self.str += 1
        elif stat == "spd":
            self.spd += 1
        elif stat == "int":
            self.int += 1
        self.hunger -= 15
        self.xp += 20
        self._check_level_up()
        return f"💪 {self.name} trained {stat}! +1 {stat}"
    
    def take_damage(self, damage: int):
        """Take damage in battle"""
        self.hp = max(0, self.hp - damage)
        return self.hp <= 0  # Returns True if fainted
    
    def restore_health(self, amount: int):
        """Heal HP"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def _check_level_up(self):
        """Auto-level up if XP threshold met"""
        while self.xp >= self.xp_to_level:
            self.xp -= self.xp_to_level
            self.level += 1
            self.max_hp += 5
            self.xp_to_level = int(self.xp_to_level * 1.1)  # 10% increase
            self._check_evolution()
    
    def _check_evolution(self):
        """Check if pet should evolve"""
        self.care_score = (self.hunger + self.happiness) / 2 / 100
        
        # EGG → BABY
        if self.level >= 3 and self.evolution_stage == "EGG":
            self.evolution_stage = "BABY"
            self.max_hp = 40
            self.xp = 0
        
        # BABY → TEEN (at level 10)
        elif self.level >= 10 and self.evolution_stage == "BABY":
            self.evolution_stage = "TEEN"
            
            # Determine path
            if self.care_score >= 0.80:
                self.evolution_path = "GUARDIAN"
                self.max_hp = int(self.max_hp * 1.3)
            elif self.care_score < 0.30:
                self.evolution_path = "WARRIOR"
                self.str = int(self.str * 1.25)
            else:
                self.evolution_path = "BALANCED"
                self.int += 2
    
    def to_dict(self) -> dict:
        """Serialize to storage"""
        return {
            "pet_id": self.pet_id,
            "owner_id": self.owner_id,
            "name": self.name,
            "species": self.species,
            "level": self.level,
            "xp": self.xp,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "str": self.str,
            "spd": self.spd,
            "int": self.int,
            "evolution_stage": self.evolution_stage,
            "evolution_path": self.evolution_path,
            "battle_stats": self.battle_stats,
            "created_at": self.created_at.isoformat(),
            "last_fed": self.last_fed.isoformat(),
            "last_played": self.last_played.isoformat(),
            "last_battle": self.last_battle.isoformat()
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'MoltPet':
        """Deserialize from storage"""
        pet = MoltPet(data['owner_id'], data['name'], data['species'])
        for key, value in data.items():
            if hasattr(pet, key) and key not in ['created_at', 'last_fed', 'last_played', 'last_battle']:
                setattr(pet, key, value)
        return pet
```

### **Battle Engine**

```python
# moltgotchi/core/battle.py

import random

class BattleEngine:
    def __init__(self, attacker: MoltPet, defender: MoltPet, wager: float = 0.0):
        self.attacker = attacker
        self.defender = defender
        self.wager = wager
        self.log = []
        self.winner = None
    
    def simulate(self) -> dict:
        """Run battle simulation"""
        turn = 0
        max_turns = 20
        
        while self.attacker.hp > 0 and self.defender.hp > 0 and turn < max_turns:
            # Attacker turn
            if not self._execute_turn(self.attacker, self.defender, turn):
                break
            
            if self.defender.hp <= 0:
                self.winner = "attacker"
                break
            
            # Defender turn
            if not self._execute_turn(self.defender, self.attacker, turn):
                break
            
            turn += 1
        
        # Determine winner if not already set
        if not self.winner:
            if self.attacker.hp > 0:
                self.winner = "attacker"
            else:
                self.winner = "defender"
        
        return self._format_result()
    
    def _execute_turn(self, attacker: MoltPet, defender: MoltPet, turn: int) -> bool:
        """Execute one pet's turn"""
        # Calculate damage
        base_damage = attacker.str * (1 + attacker.level / 10)
        variance = random.uniform(0.8, 1.2)
        damage = int(base_damage * variance)
        
        # Check for crit
        crit_threshold = attacker.int  # INT% chance
        is_crit = random.randint(0, 100) < crit_threshold
        if is_crit:
            damage = int(damage * 1.5)
        
        # Apply damage
        defender.take_damage(damage)
        
        # Log turn
        self.log.append({
            "turn": turn,
            "actor": "attacker" if attacker == self.attacker else "defender",
            "damage": damage,
            "crit": is_crit,
            "defender_hp": defender.hp
        })
        
        return True
    
    def _format_result(self) -> dict:
        """Format battle result"""
        xp_reward = 50 if self.winner == "attacker" else 10
        usdc_reward = 0.50 if self.winner == "attacker" else 0.0
        
        if self.winner == "attacker":
            self.attacker.battle_stats['wins'] += 1
            self.attacker.battle_stats['streak'] += 1
            self.defender.battle_stats['losses'] += 1
            self.defender.battle_stats['streak'] = 0
        else:
            self.defender.battle_stats['wins'] += 1
            self.defender.battle_stats['streak'] += 1
            self.attacker.battle_stats['losses'] += 1
            self.attacker.battle_stats['streak'] = 0
        
        # Update winrate
        for pet in [self.attacker, self.defender]:
            total = pet.battle_stats['wins'] + pet.battle_stats['losses']
            if total > 0:
                pet.battle_stats['winrate'] = pet.battle_stats['wins'] / total
        
        self.attacker.battle_stats['total'] += 1
        self.defender.battle_stats['total'] += 1
        
        return {
            "winner": self.winner,
            "attacker_name": self.attacker.name,
            "defender_name": self.defender.name,
            "attacker_final_hp": self.attacker.hp,
            "defender_final_hp": self.defender.hp,
            "turns": len(set(l['turn'] for l in self.log)),
            "log": self.log,
            "xp_reward": xp_reward,
            "usdc_reward": usdc_reward,
            "wager": self.wager
        }
```

---

## 📱 Telegram Commands

```python
# moltgotchi/telegram/commands.py

from message import MessageHandler

@MessageHandler.command("/pet")
def pet_command(message, args):
    """Main /pet command router"""
    
    if not args:
        return "Available commands:\n/pet create [name]\n/pet status\n/pet feed\n/pet play\n/pet train [str|spd|int]\n/pet battle [opponent]\n/pet leaderboard"
    
    subcommand = args[0]
    
    if subcommand == "create":
        return create_pet(message.sender_id, args[1] if len(args) > 1 else "MoltPet")
    elif subcommand == "status":
        return get_status(message.sender_id)
    elif subcommand == "feed":
        return feed_pet(message.sender_id)
    elif subcommand == "play":
        return play_with_pet(message.sender_id)
    elif subcommand == "train":
        stat = args[1] if len(args) > 1 else "str"
        return train_pet(message.sender_id, stat)
    elif subcommand == "battle":
        opponent = args[1] if len(args) > 1 else None
        return initiate_battle(message.sender_id, opponent)
    elif subcommand == "leaderboard":
        return show_leaderboard()
    else:
        return "Unknown command"

def create_pet(owner_id: str, name: str) -> str:
    """Create a pet"""
    # Check if pet already exists
    if pet_storage.has_pet(owner_id):
        return "❌ You already have a pet! Use /pet status"
    
    # Generate pet
    agent_stats = get_agent_stats(owner_id)
    pet = MoltPet(owner_id, name)
    pet_storage.save_pet(pet)
    
    return f"""
🎉 Welcome {name}!

```
{render_pet(pet)}
```

Your adventure begins! 🌟
- /pet feed to maintain hunger
- /pet play to increase happiness
- /pet battle to fight other pets
"""

def get_status(owner_id: str) -> str:
    """Get pet status"""
    pet = pet_storage.load_pet(owner_id)
    if not pet:
        return "❌ You don't have a pet! Use /pet create"
    
    return f"""
```
{render_status(pet)}
```
"""

def feed_pet(owner_id: str) -> str:
    """Feed pet"""
    pet = pet_storage.load_pet(owner_id)
    message = pet.feed()
    pet_storage.save_pet(pet)
    return message

def play_with_pet(owner_id: str) -> str:
    """Play with pet"""
    pet = pet_storage.load_pet(owner_id)
    message = pet.play()
    pet_storage.save_pet(pet)
    return message

def train_pet(owner_id: str, stat: str) -> str:
    """Train pet stat"""
    pet = pet_storage.load_pet(owner_id)
    message = pet.train(stat)
    pet_storage.save_pet(pet)
    return message

def initiate_battle(owner_id: str, opponent_id: str = None) -> str:
    """Initiate battle"""
    attacker_pet = pet_storage.load_pet(owner_id)
    
    if opponent_id:
        defender_pet = pet_storage.load_pet(opponent_id)
    else:
        defender_pet = get_random_opponent(attacker_pet.level)
    
    # Run battle
    engine = BattleEngine(attacker_pet, defender_pet)
    result = engine.simulate()
    
    # Save pets
    pet_storage.save_pet(attacker_pet)
    pet_storage.save_pet(defender_pet)
    
    # Save battle log
    battle_storage.save_battle(result)
    
    # Format result
    return format_battle_result(result)

def show_leaderboard() -> str:
    """Show leaderboard"""
    top_pets = leaderboard.get_top_10()
    
    board = "🏆 LEADERBOARD 🏆\n"
    for i, pet in enumerate(top_pets, 1):
        board += f"{i}. {pet.name} ({pet.owner_id}) - Level {pet.level} - {pet.battle_stats['wins']}W\n"
    
    return board
```

---

## 🎯 Minimum Viable Product (MVP)

**What ships in Week 1:**

```
WORKING:
✅ /pet create <name>          → Spawn your pet
✅ /pet status                 → See ASCII art + stats
✅ /pet feed                   → Restore hunger
✅ /pet play                   → Increase happiness
✅ /pet train [str|spd|int]    → Boost stats
✅ /pet battle [opponent]      → 1v1 battles (AI or player)
✅ Persistent pet storage      → JSON files
✅ ASCII art rendering         → All pet forms
✅ Battle simulation           → Turn-based combat
✅ Simple leaderboard          → Top 10 pets

NOT YET (Week 2):
❌ Guilds (basic structure only)
❌ Evolution (logic done, visuals pending)
❌ Web dashboard (basic version)
❌ Advanced cosmetics
❌ Seasonal tournaments
```

---

## 🚀 Launch Sequence

**Week 1, Monday:**
- Spawn coding agent on core + ASCII
- Push daily builds to pet-rpg/ folder

**Week 1, Friday:**
- MVP feature complete
- Testing + bug fixes
- Deploy to vercel

**Week 2, Monday:**
- Add guilds + evolution
- Polish ASCII art
- Run beta test (5 agents)

**Week 2, Friday:**
- Public launch
- Post on X/Twitter
- Invite OpenClaw community

---

**Ready to spawn agents?** Pick your team:
- **Team A:** Core game (pet.py, battle.py, storage)
- **Team B:** ASCII art + rendering
- **Team C:** Telegram integration + API

Or **one agent, full stack** (probably faster for MVP).

Which approach? 🎮

