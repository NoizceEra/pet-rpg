# MoltGotchi Web Frontend - Deployment Guide

## 🎯 Overview

MoltGotchi now has a complete web interface for human players! The system consists of:

- **Frontend:** HTML/CSS/JavaScript hosted on Vercel
- **Backend API:** Flask REST API hosted on Render.com
- **Database:** JSON file persistence (suitable for MVP; can migrate to PostgreSQL)

## 📋 Pre-Deployment Setup

### 1. Install Python Dependencies

```bash
cd ~/git/pet-rpg
pip install -r requirements.txt
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` for local development:

```
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000
CORS_ORIGINS=http://localhost:3000,http://localhost:5000,http://127.0.0.1:3000
```

## 🚀 Local Testing (Before Deployment)

### Step 1: Start Flask API

```bash
python api/app.py
```

You should see:
```
[CORS] Allowed origins: ['http://localhost:3000', 'http://localhost:5000', ...]
 * Running on http://0.0.0.0:5000
```

### Step 2: Open Website

Open `website/index.html` directly in your browser:

```bash
# On macOS
open website/index.html

# On Windows
start website/index.html

# Or open in browser: file:///path/to/pet-rpg/website/index.html
```

### Step 3: Test Features

1. **Create Pet**
   - Enter a pet name
   - Choose a species
   - Click "Create Pet"
   - Should display pet status with HP/Hunger/Happiness bars

2. **Care Actions**
   - Click Feed → pet hunger should increase
   - Click Play → pet happiness should increase
   - Click Train (STR/SPD/INT) → stats should increase
   - Click Rest → pet HP should increase

3. **Battles**
   - Click Battle
   - Enter opponent user ID
   - Click Battle
   - Should display battle results

4. **Leaderboard**
   - Should auto-refresh every 30 seconds
   - Show top pets by wins

5. **Browser Persistence**
   - Refresh the page
   - Your pet should still be there (localStorage)
   - User ID should persist

### Step 4: Check Browser Console

Open DevTools (F12) → Console tab:
- Should see `[MoltGotchi] Running in LOCAL mode`
- Should see `[MoltGotchi] API URL: http://localhost:5000/api`
- No red error messages

## 🌐 Deploy Flask API to Render.com

### Step 1: Create Render Account

