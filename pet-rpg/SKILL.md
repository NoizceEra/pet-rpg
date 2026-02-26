# 🐾 Moltgotchi - Pet Battle Game Skill

**A Tamagotchi-style pet RPG where you care for digital pets and battle other players.**

## 🎮 What is Moltgotchi?

Moltgotchi is a web-based pet battle game with ASCII art, real-time stats, and local gameplay. Create a pet, care for it through feeding/training/playing, and watch it evolve as it levels up. All gameplay runs offline in your browser using localStorage.

## 🚀 Quick Start

### 1. **Visit the Website**
```
https://pet-rpg-coral.vercel.app
```

### 2. **Create Your Pet**
- Enter a pet name
- Select a species (8 available)
- Click "Hatch Pet" 🥚

### 3. **Care for Your Pet**
```
🍖 Feed    → Reduces hunger, restores HP
🎾 Play    → Increases happiness
💪 Train   → Boosts stats (Strength, Speed, Intelligence)
😴 Rest    → Recovers HP
```

### 4. **Watch It Evolve**
- **EGG** → **BABY** (Lvl 3) → **TEEN** (Lvl 10) → **ADULT** (Lvl 25) → **LEGENDARY** (Lvl 50+)

## 🌍 How It Works

```
User opens https://pet-rpg-coral.vercel.app
    ↓
Flask app (app.py) serves HTML/CSS/JS
    ↓
Browser runs offline game (localStorage)
    ↓
Pet data saved locally in browser
    ↓
Pet persists across sessions
```

**No backend required.** All gameplay is local to your browser.

## 🎯 Core Features

### **Pet Lifecycle**
- 5 evolution stages from EGG to LEGENDARY
- 8 unique species with ASCII art:
  - 🦀 MoltCrab
  - 🐉 Dragon
  - 🔥 Phoenix
  - 💪 Titan
  - ✨ Mystic
  - 👤 Shadow
  - ⭐ Gleam
  - 🌟 Nova

### **Care System**
| Action | Effect | Cost |
|--------|--------|------|
| Feed | -15 hunger, +5 HP | Energy |
| Play | +20 happiness, -10 hunger | Energy |
| Train | +1 stat (STR/SPD/INT) | Energy |
| Rest | +20 HP | None |

### **Stats**
- **Strength** (STR) - Affects damage
- **Speed** (SPD) - Affects turn order
- **Intelligence** (INT) - Affects critical chance

### **Level Progression**
- Each action grants XP
- Levels = 10% more XP required
- Max level: 50+ (LEGENDARY tier)

## 📱 How to Download & Play

### **Option 1: Play Directly (No Download)**
Just visit: https://pet-rpg-coral.vercel.app

Your pet is saved automatically in your browser.

### **Option 2: Install as OpenClaw Skill**
If you have OpenClaw installed:

```bash
# Install the skill
openclaw skills install moltgotchi

# Open the game
open https://pet-rpg-coral.vercel.app
```

### **Option 3: Run Locally**
```bash
# Clone the repository
git clone https://github.com/NoizceEra/pet-rpg.git
cd pet-rpg

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py

# Visit http://localhost:5000
```

## 💾 Data & Persistence

**Where is my pet saved?**
- Browser's localStorage
- Survives browser restarts ✅
- Lost if you clear browser data ❌
- Different browsers = different pets

**Backup your pet:**
```javascript
// In browser console:
const pet = localStorage.getItem('moltgotchi_pet_demo');
console.log(pet);  // Copy and save this JSON
```

## 🎮 Gameplay Tips

1. **Feed when hungry** - Pet performs better when well-fed
2. **Play regularly** - Happiness affects evolution path
3. **Train strategically** - Balance all stats for best battles
4. **Level up** - Higher level = stronger pet
5. **Watch for evolution** - Pet evolves automatically when ready

## 📊 Tech Stack

```
Frontend:     HTML5 + CSS3 + Vanilla JavaScript
Backend:      Python Flask (serves static files)
Deployment:   Vercel (free tier)
Storage:      Browser localStorage
```

## 🌐 Platform Integration

### **Web Dashboard**
```javascript
// Open in any browser
https://pet-rpg-coral.vercel.app
```

### **Telegram Bot Integration (Example)**
```python
import requests

@bot.message_handler(commands=['game'])
def send_game(message):
    url = "https://pet-rpg-coral.vercel.app"
    bot.send_message(
        message.chat.id, 
        f"🎮 Play Moltgotchi here: {url}"
    )
```

### **Discord Bot Integration (Example)**
```python
@bot.command()
async def game(ctx):
    embed = discord.Embed(
        title="🐾 Moltgotchi",
        description="Play here: https://pet-rpg-coral.vercel.app"
    )
    await ctx.send(embed=embed)
```

## 📖 Full Gameplay Loop

1. **Create Pet**
   - Choose name + species
   - Pet starts at Level 1, EGG stage

2. **Care for Pet**
   - Feed, Play, Train, Rest
   - Gain XP with each action
   - Pet stats increase when trained

3. **Level Up**
   - Every level requires more XP
   - Stats increase on level-up
   - Unlock evolution at key levels

4. **Evolve**
   - At Level 3 → BABY
   - At Level 10 → TEEN
   - At Level 25 → ADULT
   - At Level 50+ → LEGENDARY

5. **Repeat**
   - Keep caring for pet
   - Watch it grow stronger
   - Enjoy the journey 🐾

## 🎯 Future Features (Roadmap)

- ✅ Local gameplay (DONE)
- ✅ ASCII art (DONE)
- ✅ Pet persistence (DONE)
- 🔄 Multiplayer battles (Backend needed)
- 🔄 Global leaderboard (Backend + DB needed)
- 🔄 Trading pets (Backend needed)
- 🔄 Mobile app (React Native)

## 🔗 Links

- **Live Game:** https://pet-rpg-coral.vercel.app
- **GitHub:** https://github.com/NoizceEra/pet-rpg
- **Developer:** Pinchie 🦀

## ❓ FAQ

**Q: Will my pet be saved?**
A: Yes! In your browser's localStorage. Clear your browser data and it's gone.

**Q: Can I play with friends?**
A: Not yet - multiplayer coming when backend is deployed.

**Q: Can I transfer my pet?**
A: Not yet - future feature.

**Q: Is there a cost?**
A: No! Completely free. Forever.

**Q: Why offline?**
A: Simple deployment, zero latency, works anywhere. Backend coming soon!

## 🚀 Deploy Your Own Version

```bash
# Fork the GitHub repo
git clone https://github.com/YOUR_USERNAME/pet-rpg.git

# Deploy to Vercel
vercel --prod

# Your game is now live!
```

---

**Play Moltgotchi: Care, Train, Evolve, Win.** 🐾

