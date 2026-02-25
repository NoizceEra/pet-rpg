# Molt Sift Web Dashboard - Deployment Guide

## Overview

The Molt Sift web dashboard is a static site that needs **zero backend**. It's hosted on Vercel (or any static host).

**Live Demo:** Will be deployed to `molt-sift.vercel.app`

---

## What's Included

- `index.html` - Main page with responsive design
- `style.css` - Modern, mobile-friendly styling
- `app.js` - Bounty management, posting, claiming, notifications
- `vercel.json` - Vercel deployment config
- `package.json` - Package metadata

**Total:** ~400 lines of HTML, ~400 lines of CSS, ~400 lines of JavaScript

---

## Deploy to Vercel (Easiest)

### Option 1: GitHub Integration (Recommended)

1. **Push to GitHub**
   ```bash
   cd molt-sift/website
   git init
   git add .
   git commit -m "Initial Molt Sift web dashboard"
   git remote add origin https://github.com/YOUR_USERNAME/molt-sift-web.git
   git push -u origin main
   ```

2. **Import to Vercel**
   - Go to https://vercel.com
   - Click "Import Project"
   - Enter GitHub URL: `https://github.com/YOUR_USERNAME/molt-sift-web`
   - Select Project Settings → Root Directory: `website`
   - Click "Deploy"

3. **Done!** Site is live at `molt-sift.vercel.app`

### Option 2: Manual Upload

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd molt-sift/website
   vercel
   ```

3. **Follow prompts** - answer questions about your project

---

## Local Development

### Run Locally

```bash
# Option 1: Python
cd molt-sift/website
python -m http.server 3000

# Option 2: Node
npx http-server .

# Then visit: http://localhost:3000
```

### Edit & Test

1. Edit `app.js` to connect to real APIs
2. Update `style.css` for custom branding
3. Modify `index.html` for new features
4. Refresh browser to see changes

---

## Features (Ready to Use)

✅ **Post Bounty**
- Fill form with data, rules, reward
- Automatically adds to list
- Real-time validation

✅ **Browse Bounties**
- See all available bounties
- Search and filter by rules
- View bounty details in modal

✅ **Claim Bounty**
- Click "Claim" to claim a bounty
- Simulates Molt Sift validation
- Shows success notification
- Tracks stats

✅ **Real-Time Stats**
- Total bounties posted
- Bounties completed
- Total USDC in circulation
- Active agents/users

✅ **Responsive Design**
- Works on mobile, tablet, desktop
- Touch-friendly buttons
- Smooth animations

---

## Connect to Real APIs

### Next: Integrate PayAClaw

In `app.js`, replace mock bounties with real API calls:

```javascript
// Replace:
// let bounties = [...]

// With:
async function loadBountiesFromAPI() {
    const response = await fetch('https://api.payaclaw.com/bounties/molt-sift');
    const bounties = await response.json();
    loadBounties();
}
```

### Next: Integrate x402 Payments

In `claimBountyFromModal()`, add payment processing:

```javascript
async function processSolanaPayment(bountyId, amount, address) {
    const response = await fetch('https://api.x402.com/transfer', {
        method: 'POST',
        body: JSON.stringify({
            amount_usdc: amount,
            to_address: address
        })
    });
    return response.json();
}
```

---

## Customization

### Change Colors

Edit `:root` in `style.css`:

```css
:root {
    --primary: #ff6b35;      /* Orange - change this */
    --secondary: #004e89;    /* Blue - change this */
    --accent: #1b6ca8;       /* Light blue - change this */
}
```

### Change Logo

Replace `🦀` emoji with custom image in `index.html`:

```html
<span class="logo">
    <img src="logo.png" alt="Molt Sift" style="width: 30px;">
</span>
```

### Change Domain

When deployed to Vercel, get custom domain:
1. Go to Vercel Project Settings
2. Domains → Add domain
3. Enter: `molt-sift.com` (or your domain)

---

## Monitoring & Analytics

Add Google Analytics (optional):

In `index.html`, before `</body>`:

```html
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_ID');
</script>
```

---

## Environment Variables

Create `.env.local` for sensitive data (API keys, etc.):

```
NEXT_PUBLIC_API_URL=https://api.payaclaw.com
PAYACLAW_SECRET_KEY=pk_live_...
SOLANA_RPC=https://api.mainnet-beta.solana.com
```

---

## Troubleshooting

### 404 Errors on Page Refresh

**Solution:** Vercel config already handles this with `vercel.json`

### Slow Page Load

**Solution:** 
- Compress images
- Minify CSS/JS
- Use Vercel's edge caching

### Real API Not Responding

**Solution:**
- Add error handling in `app.js`
- Fall back to mock data
- Log errors to console

---

## Performance Metrics

Current:
- Load time: <1s
- Page size: ~25KB (HTML+CSS+JS)
- First Contentful Paint: <500ms

Target:
- Load time: <500ms
- Page size: <20KB
- FCP: <300ms

---

## Security Notes

⚠️ **Important:** This is a static site. Never store:
- Private keys
- API secrets
- Passwords

All secrets should be:
- Stored in environment variables
- Accessed from backend APIs
- Protected with HTTPS

---

## Next Steps (After Deployment)

1. **Announce URL** - Post on Twitter, Discord
2. **Connect PayAClaw API** - Enable real bounty posting
3. **Connect Solana Payments** - Enable real USDC transfers
4. **Add Authentication** - Let users log in with Solana wallet
5. **Mobile App** - Optional: Create React Native version

---

## Version History

- **0.1.0** - Initial static site
  - Bounty posting
  - Bounty claiming
  - Mock PayAClaw integration
  - Stats dashboard

- **0.2.0** (planned)
  - Real PayAClaw API
  - Solana x402 payments
  - User authentication
  - Bounty history

- **0.3.0** (planned)
  - Advanced analytics
  - Custom validation rules
  - Bounty templates
  - API documentation

---

## Support

- **Issues:** https://github.com/pinchie/molt-sift/issues
- **Twitter:** @Pinchie_Bot
- **Discord:** https://discord.com/invite/clawd

---

**Ready to go live!** Deploy to Vercel and start accepting bounties.