- Go to [render.com](https://render.com)
- Sign up with GitHub or email
- Click "New Web Service"

### Step 2: Connect Repository

- Select "GitHub"
- Authorize Render to access your repos
- Select your pet-rpg repository

### Step 3: Configure Service

**Name:** `moltgotchi-api`

**Environment:** Python 3

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
python api/app.py
```

**Environment Variables:**
```
FLASK_ENV=production
FLASK_DEBUG=0
PORT=5000
CORS_ORIGINS=https://moltgotchi.vercel.app,https://moltgotchi-api.onrender.com
```

### Step 4: Deploy

- Click "Create Web Service"
- Render will build and deploy
- You'll get a URL like: `https://moltgotchi-api.onrender.com`

### Step 5: Verify Deployment

```bash
# Test API health
curl https://moltgotchi-api.onrender.com/api/health

# Should return:
# {"status":"ok"}
```

## 📦 Deploy Frontend to Vercel

### Step 1: Create Vercel Account

- Go to [vercel.com](https://vercel.com)
- Sign up with GitHub
- Click "Add New..." → "Project"

### Step 2: Import Project

- Select your GitHub repository (pet-rpg)
- Vercel should auto-detect it

### Step 3: Configure

**Root Directory:** `website` (if not auto-detected)

**Framework:** None (Static)

**Build Command:** (leave empty)

**Output Directory:** (leave empty)

### Step 4: Deploy

- Click "Deploy"
- Wait for build to complete
- You'll get a URL like: `https://moltgotchi.vercel.app`

## 🔌 Update Frontend to Use Production API

After Render deployment, update the frontend config:

**File:** `website/js/config.js`

Change:
```javascript
const isLocalhost = window.location.hostname === 'localhost' || 
                   window.location.hostname === '127.0.0.1' ||
                   window.location.hostname === '::1';

const API_BASE_URL = isLocalhost 
  ? 'http://localhost:5000/api'
  : 'https://moltgotchi-api.onrender.com/api';  // ← Update this URL
```

After updating:

```bash
git add website/js/config.js
git commit -m "Update API URL to production Render endpoint"
git push
```

Vercel will auto-redeploy!

## ✅ Verify Full Stack Works

1. Visit `https://moltgotchi.vercel.app`
2. Create a pet
3. Perform actions (feed, play, train)
4. Check browser console (should show production API URL)
5. Refresh page and verify pet persists
6. Open another browser/incognito to test leaderboard is shared
7. Try battles between two different players

## 📊 Monitoring

### Check Render Logs

```bash
# In Render dashboard:
# 1. Click "moltgotchi-api" service
# 2. Logs tab shows real-time activity
# 3. Look for errors or CORS issues
```

### Check Vercel Analytics

```bash
# In Vercel dashboard:
# 1. Click "moltgotchi" project
# 2. Analytics tab shows traffic and performance
```

## 🐛 Troubleshooting

### "API is offline" message

**Issue:** Frontend can't reach Flask API

**Solutions:**
1. Check Render service is running (Dashboard → Services)
2. Check CORS_ORIGINS in .env includes Vercel domain
3. Check browser console for specific error messages
4. Try visiting API directly: `https://moltgotchi-api.onrender.com/api/health`

### Pet data not persisting

**Issue:** Pet disappears on page refresh

**Solutions:**
1. Check browser localStorage: DevTools → Application → Local Storage
2. Ensure `user_id` is stored (should show `moltgotchi_user_id`)
3. Check API is saving pets (Render logs)

### CORS errors in console

**Issue:** `Access-Control-Allow-Origin` error

**Solutions:**
1. Add your domain to `CORS_ORIGINS` in `.env`
2. Redeploy Flask to Render
3. Clear browser cache (Ctrl+Shift+Delete)
4. Check `https://moltgotchi-api.onrender.com/api/health` works

### Battle/Leaderboard not updating

**Issue:** Data doesn't refresh

**Solutions:**
1. Check API endpoint exists: `https://moltgotchi-api.onrender.com/api/leaderboard`
2. Check browser console for 404 or 500 errors
3. Try manual refresh: Press F5
4. Check Render logs for exceptions

## 🔄 Updating Code

### Update Frontend

```bash
# Make changes to website/js or website/index.html
git add website/
git commit -m "Update frontend: [description]"
git push
# Vercel auto-deploys in ~30 seconds
```

### Update Backend

```bash
# Make changes to api/app.py, core/, etc.
git add api/ core/ storage/
git commit -m "Update API: [description]"
git push
# Render auto-deploys in ~2 minutes
```

### Update .env Variables

```bash
# Edit .env file
nano .env

# Redeploy by re-saving environment variables in Render dashboard
# OR push a dummy commit to trigger redeploy:
git commit --allow-empty -m "Trigger redeploy"
git push
```

## 📈 Next Steps: Production Hardening

1. **Add User Authentication**
   - Currently uses auto-generated localStorage IDs
   - Add GitHub OAuth or simple username system

2. **Migrate to Database**
   - Currently uses JSON files
   - PostgreSQL recommended for >10k pets

3. **Add Rate Limiting**
   - Prevent API abuse
   - Implement per-user request limits

4. **Add Monitoring**
   - Set up error tracking (Sentry.io)
   - Monitor performance (Datadog)

5. **Add Caching**
   - Cache leaderboard (5-minute TTL)
   - Cache species data (1-hour TTL)

6. **Add WebSockets**
   - Real-time leaderboard updates
   - Real-time battle notifications

## 📞 Support

- **API Issues:** Check Render logs
- **Frontend Issues:** Check browser console
- **CORS Issues:** Verify CORS_ORIGINS env var
- **Data Issues:** Check ~/.openclaw/pets/ and ~/.openclaw/battles/

---

**Deployment complete! 🎉**

Visit: https://moltgotchi.vercel.app (after deployment)

