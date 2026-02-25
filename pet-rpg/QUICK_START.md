# MoltGotchi - Quick Start Guide

Get MoltGotchi running locally in 5 minutes!

## ⚡ Local Setup

### 1. Install Dependencies

```bash
cd ~/path/to/pet-rpg
pip install -r requirements.txt
```

### 2. Start Flask API

```bash
python api/app.py
```

Expected output:
```
[CORS] Allowed origins: ['http://localhost:3000', 'http://localhost:5000', ...]
 * Running on http://0.0.0.0:5000
```

### 3. Open Website

```bash
# macOS
open website/index.html

# Windows
start website/index.html

# Linux
xdg-open website/index.html
```

Or manually open in browser: `file:///path/to/pet-rpg/website/index.html`

### 4. Create Your First Pet

1. Enter a pet name (e.g., "Snappy")
2. Choose a species (e.g., "MoltCrab")
3. Click **"Create Pet"**
4. Done! You should see your pet's status panel

## 🎮 Try These Actions

```
Feed → Hunger increases
Play → Happiness increases  
Train → Stats increase
Rest → HP increases
Battle → Fight another player
```

To battle another pet, you need another player ID. Try using:
- Different browser tab (incognito mode)
- Different device
- Different browser

## 🚀 Deploy to Production

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for:
- Deploying Flask API to Render.com
- Deploying Frontend to Vercel
- Setting up environment variables
- Verifying production setup

## 🐛 Troubleshooting

### "Cannot load script files" (404 errors)

**Problem:** Scripts not found when opening index.html

**Fix:** Verify directory structure:
```
pet-rpg/
  website/
    index.html
    style.css
    js/
      ├─ config.js
      ├─ api.js
      ├─ state.js
      ├─ ui.js
      └─ main.js
```

### "API is offline"

**Problem:** Cannot reach Flask API

**Check:**
1. Is Flask running? `python api/app.py`
2. Check console: Should see `Running on http://0.0.0.0:5000`
3. Try direct API call: `curl http://localhost:5000/api/health`

### "Cannot create pet"

**Problem:** POST request fails

**Check console (F12 → Console):**
- Look for network errors
- Verify API_BASE_URL shows `http://localhost:5000/api`
- Check Flask logs for stack trace

### Pet doesn't persist after refresh

**Problem:** Pet disappears on page reload

**Solutions:**
1. Check DevTools → Application → Storage → Local Storage
2. Look for `moltgotchi_user_id` key
3. Check browser allowed localStorage (not in private mode)

## 📝 Common Tasks

### Create a Pet Programmatically

```bash
curl -X POST http://localhost:5000/api/pet/create \
  -H "Content-Type: application/json" \
  -d '{
    "owner_id": "test_user",
    "name": "MyPet",
    "species": "Dragon"
  }'
```

### Get Pet Status

```bash
curl http://localhost:5000/api/pet/test_user
```

### Start a Battle

```bash
curl -X POST http://localhost:5000/api/battle \
  -H "Content-Type: application/json" \
  -d '{
    "attacker_owner": "player1",
    "defender_owner": "player2",
    "wager": 0.5
  }'
```

### Get Leaderboard

```bash
curl http://localhost:5000/api/leaderboard?limit=10
```

## 🔍 Check API Health

```bash
curl http://localhost:5000/api/health
```

Should return:
```json
{
  "status": "ok"
}
```

## 📚 Learn More

- **System Overview:** [SYSTEM_SUMMARY.md](./SYSTEM_SUMMARY.md)
- **Production Deploy:** [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Frontend Details:** [website/README.md](./website/README.md)
- **API Documentation:** In [api/app.py](./api/app.py) docstring

## 🎯 What's Included

| Component | Status | Location |
|-----------|--------|----------|
| Game engine | ✅ | `core/` |
| REST API | ✅ | `api/app.py` |
| Web UI | ✅ | `website/` |
| Telegram bot | ✅ | `telegram/commands.py` |
| Data storage | ✅ | `storage/` |
| Tests | ✅ | `test_game.py` |

## ⚡ Pro Tips

1. **Use DevTools Console** - Check `gameState.userId` to verify you're logged in
2. **Check API Logs** - Flask output shows what requests are being made
3. **Test Multiple Players** - Open in incognito tab to test battles
4. **Monitor Browser Network** - DevTools → Network tab to debug API calls
5. **Reset Everything** - Delete `~/.openclaw/` folder to start fresh

## 🚀 Next Steps After Setup

1. ✅ Create a pet
2. ✅ Feed and play with it
3. ✅ Create another pet (different tab/browser)
4. ✅ Battle between pets
5. ✅ Check leaderboard
6. ✅ Deploy to production!

---

**All set! Happy gaming! 🐾**

Questions? Check [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) or [SYSTEM_SUMMARY.md](./SYSTEM_SUMMARY.md)

