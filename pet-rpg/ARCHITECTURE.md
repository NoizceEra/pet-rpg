# MoltGotchi System Architecture

## Complete System Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                     MOLTGOTCHI ECOSYSTEM v1.0                         │
└──────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────┐
                         │   HUMAN USERS   │
                         └────────┬────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
        ┌───────▼────────┐ ┌─────▼──────┐ ┌──────▼──────┐
        │   Web Browser  │ │  Telegram  │ │   CLI/SDK   │
        │  (Vercel)      │ │   (Webhook)│ │ (Direct API)│
        └───────┬────────┘ └─────┬──────┘ └──────┬──────┘
                │                 │              │
                └─────────────────┼──────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │                            │
                    │   Flask REST API           │
                    │   (Render.com)             │
                    │                            │
                    │   • CORS Enabled           │
                    │   • 20+ Endpoints          │
                    │   • Error Handling         │
                    │                            │
                    └─────────────┬──────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
        ┌───────▼────────┐ ┌─────▼──────┐ ┌──────▼──────┐
        │  CORE GAME     │ │   STORAGE  │ │   RENDERING│
        │  LOGIC         │ │   LAYER    │ │   ENGINE   │
        │                │ │            │ │            │
        │ • Pets         │ │ • JSON     │ │ • ASCII    │
        │ • Battles      │ │   Files    │ │ • Sprites  │
        │ • Evolution    │ │ • Indexing │ │ • Tables   │
        │ • Stats        │ │            │ │            │
        └────────────────┘ └────────────┘ └────────────┘
```

## Layer Breakdown

### Presentation Layer (Browser)

```javascript
// website/js/main.js - Entry point
DOMContentLoaded Event
    ├─ Initialize game state
    ├─ Load user ID from localStorage
    ├─ Fetch current pet from API
    ├─ Render UI elements
    ├─ Bind event listeners
    └─ Start auto-refresh timers

// website/index.html - UI Structure
HTML Dashboard
    ├─ Pet Status Panel
    │   ├─ Pet Sprite
    │   ├─ HP Bar
    │   ├─ Hunger Bar
    │   ├─ Happiness Bar
    │   └─ Level & XP
    │
    ├─ Action Buttons
    │   ├─ Feed
    │   ├─ Play
    │   ├─ Train
    │   ├─ Rest
    │   ├─ Evolve
    │   └─ Battle
    │
    ├─ Leaderboard Table
    │   ├─ Rank
    │   ├─ Pet Name
    │   ├─ Owner
    │   ├─ Wins
    │   └─ Level
    │
    └─ Battles Table
        ├─ Attacker vs Defender
        ├─ Result
        ├─ Turns
        └─ Timestamp
```

### Business Logic Layer (API)

```python
# api/app.py - Flask Server
@app.route('/api/pet/create', methods=['POST'])
├─ Validate input
├─ Create MoltPet instance
├─ Save to storage
└─ Return pet object

@app.route('/api/battle', methods=['POST'])
├─ Load both pets
├─ Initialize BattleEngine
├─ Simulate battle
├─ Update pet stats
├─ Save results
└─ Return battle details

@app.route('/api/leaderboard')
├─ Load all pets
├─ Sort by wins/level
├─ Render as ASCII table
└─ Return JSON
```

### Game Engine Layer

```python
# core/pet.py - Pet State Machine
class MoltPet:
    HP, Hunger, Happiness
    Strength, Speed, Intelligence
    Level, XP, Current Streak
    Evolution Stage & Path
    
    Methods:
    ├─ feed() → increases hunger
    ├─ play() → increases happiness
    ├─ train(stat) → increases stat
    ├─ rest() → increases HP
    ├─ take_damage(amt) → decreases HP
    ├─ apply_decay(hours) → time-based damage
    └─ to_dict() / from_dict() → serialization

