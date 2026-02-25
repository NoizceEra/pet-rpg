# ⚡ Website Deployment - Action Items

**Status:** Review complete. Ready for immediate deployment.  
**Estimated Time:** 25 minutes  

---

## 🎯 DO THIS NOW (3 Steps)

### **Step 1: Replace HTML File** (1 minute)

```bash
cd pet-rpg/website

# Backup the old one
mv index.html index_BROKEN.html

# Copy the fixed one
cp index_FIXED.html index.html

# Verify
ls -la index.html  # Should exist
```

**What changed:**
- Removed old placeholder code
- Added proper modular JS initialization
- Fixed DOM element IDs and structure
- Added notification container and loader

---

### **Step 2: Test Locally** (10 minutes)

**Terminal 1: Start API**
```bash
cd pet-rpg
python api/app.py
```

Wait for:
```
[MoltGotchi] API health check passed
 * Running on http://0.0.0.0:5000
```

**Terminal 2: Open Website**
```bash
# Mac
open website/index.html

# Windows
start website\index.html

# Linux
firefox website/index.html
```

**Test These Features:**

1. ✅ **Page loads** - No errors in console (F12)
   - Should see: `[MoltGotchi] Running in LOCAL mode`
   - Should see: `[MoltGotchi] API URL: http://localhost:5000/api`

2. ✅ **Create Pet**
   - Type "Fluffy"
   - Select "MoltCrab"
   - Click "Hatch Pet"
   - Should show pet status immediately

3. ✅ **Feed Button**
   - Click "Feed"
   - Hunger bar should fill up
   - Should see success notification

4. ✅ **Play Button**
   - Click "Play"
   - Happiness should increase
   - Hunger should decrease

5. ✅ **Train Button**
   - Click "Train"
   - Modal should appear
   - Select a stat
   - Stat should increase

6. ✅ **Battle Button**
   - Click "Battle"
   - Modal should appear
   - Enter any opponent ID
   - Should attempt battle

7. ✅ **Persistence**
   - Refresh page (F5)
   - Pet should still be there
   - User ID should be same

**If All Tests Pass:** ✅ Ready for deployment

**If Something Fails:** 
- Check browser console (F12) for errors
- Verify API is running
- Check that all files are present

---

### **Step 3: Deploy to Vercel** (10 minutes)

Choose **ONE** of these options:

#### **Option A: Web UI (Easiest)**

1. Go to https://vercel.com
2. Sign up with GitHub
3. Click "New Project"
4. Select your `pet-rpg` repository
5. Configure:
   - **Framework:** Other
   - **Build Command:** `echo 'Static site'`
   - **Output Directory:** `website`
6. Click "Deploy"
7. Wait for build (2-3 min)
8. You get a URL like: `https://moltgotchi.vercel.app`

#### **Option B: CLI (Fastest)**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from project root
cd pet-rpg
vercel

# Follow prompts:
# - Connect GitHub? Yes
# - Override settings? No
# - Output directory? website
# - Deploy? Yes

# Get URL when done
```

#### **Option C: GitHub Push**

1. Connect GitHub to Vercel (one-time setup)
2. Push to GitHub: `git push origin main`
3. Vercel auto-deploys
4. Watch progress: https://vercel.com/dashboard

---

## 🔗 Step 4: Connect Website to API (5 minutes)

**After you deploy the API** (see below), update Vercel:

1. Go to Vercel dashboard
2. Select your project
3. Settings → Environment Variables
4. Add:
   ```
   VITE_API_URL=https://your-api-url
   ```
   (Replace with your actual API URL)

5. Click "Save"
6. Click "Redeploy" button
7. Wait for deployment

**Example API URLs:**
- Render: `https://moltgotchi-api.onrender.com`
- Railway: `https://moltgotchi-api-production.up.railway.app`
- Your server: `https://api.yourdomain.com`

---

## 🌐 Deploy API Backend (Choose One)

### **Option 1: Render.com (Recommended - Free)**

1. Go to https://render.com
2. Click "New Web Service"
3. Select your GitHub repo
4. Configure:
   - **Name:** `moltgotchi-api`
   - **Environment:** Python 3
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `python api/app.py`
5. Add env vars:
   ```
   FLASK_ENV=production
   PORT=5000
   CORS_ORIGINS=https://moltgotchi.vercel.app,http://localhost:3000
   ```
6. Click "Deploy"
7. Wait 5-10 min for build
8. Get URL: `https://moltgotchi-api.onrender.com`

### **Option 2: Railway.app**

1. Go to https://railway.app
2. Create new project
3. Select GitHub (connect once)
4. Select `pet-rpg` repo
5. Deploy with defaults
6. Get URL from dashboard

### **Option 3: Your Own Server**

```bash
ssh your-server

# Clone repo
git clone https://github.com/yourusername/pet-rpg.git
cd pet-rpg

# Install
pip install -r requirements.txt
pip install gunicorn

# Run
gunicorn -w 4 -b 0.0.0.0:5000 api.app:app &

# Get public URL (IP or domain + port)
```

---

## ✅ Verification Checklist

**API Deployed?**
```bash
curl https://your-api-url/api/health
# Should return: {"status":"ok"}
```

**Website Deployed?**
- Open: https://moltgotchi.vercel.app
- Should load without errors

**API Connected?**
- Open website
- Press F12 → Console
- Should see correct API URL (not localhost)
- Create pet should work

**All Features Work?**
- [ ] Create pet
- [ ] Feed pet
- [ ] Play with pet
- [ ] Train pet
- [ ] Battle opponent
- [ ] Leaderboard loads
- [ ] Data persists on refresh

---

## 🎉 YOU'RE LIVE!

If everything above works:

1. **Share the URL**
   ```
   Website: https://moltgotchi.vercel.app
   API: https://your-api-url
   ```

2. **Announce**
   ```
   🎮 MOLTGOTCHI MVP IS LIVE! 🎮
   
   Create your pet and battle others!
   https://moltgotchi.vercel.app
   
   Features:
   ✓ Pet evolution
   ✓ Battles
   ✓ Leaderboards
   ✓ Multi-platform support
   
   Play now! 🐾
   ```

3. **Monitor**
   - Check Vercel dashboard for errors
   - Check Render/Railway dashboard for API status
   - Monitor pet creation & battles

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot reach API" | API not deployed yet / URL wrong |
| "CORS error" | Add website URL to API CORS_ORIGINS |
| "Buttons don't work" | Check console (F12) for JS errors |
| "Pet won't save" | Check localStorage enabled in DevTools |
| "Website blank" | Check output directory is `website` |
| "404 on refresh" | Add rewrite rule (already in vercel.json) |

---

## 📚 Documentation

- **WEBSITE_REVIEW.md** - What was wrong and why
- **WEBSITE_DEPLOYMENT.md** - Detailed deployment guide
- **website/README.md** - Feature documentation
- **This file** - Quick action items

---

## ⏱️ Timeline

| Step | Time | Total |
|------|------|-------|
| 1. Replace HTML | 1 min | 1 min |
| 2. Test locally | 10 min | 11 min |
| 3. Deploy website | 10 min | 21 min |
| 4. Deploy API | 10 min | 31 min |
| 5. Connect & verify | 5 min | 36 min |

**Total: ~30 minutes to production**

---

## 🚀 DO IT NOW

1. Replace `index.html` with `index_FIXED.html`
2. Run `python api/app.py` and test locally
3. Deploy to Vercel (use web UI - easiest)
4. Deploy API to Render (free tier works)
5. Connect them together
6. Celebrate! 🎉

**All files are fixed and ready.** ✅

