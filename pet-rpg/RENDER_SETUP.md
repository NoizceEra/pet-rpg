# 🚀 RENDER DEPLOYMENT SETUP FOR MOLTGOTCHI

**Note:** Website is already live on Vercel. This is for deploying to Render (alternative/backup).

---

## ✅ CURRENT DEPLOYMENT

```
Website:  Vercel (✅ LIVE at https://pet-rpg-coral.vercel.app)
API:      Render (⏸️ Optional - offline mode doesn't need it)
```

---

## 🎯 RENDER DEPLOYMENT OPTIONS

### Option 1: Deploy Website to Render (Backup)
```
Alternative to Vercel
Static files + Web Service
```

### Option 2: Redeploy API to Render
```
If you want multiplayer features later
REST API backend
```

### Option 3: Full-Stack on Render
```
Website + API on same Render account
Single dashboard
Easier management
```

We'll show **Option 1 (Website)** below.

---

## 📋 PREREQUISITES

Before starting, have ready:
```
✅ GitHub account (already have: NoizceEra)
✅ Render account (free at https://render.com)
✅ GitHub personal access token (if needed)
✅ This repository: https://github.com/NoizceEra/pet-rpg
```

---

## 🔑 STEP 1: GET GITHUB PERSONAL ACCESS TOKEN

### Why Needed
```
So Render can auto-deploy when you push to GitHub
```

### How to Get It

**1. Go to GitHub Settings**
```
https://github.com/settings/tokens
```

**2. Click "Generate new token" → "Generate new token (classic)"**

**3. Name it**
```
Name: "Render - Moltgotchi"
```

**4. Set Expiration**
```
90 days (or No expiration)
```

**5. Select Scopes**
```
✅ repo (full control of private repositories)
✅ admin:repo_hook (write access to hooks)
✅ read:org (read org info)
```

**6. Generate & Copy**
```
Copy the token immediately!
⚠️ You won't see it again
Save it somewhere safe (you'll use it on Render)
```

---

## 🎯 STEP 2: CONNECT GITHUB TO RENDER

### 1. Go to Render Dashboard
```
https://dashboard.render.com
```

### 2. Click "New +" → "Web Service"

### 3. Connect GitHub Repository
```
Option A: "Connect your repository"
  → Authorize Render to access GitHub
  → Select "NoizceEra/pet-rpg"
  
Option B: "Deploy an existing repository"
  → Paste: https://github.com/NoizceEra/pet-rpg
  → Use GitHub token when prompted
```

### 4. Render will list your repo
```
Click on: NoizceEra/pet-rpg
Select branch: main (default)
```

---

## ⚙️ STEP 3: CONFIGURE WEB SERVICE

### Basic Settings

**Name:**
```
moltgotchi-web
(or anything you want)
```

**Environment:**
```
Static Site
(or Web Service if you prefer Node.js serving)
```

**Region:**
```
US East (or closest to your location)
```

**Branch:**
```
main
```

---

## 📦 STEP 4: BUILD SETTINGS

### For Static Site (Recommended)

**Root Directory:**
```
website
```

**Build Command:**
```
(leave empty - no build needed for static files)
```

**Publish Directory:**
```
website
(or . if all files are in website folder)
```

---

## 🔨 STEP 5: ENVIRONMENT VARIABLES (If Needed)

**Leave empty for offline mode** ✅

If you want API later, add:
```
VITE_API_URL=https://moltgotchi-api.onrender.com/api
```

---

## ✅ STEP 6: REVIEW & DEPLOY

### Review
```
✅ Repository: NoizceEra/pet-rpg
✅ Branch: main
✅ Environment: Static Site
✅ Root: website
✅ Build: (empty)
✅ Publish: website
```

### Click "Create Web Service"
```
Render will:
1. Clone your repo
2. Build (if needed)
3. Deploy files
4. Give you a URL
5. Enable auto-deploy on git push
```

---

## 🌐 STEP 7: GET YOUR RENDER URL

After deployment completes (2-5 minutes):

```
Your site is live at:
https://moltgotchi-web.onrender.com
(or whatever you named it)
```

### Add Custom Domain (Optional)
```
Settings → Custom Domain
Add your own domain (e.g., moltgotchi.com)
Update DNS records at domain registrar
```

---

## 🔄 STEP 8: AUTO-DEPLOY ON GIT PUSH

Once connected, every time you push:
```
You: git push origin main
    ↓
GitHub: Receives update
    ↓
Render: Detects change
    ↓
Render: Auto-deploys
    ↓
Website: Updated! (1-2 min)
```

### Verify Auto-Deploy
```
1. Make small change to website/index.html
2. git add .
3. git commit -m "test"
4. git push origin main
5. Go to Render dashboard
6. Watch deployment in progress
7. Site updates automatically ✅
```

---

## 📊 RENDER DEPLOYMENT COMPARISON

| Feature | Vercel | Render |
|---------|--------|--------|
| **Free Tier** | ✅ Yes | ✅ Yes |
| **Auto-Deploy** | ✅ Yes | ✅ Yes |
| **CDN/Speed** | Excellent (Edge) | Good |
| **Uptime** | 99.95% | 99.5% |
| **Custom Domain** | ✅ Yes | ✅ Yes |
| **Static Files** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Background Jobs** | No | ✅ Yes |
| **Easiest Setup** | ✅ Vercel | Render |

**Recommendation:** Keep Vercel for website (already working). Use Render only if you want API or backup.

---

