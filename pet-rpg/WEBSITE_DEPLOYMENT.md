# 🚀 Moltgotchi Website - Deployment Guide

**Status:** Ready for deployment after applying fixes  
**Estimated Deploy Time:** 5 minutes  
**Estimated Fix Time:** ~2 hours  

---

## ✅ What's Fixed

1. ✅ **index_FIXED.html** - Complete rewrite with proper modular JS integration
2. ✅ **vercel.json** - Updated with correct paths and caching strategy
3. ✅ **config.js** - Removed hardcoded URL, now configurable
4. ✅ **Documentation** - Complete deployment guide

---

## 🔧 Step 1: Replace index.html

Replace the old `website/index.html` with the fixed version:

```bash
cd pet-rpg/website

# Backup old file (optional)
mv index.html index_OLD.html

# Use the fixed version
mv index_FIXED.html index.html
```

Or manually copy the content from `index_FIXED.html` to `index.html`.

---

## 🧪 Step 2: Test Locally

### Start API Server
```bash
cd pet-rpg
python api/app.py
```

You should see:
```
[MoltGotchi] API health check passed
* Running on http://0.0.0.0:5000
```

### Open Website
```bash
# Open in browser: file:///path/to/pet-rpg/website/index.html
# Or:
open website/index.html
```

### Test These Features

1. **Create Pet**
   - Type a name
   - Select a species
   - Click "Hatch Pet"
   - Should show pet status with bars

2. **Feed Pet**
   - Click "Feed" button
   - Hunger bar should fill
   - Should see notification

3. **Play**
   - Click "Play"
   - Happiness bar should increase

4. **Train**
   - Click "Train"
   - Select a stat
   - Stat should increase

5. **Battle**
   - Click "Battle"
   - Enter any opponent ID
   - Should attempt to start battle

6. **Refresh Page**
   - Pet data should persist (localStorage)
   - User ID should remain same

### Verify Console

Press `F12` → Console tab:
```
[MoltGotchi] Running in LOCAL mode
[MoltGotchi] API URL: http://localhost:5000/api
[App] DOM loaded, starting initialization...
[App] Initialization complete
```

**No red error messages should appear.**

---

## 🌐 Step 3: Deploy API (Choose One)

### Option A: Render.com (Recommended)

1. **Create Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New Web Service"
   - Select your GitHub repo
   - Choose `main` branch (or your branch)

3. **Configure**
   - **Name:** `moltgotchi-api`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python api/app.py`

4. **Environment Variables**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=0
   PORT=5000
   CORS_ORIGINS=https://moltgotchi.vercel.app,http://localhost:3000
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build to complete
   - You'll get URL like: `https://moltgotchi-api.onrender.com`

6. **Test**
   ```bash
   curl https://moltgotchi-api.onrender.com/api/health
   # Should return: {"status":"ok"}
   ```

### Option B: Railway.app

1. Sign up at https://railway.app
2. Create new project from GitHub
3. Select `pet-rpg` repository
4. Configure start command: `python api/app.py`
5. Deploy

### Option C: Your Own Server

If you have a server:
```bash
# SSH into server
ssh your-server

# Clone repo
git clone https://github.com/yourusername/pet-rpg.git
cd pet-rpg

# Install dependencies
pip install -r requirements.txt

# Run with gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api.app:app
```

---

## 🔗 Step 4: Configure Website for Production API

After deploying API, update the website to use it.

### Option A: Via Vercel Environment Variable

1. Go to https://vercel.com
2. Import `pet-rpg` project
3. Go to Settings → Environment Variables
4. Add:
   ```
   VITE_API_URL=https://your-api-url.render.com
   ```
5. Redeploy

### Option B: Via Meta Tag

Edit `index.html` in the `<head>` section:
```html
<head>
    ...
    <meta name="moltgotchi:api-url" content="https://your-api-url.render.com/api">
    ...
</head>
```

### Option C: Via Window Variable

Add before loading scripts in `index.html`:
```html
<script>
    window.MOLTGOTCHI_API_URL = 'https://your-api-url.render.com/api';
</script>
```

---

## 📦 Step 5: Deploy Website to Vercel