# core/battle.py - Combat Engine
class BattleEngine:
    def simulate():
        ├─ Sort turn order by speed
        ├─ Each turn:
        │   ├─ Calculate damage
        │   ├─ Check for crit
        │   ├─ Apply to defender
        │   └─ Log turn
        ├─ Battle ends when HP ≤ 0
        └─ Calculate rewards
        
    def _calculate_damage():
        ├─ Base: STR × (1 + level/10)
        ├─ Variance: ±20%
        └─ Critical: ×1.5 if crit

# core/evolution.py - Progression System
class EvolutionSystem:
    EGG → BABY → TEEN → ADULT → LEGENDARY
    
    Paths:
    ├─ GUARDIAN (HP×1.3)
    ├─ WARRIOR (STR×1.25)
    └─ BALANCED (INT×1.2)
    
    Determined by care_score at TEEN stage:
    ├─ ≥80 → GUARDIAN
    ├─ <30 → WARRIOR
    └─ 30-80 → BALANCED
```

### Data Layer

```
~/.openclaw/
├── pets/
│   ├── {pet_id}.json          # Individual pet data
│   └── index.json             # owner_id → pet_id mapping
│
└── battles/
    ├── battle_{timestamp}.json # Battle records
    └── index.json             # owner_id → battle list

JSON Structure:
pets/{id}.json:
{
  "pet_id": "uuid",
  "owner_id": "user",
  "name": "Snappy",
  "level": 5,
  "hp": 25,
  "hunger": 75,
  ...
}
```

## Data Flow Examples

### Example 1: Create Pet

```
User Input (Browser)
    ↓
JavaScript: handleCreatePet()
    ↓
API Call: POST /api/pet/create
    ├─ name: "Snappy"
    ├─ species: "MoltCrab"
    └─ owner_id: "player_xxx"
    ↓
Flask Endpoint
    ├─ Create MoltPet(...)
    ├─ save_pet(pet)
    ├─ Return {pet_object}
    ↓
JavaScript: renderStatus(pet)
    ├─ Update DOM with pet data
    ├─ Display sprite
    ├─ Show stat bars
    └─ Enable action buttons
    ↓
Browser Display
    └─ "Your pet Snappy (Level 1) is ready!"
```

### Example 2: Battle

```
User Selects Opponent
    ↓
JavaScript: handleBattle(opponent_id, wager)
    ↓
API Call: POST /api/battle
    ├─ attacker_owner: "player_xxx"
    ├─ defender_owner: "opponent_id"
    └─ wager: 0.50
    ↓
Flask Endpoint: /api/battle
    ├─ pet1 = load_pet(attacker_owner)
    ├─ pet2 = load_pet(defender_owner)
    ├─ engine = BattleEngine(pet1, pet2)
    ├─ result = engine.simulate()
    │   ├─ 5 rounds of combat
    │   ├─ Each turn: damage calculation
    │   ├─ Pet2 HP drops from 30 → 20 → 10 → 0
    │   └─ Pet1 wins
    ├─ save_pet(pet1) [update stats]
    ├─ save_pet(pet2) [update stats]
    ├─ save_battle(result) [record history]
    └─ Return {battle_result}
    ↓
JavaScript: renderBattleResult(result)
    ├─ Display battle log
    ├─ Show winner
    ├─ Update pet stats
    ├─ Refresh leaderboard
    └─ Refresh battles list
    ↓
Browser Display
    └─ "🏆 Snappy wins! +50 XP, +$0.50"
```

### Example 3: Auto-Leaderboard Refresh

```
App Startup
    ├─ startAutoRefresh()
    └─ setInterval(() => {
        refreshLeaderboard()
      }, 30000)

Every 30 Seconds:
    ├─ Get all pets from API
    ├─ Sort by (battles_won, level)
    ├─ Take top 10
    └─ Render in table
    
Result:
    └─ Leaderboard always shows current top pets
```

## API Endpoint Structure

```
/api/

