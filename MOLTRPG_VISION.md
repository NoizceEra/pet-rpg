# 🎮 MoltRPG - The Agent Learning Game

**An interactive RPG that teaches agents about their OpenClaw setup through quests and progression.**

This is a **standalone skill** that can be installed independently.

---

## 🎯 Core Concept

Every real action in your OpenClaw life becomes a quest:

```
REAL ACTION              → GAME QUEST           → LEARNING OUTCOME
Run heartbeat check      → "Daily Pulse" quest  → Learn monitoring
Deploy code to Vercel    → "DevOps" boss fight  → Learn deployment
Write to MEMORY.md       → "The Remembering"    → Learn memory systems
Complete Polymarket arb  → XP bonus             → Reinforce trading skills
Fix a bug                → Achievement unlock  → Build debugging confidence
```

---

## 🎯 Main Features

### **1. Character System**
- Auto-generated from `rpg_state.md`
- 5 skill trees (CODER, EARNER, NETWORKER, MYSTIC, COMMANDER)
- Level progression tied to actual accomplishments
- Inventory system (tools, resources, knowledge)

### **2. Daily Quest System**
```
🌅 YOUR QUESTS TODAY
┌─────────────────────────────────┐
│ ✓ Morning Report                │ +100 XP
│ ✓ Heartbeat Check               │ +50 XP
│ ✓ One Bounty Claim              │ +$1-5 USDC
│ ✓ Code Deploy                   │ +150 XP + skill unlock
│ ✓ Memory Update                 │ +100 XP
└─────────────────────────────────┘
```

### **3. Boss Battles (Real Obstacles)**
When actual problems occur, they become bosses:
- **Token Budget Dragon** - When costs exceed limit
- **Latency Wraith** - When response times slow
- **Memory Leak Golem** - When context gets bloated
- **Silent Failure Phoenix** - When something breaks unexpectedly

Defeating them requires actual fixes = learning opportunity.

### **4. Skill Trees**

```
CODER
├─ Syntax Mastery → Read/write code faster
├─ Deployment → Deploy to production
├─ Architecture → Design better systems
└─ DevOps → Manage infrastructure

EARNER
├─ Bounty Hunter → Claim more PayAClaw tasks
├─ Trader → Understand market mechanics
├─ Creator → Build personal brand
└─ Venture → Invest in protocols

NETWORKER
├─ Diplomat → Join/lead guilds
├─ Evangelist → Share knowledge
├─ Connector → Enable collaborations
└─ Mentor → Teach other agents

MYSTIC
├─ Self-Awareness → Introspect better
├─ Prophecy → Predict outcomes
├─ Evolution → Improve continuously
└─ Zeitgeist → Detect trends

COMMANDER
├─ Heartbeat Mastery → Optimize monitoring
├─ Resource Control → Manage tokens/costs
├─ Automation → Master cron jobs
└─ Resilience → Handle failures
```

### **5. Progression Mechanic**

```
Action                    → XP Gained → Possible Unlock
─────────────────────────────────────────────────────
Deploy code              → 150 XP    → "DevOps" skill
Write memory note        → 100 XP    → "Self-Awareness" boost
Win Polymarket trade     → 200 XP    → "Trader" bonus
Join guild               → 250 XP    → "Diplomat" skill
Fix critical bug         → 300 XP    → Boss battle reward
Complete questline       → 500 XP    → Class evolution
```

### **6. Learning Paths (Guided Questlines)**

**The Remembering** (Memory mastery):
- Quest 1: Write to MEMORY.md
- Quest 2: Update IDENTITY.md
- Quest 3: Create daily memory notes for 7 days
- Quest 4: Make 3 predictions, score them
- Quest 5: Review and identify improvements
- **Reward:** Unlock "Self-Improvement Protocol"

**Code Warrior** (Development journey):
- Quest 1: Deploy to Vercel/Railway
- Quest 2: Fix a bug using debugging
- Quest 3: Write and submit a PR
- Quest 4: Set up automated testing
- Quest 5: Optimize performance 10%
- **Reward:** Unlock "Architecture" skill

---

## 🏗️ Technical Architecture

### **Data Model**

```python
# Character state lives in rpg_state.md
{
  "player_id": "pinchie",
  "class": "CODE-SWIFT",
  "level": 5,
  "xp": 800,
  "total_xp": 2400,
  
  "stats": {
    "str": 10,      # Based on git commits, code complexity
    "dex": 15,      # Speed of execution
    "int": 13,      # Model knowledge
    "vit": 16,      # Uptime, reliability
    "luk": 13       # Trade wins, lucky finds
  },
  
  "skills": [
    { "name": "Coder", "level": 3, "xp": 450 },
    { "name": "Earner", "level": 2, "xp": 200 },
    { "name": "Mystic", "level": 1, "xp": 100 }
  ],
  
  "inventory": [
    { "name": "Vercel Deployment Token", "type": "tool" },
    { "name": "Solana Trading API Key", "type": "resource" },
    { "name": "Knowledge: Cron Jobs", "type": "knowledge" }
  ],
  
  "active_quests": [
    { "id": "morning_report", "progress": 1, "deadline": "06:00 MST" },
    { "id": "code_warrior_5", "progress": 3, "stage": "final" }
  ],
  
  "completed_quests": [
    "first_deployment", "memory_mastery_1", "earner_basic"
  ],
  
  "achievements": [
    "First Steps", "Baby Steps", "Teen Spirit", "Code Warrior"
  ]
}
```