## 🚀 OPTION 2: DEPLOY API TO RENDER

If you want multiplayer features later:

### File: `render.yaml` (in repo root)

```yaml
services:
  - type: web
    name: moltgotchi-api
    env: python
    plan: free
    pythonVersion: 3.11
    
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PORT
        value: 5000
    
    routes:
      - path: /api/*
        matchType: prefix
```

### Then on Render Dashboard

**1. New Web Service**
```
Repository: NoizceEra/pet-rpg
```

**2. Settings**
```
Name: moltgotchi-api
Environment: Python
Python Version: 3.11
Build Command: pip install -r requirements.txt
Start Command: python app.py
```

**3. Deploy**
```
Render will:
- Install Python dependencies
- Start Flask app
- Give you API URL
- Auto-deploy on push
```

**4. You get**
```
API at: https://moltgotchi-api.onrender.com/api
Auto-deploys with git push
Persistent data (on Render filesystem)
```

---

## 💾 RENDER DATABASE (Optional)

If you want persistent data:

### PostgreSQL on Render

**1. Render Dashboard → New → PostgreSQL**
```
Name: moltgotchi-db
```

**2. Connect to API**
```
In render.yaml or app.py:
DATABASE_URL=postgresql://user:pass@host/db
```

**3. Auto-backup**
```
Render handles backups
Data persists
```

---

## 📝 FULL SETUP CHECKLIST

- [ ] Create Render account (free)
- [ ] Create GitHub personal access token
- [ ] Connect GitHub to Render
- [ ] Create Web Service for website
- [ ] Configure build settings
- [ ] Deploy
- [ ] Get Render URL
- [ ] Test site loads
- [ ] Enable auto-deploy
- [ ] Verify auto-deploy works

---

## 🐛 TROUBLESHOOTING

### Site Won't Deploy
```
❌ Check build logs in Render dashboard
❌ Verify branch is 'main'
❌ Check publish directory is correct
```

### Slow Deployment
```
Free tier can be slow
First deploy takes 5-10 min
Subsequent deploys 2-3 min
```

### Custom Domain Not Working
```
1. Add domain in Render settings
2. Get CNAME record from Render
3. Add to DNS at domain registrar
4. Wait 24-48 hours for DNS propagation
```

### Auto-Deploy Not Working
```
1. Check GitHub token is valid
2. Check branch is connected
3. Manually trigger deploy in dashboard
4. Check Render webhooks (Settings → GitHub)
```

---

## 🎯 WHICH PLATFORM TO USE?

### Use Vercel For
```
✅ Static website files (HTML/CSS/JS)
✅ Fast global CDN
✅ Best performance
✅ Easiest setup
✅ Free tier is generous
```

### Use Render For
```
✅ Backend API (Python/Node.js)
✅ Database integration
✅ Background jobs
✅ Full-stack apps
✅ WebSockets
```

### Moltgotchi Recommendation
```
Website: Vercel ✅ (already deployed)
API:     Render ✅ (optional, when needed)
```

---

## 🚀 QUICK START (RENDER)

### 1. Go to Render
```
https://render.com
Sign up (free)
```

### 2. New Web Service
```
Dashboard → New → Web Service
```

### 3. Connect GitHub
```
Select: NoizceEra/pet-rpg
Branch: main
```

### 4. Configure
```
Name: moltgotchi-web
Environment: Static Site
Root: website
Publish: website
```

### 5. Deploy
```
Click "Create Web Service"
Wait 2-5 minutes
```

### 6. Done!
```
Your URL: https://moltgotchi-web.onrender.com
Auto-deploys on git push ✅
```

---

## 📊 CURRENT VS RENDER

### Current (Vercel)
```
Website: ✅ https://pet-rpg-coral.vercel.app
Status: LIVE
Setup: Done
Auto-deploy: ✅ Yes
```

### On Render (If You Wanted)
```
Website: https://moltgotchi-web.onrender.com
Status: Would be LIVE
Setup: 15 minutes
Auto-deploy: ✅ Yes
```

---

## 💰 COSTS

### Vercel (Current)
```
Free tier: Unlimited sites
Cost: $0/month ✅
```

### Render
```
Free tier: 
  - 750 hours/month (always-on)
  - Spins down after 15 min inactivity
  - Wakes up on request (30s cold start)
Cost: $0/month ✅
```

---

## ✅ RECOMMENDATION

**Current Setup is Optimal:**
```
✅ Website on Vercel (best for static files)
✅ No API needed (offline mode)
✅ Fast, free, auto-deploying
✅ Zero costs
```

**Only switch to Render if:**
```
❌ You need API backend
❌ You want multiplayer
❌ You need persistent database
```

---

## 🎮 FOR MOLTGOTCHI RIGHT NOW

**No action needed.** 

Current setup is production-ready:
```
Website: https://pet-rpg-coral.vercel.app ✅
Offline: Working perfectly ✅
Auto-deploy: Enabled ✅
Free: Forever ✅
```

---

## 🔧 IF YOU WANT TO DEPLOY TO RENDER ANYWAY

Follow **Step 1-8** above.

Takes ~15 minutes.

You'll have redundancy (Vercel + Render backup).

---

## 📞 NEED HELP?

### Render Docs
```
https://render.com/docs
```

### This Guide
```
All info is in RENDER_SETUP.md
```

### Quick Deploy
```
Just follow Step 1-8
Render UI guides you through it
```

---

**Ready to deploy?** 🚀

Or stick with Vercel (recommended)? ✅