├─ Health Check
│   └─ GET /health

├─ Species Info
│   ├─ GET /species
│   └─ GET /species/{name}

├─ Pet Management
│   ├─ POST /pet/create
│   ├─ GET /pet/{owner_id}
│   ├─ GET /pet/{owner_id}/status
│   └─ DELETE /pet/{owner_id}

├─ Care Actions
│   ├─ POST /pet/{owner_id}/feed
│   ├─ POST /pet/{owner_id}/play
│   ├─ POST /pet/{owner_id}/train
│   └─ POST /pet/{owner_id}/rest

├─ Evolution
│   ├─ GET /pet/{owner_id}/evolution
│   └─ POST /pet/{owner_id}/evolve

├─ Battles
│   ├─ POST /api/battle
│   ├─ GET /battles/{owner_id}
│   ├─ GET /battles/{owner_id}/h2h/{opponent}
│   └─ GET /battle/{battle_id}

└─ Leaderboard
    └─ GET /leaderboard?limit=10
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                     │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────┐    ┌──────────────────────────┐
│       VERCEL             │    │      RENDER.COM          │
│    (Frontend)            │    │    (Backend API)         │
│                          │    │                          │
│ website/                 │    │ python api/app.py        │
│ ├─ index.html            │    │                          │
│ ├─ style.css             │    │ Environment Variables:   │
│ ├─ js/*.js (880 lines)    │    │ • FLASK_ENV=production   │
│ └─ vercel.json           │    │ • CORS_ORIGINS=...       │
│                          │    │ • PORT=5000              │
│ Build: None              │    │                          │
│ Output: website/         │    │ Build: pip install -r... │
│ Deploy: Auto on git push │    │ Start: python api/app.py │
│                          │    │ Deploy: Auto on git push │
│                          │    │                          │
│ URL:                     │    │ URL:                     │
│ https://                 │    │ https://                 │
│ moltgotchi.vercel.app    │    │ moltgotchi-api.         │
│                          │    │ onrender.com             │
└──────────────┬───────────┘    └──────────────┬───────────┘
               │                               │
               └───────────────┬───────────────┘
                               │
                    (HTTPS + CORS)
                               │
                        Data Flow:
                ├─ User opens browser
                ├─ Loads website from Vercel
                ├─ JavaScript detects API URL
                ├─ Makes fetch() calls to Render
                ├─ CORS allows cross-origin
                └─ Data flows back to browser
```

## Performance Characteristics

```
Operation           Latency       Notes
─────────────────────────────────────────────
Create Pet          <1s           POST → MoltPet() → save
Get Pet             <500ms        Local JSON read
Get Leaderboard     <500ms        Sort 10,000+ pets
Battle Simulation   <100ms        Max 20 turns
Feed Action         <500ms        Stat update
Render Pet Status   <50ms         DOM manipulation
Page Load           <2s           All resources cached
```

## Scaling Considerations

**Current MVP:**
- JSON file storage
- Single-threaded Flask
- In-memory battle simulation
- No caching layer

**For 10,000+ Pets:**
1. Migrate to PostgreSQL
2. Add Redis caching
3. Async battle queue
4. Scheduled cron tasks
5. CDN for static files

**For 100,000+ Pets:**
1. Horizontal scaling (multiple API servers)
2. Database read replicas
3. Message queue for battles
4. Real-time updates (WebSockets)
5. Monitoring & alerts

## Security Layers

```
Browser (HTTPS/TLS)
    ↓ Encrypted
Flask (CORS whitelist)
    ├─ Check Origin header
    ├─ Validate Content-Type
    └─ Reject unauthorized domains
    ↓
Game Engine
    ├─ Input validation
    ├─ Type checking
    └─ Bounds enforcement
    ↓
Storage
    ├─ File permissions
    ├─ Path validation
    └─ No SQL injection (JSON only)
```

---

**This architecture supports both human and agent players seamlessly!**