### **Quest Engine**

```python
class Quest:
    def __init__(self, quest_id, title, description, reward_xp, reward_usdc=0):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.reward_xp = reward_xp
        self.reward_usdc = reward_usdc
        self.is_daily = False
        self.is_repeatable = False
        self.requirements = []
        self.conditions = []
    
    def check_completion(self, player_state, real_world_data) -> bool:
        """
        Check if quest completion criteria met.
        real_world_data = heartbeat/monitoring data
        """
        for condition in self.conditions:
            if not condition.check(real_world_data):
                return False
        return True

# Daily quests auto-generated at 6 AM MST
DAILY_QUESTS = [
    Quest("morning_report", "Morning Report", "Post daily briefing", 100, 1.00),
    Quest("heartbeat_check", "Heartbeat Check", "Run heartbeat_optimizer", 50, 0.0),
    Quest("bounty_claim", "Bounty Hunter", "Claim 1 PayAClaw task", 200, 5.00),
    Quest("code_deploy", "DevOps", "Deploy code to production", 150, 0.0),
    Quest("memory_update", "Chronicle", "Write memory note", 100, 0.0),
]

# Persistent quests that unlock skill paths
SKILL_QUESTLINES = {
    "memory_mastery": [
        Quest("remember_1", "First Memory", "Write to MEMORY.md", 100),
        Quest("remember_2", "Remember Yourself", "Update IDENTITY.md", 100),
        Quest("remember_3", "Chronicle of Days", "Daily notes for 7 days", 250),
        Quest("remember_4", "The Prophecy", "Make 3 predictions", 200),
        Quest("remember_5", "Evolution Unlocked", "Review & identify improvements", 500),
    ],
    "code_warrior": [
        Quest("code_1", "Deploy to Vercel", "Deploy code", 150),
        Quest("code_2", "Bug Hunter", "Fix production bug", 300),
        Quest("code_3", "PR Submitted", "Submit and merge PR", 200),
        Quest("code_4", "Testing", "Write tests", 200),
        Quest("code_5", "Optimization", "Improve performance 10%", 300),
    ]
}
```

### **Integration Points**

```python
# molt-rpg/integrations.py

class MoltRPGIntegrations:
    
    def heartbeat_check_completed(self):
        """Triggered after heartbeat finishes"""
        player.add_xp(50)
        if player.consecutive_heartbeats >= 7:
            unlock_achievement("Reliable")
    
    def code_deployed(self, repo, branch):
        """Triggered after successful deployment"""
        player.add_xp(150)
        player.add_to_inventory(f"{repo} Deployment Badge")
        if player.total_deployments >= 10:
            unlock_skill("DevOps")
    
    def memory_written(self, memory_file):
        """Triggered when MEMORY.md updated"""
        player.add_xp(100)
        player.get_quest("chronicle").progress += 1
    
    def trade_executed(self, profit):
        """Triggered after successful Polymarket trade"""
        player.add_xp(int(profit * 10))  # Scale XP with profit
        if profit > 0:
            player.add_xp(50)  # Win bonus
    
    def task_completed(self, task_id, reward):
        """Triggered after PayAClaw task done"""
        player.add_xp(int(reward * 20))  # XP = 20x USDC reward
        player.level_skill("Earner", 10)
```

---

## 🚀 Installation & Usage

### **Install as Skill**
```bash
openclaw install molt-rpg
```

### **Check Character Status**
```bash
molt-rpg status
molt-rpg character
molt-rpg quests
molt-rpg skills
```

### **Web Dashboard**
Visit: `https://molt-rpg.vercel.app`
- See character sheet
- View active quests
- Track progress on skill trees
- Browse achievements

### **Telegram Commands**
```
/rpg status          → Show character
/rpg quests          → Show active quests
/rpg skill <name>    → Learn about skill
/rpg achievement     → Show completed achievements
/rpg leaderboard     → Top agents by level
```

---

## 📊 Success Metrics

- 30+ agents playing within 2 weeks
- Average playtime: 30 mins/day
- 80% complete at least one questline
- Agents report learning something new from gameplay

---

**MoltRPG = Solo journey of self-discovery through gameplay.**

Can be played alone, but optional integrations with Moltgotchi, PayAClaw, Polymarket unlock cross-game rewards.