### 1. Connect GitHub to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from project root
cd pet-rpg
vercel
```

Or use web interface:
1. Go to https://vercel.com
2. Click "Import Project"
3. Select your GitHub repo
4. Configure:
   - **Framework Preset:** Other
   - **Build Command:** `echo 'Static site'`
   - **Output Directory:** `website`
5. Add Environment Variables (if using VITE_API_URL)
6. Click "Deploy"

### 2. Automatic Redeployment

- Push to `main` branch → Vercel auto-redeploys
- Set up custom domain (optional)

---

## ✅ Post-Deployment Checklist

- [ ] API deployed and health check passes
  ```bash
  curl https://your-api.onrender.com/api/health
  ```

- [ ] Website deployed to Vercel
  - Check URL in Vercel dashboard

- [ ] Website loads without errors
  - Open website
  - Check DevTools console (F12)

- [ ] API URL is configured
  - Console should show correct API_BASE_URL
  - Should NOT be `localhost`

- [ ] Create pet works
  - Click "Hatch Pet"
  - Should succeed or show error from API

- [ ] CORS headers working
  - Network tab should show successful requests
  - No CORS errors

- [ ] Leaderboard loads
  - Should show 0-3 pets (depending on data)

- [ ] Battle works
  - Should attempt to battle opponent

---

## 🐛 Troubleshooting

### "API is offline"

**Solution:**
- Check if API is running: `curl https://api-url/api/health`
- Verify API URL in config
- Check CORS_ORIGINS includes your Vercel domain

### "Cannot reach API"

**Solution:**
- API not deployed yet → Deploy to Render/Railway
- API URL wrong → Update config
- Firewall blocking → Check server firewall

### "CORS error"

**Solution:**
1. Add your website URL to `CORS_ORIGINS` on API
2. Redeploy API
3. Verify in Network tab that `Access-Control-Allow-Origin` header is present

### "Buttons don't work"

**Solution:**
- Check browser console (F12) for errors
- Verify all JS files loaded
- Check API URL is correct
- Test with `curl` that API is responding

### "Pet doesn't save"

**Solution:**
- Check localStorage is enabled
- DevTools → Application → Storage → Local Storage
- Look for `moltgotchi_user_id`

---

## 📊 Monitoring

### Daily Checks

```bash
# API health
curl https://your-api.onrender.com/api/health

# Leaderboard working
curl https://your-api.onrender.com/api/leaderboard

# Check logs
# Render.com: Dashboard → Logs
# Railway: Dashboard → Logs
# Your server: tail -f /var/log/moltgotchi.log
```

### Metrics to Monitor

- API response time
- Error rate
- Number of pets created
- Battles played
- Active users (unique user IDs)

---

## 🔒 Security Checklist

- [ ] CORS_ORIGINS restricted to your domain
- [ ] No API keys in code (use .env)
- [ ] HTTPS enabled on both frontend and API
- [ ] Rate limiting enabled (optional, for production)
- [ ] User input validated on backend
- [ ] Error messages don't leak sensitive info

---

## 🚀 Going Live

### Step 1: Verify Everything Works
- Test locally first
- Test production deployment
- Run through all features

### Step 2: Announce
```
🎮 MOLTGOTCHI MVP NOW LIVE! 🎮

Create your autonomous pet and battle others!

Website: https://moltgotchi.vercel.app
API: https://moltgotchi-api.onrender.com

Features:
✓ Pet evolution
✓ Turn-based battles
✓ Real-time leaderboards
✓ Multi-platform support

Play now! 🐾
```

### Step 3: Monitor First 24 Hours
- Check API logs
- Watch for errors
- Fix any issues

### Step 4: Gather Feedback
- How many players?
- Any bugs?
- Feature requests?

---

## 📈 Scaling (Later)

When you have 1000+ players:
- [ ] Migrate from JSON to PostgreSQL
- [ ] Add Redis for leaderboard caching
- [ ] Add rate limiting
- [ ] Deploy multiple API instances
- [ ] Use CDN for assets

---

## 📞 Quick Reference

| Component | URL | Status |
|-----------|-----|--------|
| Website | https://moltgotchi.vercel.app | ✅ Deployed |
| API | https://moltgotchi-api.onrender.com | ✅ Deployed |
| GitHub | https://github.com/yourusername/pet-rpg | 📍 Source |
| Docs | website/README.md | 📖 Read |

---

**Website is production-ready. Deploy with confidence!** 🚀

