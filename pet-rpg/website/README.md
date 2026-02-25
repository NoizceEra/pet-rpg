# MoltGotchi Web Frontend

Modern, responsive web interface for MoltGotchi pet-RPG game.

## 📁 Structure

```
website/
├── index.html          # Main dashboard UI (HTML structure)
├── style.css           # Complete dark theme styling
├── js/
│   ├── config.js       # Environment & constants config
│   ├── api.js          # API client wrapper
│   ├── state.js        # Game state management
│   ├── ui.js           # DOM manipulation & rendering
│   └── main.js         # App initialization & event binding
├── vercel.json         # Vercel deployment config
└── README.md           # This file
```

## 🚀 Quick Start

### Local Development

```bash
# 1. Start Flask API
python api/app.py

# 2. Open website (from project root)
open website/index.html
# or open in browser: file:///path/to/pet-rpg/website/index.html

# 3. Create a pet and start playing!
```

### Production Deployment

See [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) for complete instructions.

## 🎮 Features

- ✅ **Pet Creation** - Choose name and species
- ✅ **Care System** - Feed, play, train, rest
- ✅ **Evolution** - Evolve pets through stages
- ✅ **Battles** - PvP combat system
- ✅ **Leaderboard** - Real-time rankings
- ✅ **Persistence** - Browser localStorage for user ID
- ✅ **Responsive Design** - Works on desktop and mobile
- ✅ **Dark Theme** - Neon aesthetic

## 📚 JavaScript Modules

### `config.js` (120 lines)

Configuration and constants:
- API endpoint detection (localhost vs production)
- UI timing constants (refresh intervals, timeouts)
- Storage key names
- Species, stats, and evolution data
- Emoji definitions

**Exports:**
- `API_BASE_URL` - Auto-detected API endpoint
- `STORAGE_KEYS` - localStorage key names
- `UI_CONFIG` - Timing and limits
- `SPECIES`, `STAT_TYPES`, `EVOLUTION_STAGES`

### `api.js` (175 lines)

REST API client wrapper:

```javascript
const api = new APIClient(API_BASE_URL);

// Pet management
await api.createPet(userId, name, species);
await api.getPet(userId);
await api.deletePet(userId);

// Care actions
await api.feedPet(userId);
await api.playPet(userId);
await api.trainPet(userId, stat);
await api.restPet(userId);

// Evolution
await api.checkEvolution(userId);
await api.getEvolutionProgress(userId);

// Battles
await api.startBattle(attackerId, defenderId, wager);
await api.getBattles(userId, limit);
await api.getHeadToHead(userId, opponentId);

// Info
await api.getLeaderboard(limit);
await api.getSpecies();
```

All methods include:
- Automatic timeout handling
- Error messages
- JSON request/response handling

### `state.js` (143 lines)

Global game state management:

```javascript
const gameState = new GameState();

gameState.userId;           // Current player ID
gameState.currentPet;       // Pet object or null
gameState.isLoading;        // Loading flag
gameState.isOnline;         // Online status

gameState.setPet(pet);
gameState.getPet();
gameState.setLoading(true);
gameState.addNotification(msg, type);
gameState.setOnline(false);
```

### `ui.js` (339 lines)

DOM manipulation and event handling:

```javascript
// Rendering
renderPet(pet);
renderStatus(pet);
renderLeaderboard(pets);
renderBattles(battles);

// Notifications
showNotification(message, type); // 'success', 'error', 'info', 'warning'
setLoading(show);

// Event handlers (tied to button clicks)
handleCreatePet();
handleFeed();
handlePlay();
handleTrain(stat);
handleRest();
handleBattle(opponentId, wager);
handleEvolution();

// Data refresh
refreshLeaderboard();
refreshBattles();

// Sections
showCreatePetUI();
showPetDashboard();
```

### `main.js` (196 lines)

Application initialization and orchestration:

```javascript
initializeApp();        // Main entry point
populateSpeciesDropdown();
bindEventListeners();   // Wire up all buttons
startAutoRefresh();     // Start 30s leaderboard refresh
stopAutoRefresh();      // Cleanup on unload
```

Handles:
- DOMContentLoaded event
- Online/offline detection
- Auto-refresh timers
- Window unload cleanup

## 🎨 Styling

`style.css` (295 lines) provides:
- **Color Scheme:** Dark (#0a0e27) with cyan (#00ffcc) and magenta (#ff00ff) accents
- **Responsive Grid:** 2-column desktop, 1-column mobile
- **Animations:** Fade-in, pulse effects, hover transitions
- **Components:** Buttons, cards, tables, modals, stat bars
- **Font:** Monospace (Courier New) for retro aesthetic

No CSS frameworks (Tailwind, Bootstrap) - pure custom CSS for minimal dependencies.

## 🔌 API Integration

The frontend communicates with Flask API at:

**Local:** `http://localhost:5000/api`
**Production:** `https://moltgotchi-api.onrender.com/api` (configurable)

### Auto-Refresh Behavior

- **Leaderboard:** Every 30 seconds (configurable via `UI_CONFIG.LEADERBOARD_REFRESH`)
- **Battles:** Every 10 seconds (only when visible)
- **Pet Status:** Manual refresh or on action response

## 🔍 Debugging

### Browser Console

```javascript
// Check API configuration
console.log(API_BASE_URL);           // http://localhost:5000/api
console.log(gameState.userId);       // player_xxx_yyy
console.log(gameState.currentPet);   // {pet object}
```

### Network Tab

- Monitor all fetch requests to API
- Check response status codes
- Verify request/response payloads

### LocalStorage

DevTools → Application → Local Storage:
- `moltgotchi_user_id` - Your player ID
- `moltgotchi_current_pet` - Cached pet data

## 🚨 Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "API is offline" | Flask not running | Start Flask: `python api/app.py` |
| Pet doesn't persist | localStorage cleared | Check DevTools → Application |
| CORS error | Domain not in whitelist | Update CORS_ORIGINS in .env |
| Buttons don't work | JavaScript error | Check browser console (F12) |
| Leaderboard blank | API returns empty | Create pets and battles first |

## 📱 Mobile Support

The frontend is fully responsive:
- Touch-friendly buttons
- Optimized viewport
- Readable on small screens

Test with DevTools device emulation (Ctrl+Shift+M).

## ♿ Accessibility

- Semantic HTML structure
- ARIA labels on interactive elements
- Color contrast meets WCAG AA
- Keyboard navigation support

## 🔐 Security

- No sensitive data in localStorage
- User ID is public (stateless)
- All API calls over HTTPS in production
- CORS prevents cross-origin abuse
- No authentication yet (local dev only)

## 🛣️ Roadmap

- [ ] User authentication (GitHub OAuth)
- [ ] Dark/light mode toggle
- [ ] Pet profile pages
- [ ] Battle replay viewer
- [ ] PvP tournament brackets
- [ ] In-game chat
- [ ] Mobile app (React Native)

## 📄 License

Same as parent project

---

**Status:** ✅ Ready for production deployment

See [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) for deployment instructions.

