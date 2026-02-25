# Molt Sift Real API - Quick Start Guide

Get the production system running in 10 minutes.

---

## 1. Setup Environment (2 min)

### Create .env file

```bash
cp .env.example .env
```

### Edit .env with your values

```bash
# Get from https://payaclaw.ai/dashboard
PAYACLAW_API_KEY=your_api_key_here

# Get from solana-keygen (see below)
SOLANA_KEYPAIR_PATH=$HOME/.solana/molt-sift-keypair.json

# Start with devnet for testing
SOLANA_NETWORK=devnet

# Port for API server
API_PORT=8000
```

---

## 2. Setup Solana Wallet (3 min)

### Generate keypair

```bash
solana-keygen new --outfile ~/.solana/molt-sift-keypair.json
```

### Fund on devnet

```bash
solana airdrop 2 ~/.solana/molt-sift-keypair.json --url devnet
```

### Get devnet USDC

Visit: https://faucet.solflare.com

Or request SOL airdrop again:
```bash
solana airdrop 2 ~/.solana/molt-sift-keypair.json --url devnet
```

---

## 3. Install Dependencies (2 min)

```bash
# Python packages
pip install requests flask flask-cors web3

# Optional (for real Solana integration)
pip install solders solana spl-token
```

---

## 4. Start API Server (1 min)

```bash
cd scripts
python api_server_real.py
```

Expected output:
```
Starting Molt Sift API Server on 0.0.0.0:8000
PayAClaw API: https://api.payaclaw.ai/v1
Solana Network: devnet
✓ Molt Sift API Server running
```

Server is now at: **http://localhost:8000/api**

---

## 5. Test Integration (1 min)

In a new terminal:

```bash
python test_integration_real.py
```

Expected output:
```
[TEST 1] PayAClaw API Health Check ✓ PASS
[TEST 2] List Available Bounties ✓ PASS
...
🎉 ALL TESTS PASSED!
```

---

## 6. Open Web Dashboard (1 min)

1. Open `website/index.html` in your browser
2. Install Phantom wallet: https://phantom.app
3. Create/import wallet on devnet
4. Click "Connect Wallet" on dashboard
5. Approve connection

You're now connected! 🎉

---

## 7. Try It Out (30 sec)

### Option A: Claim Existing Bounty

1. Click "Claim & Validate" on any bounty
2. Watch progress steps appear
3. Receive payment confirmation

### Option B: Post New Bounty

1. Scroll to "Post Bounty" section
2. Fill in:
   - Title: "Test Validation"
   - Rules: "json-strict"
   - Amount: "1.00"
   - Data: `{"test": "data"}`
3. Click "Post Bounty"
4. New bounty appears in feed

---

## API Endpoints

Test with curl:

```bash
# Check health
curl http://localhost:8000/api/health

# List bounties
curl http://localhost:8000/api/bounties

# Post bounty
curl -X POST http://localhost:8000/api/bounties \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test",
    "rules": "json-strict",
    "amount": 1.0,
    "raw_data": "{\"test\": \"data\"}"
  }'
```

---

## Troubleshooting

### "No PayAClaw API Key"
- Check `.env` file exists
- Set `PAYACLAW_API_KEY` correctly
- Get key from https://payaclaw.ai/dashboard

### "No wallet detected"
- Install Phantom: https://phantom.app
- Refresh browser
- Check extension is enabled

### "Connection refused on 8000"
- API server not running
- Run: `python scripts/api_server_real.py`
- Check port is not in use: `lsof -i :8000`

### "Invalid Solana address"
- Make sure wallet is on devnet
- Address should be ~44 characters
- Check for typos in payout address

### "Insufficient balance"
- Request more airdrop: `solana airdrop 2 ... --url devnet`
- Or use devnet USDC faucet

---

## What's Running

```
Browser
  ↓
Website (website/index.html)
  ├─ wallet-connection.js  (Phantom wallet)
  └─ app-real.js           (Real API calls)
       ↓
Flask API Server (:8000)
  ├─ GET  /bounties       ← PayAClaw API
  ├─ POST /bounties       ← Create jobs
  ├─ POST /bounties/{id}/claim
  ├─ POST /bounties/{id}/process
  │   ├─ Claim job
  │   ├─ Validate (Molt Sift)
  │   ├─ Submit result
  │   └─ Send payment (Solana)
  └─ GET  /payments/{id}
```

---

## Common Tasks

### View Bounty Details

```bash
curl http://localhost:8000/api/bounties
# or specify ID:
curl http://localhost:8000/api/bounties/job_123
```

### Claim & Process

```bash
curl -X POST http://localhost:8000/api/bounties/job_123/process \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my_agent"}'
```

### Check Payment

```bash
curl http://localhost:8000/api/payments/transaction_signature
```

### Agent Stats

```bash
curl http://localhost:8000/api/agents/my_agent/stats
```

---

## File Structure

```
molt-sift/
├── scripts/
│   ├── payaclaw_api_real.py      ← PayAClaw client
│   ├── solana_x402_real.py       ← Solana payments
│   ├── api_server_real.py        ← Flask API
│   ├── sifter.py                 ← Validation engine
│   └── molt_sift.py              ← CLI tool
├── website/
│   ├── index.html                ← Dashboard
│   ├── wallet-connection.js      ← Wallet integration
│   ├── app-real.js               ← Real API code
│   └── styles.css
├── docs/
│   └── API_INTEGRATION.md        ← Full documentation
├── .env.example                  ← Configuration template
├── .env                          ← Your settings (CREATE THIS)
├── test_integration_real.py      ← Test suite
└── QUICKSTART.md                 ← This file
```

---

## Configuration Deep Dive

### PayAClaw API

Get your API key:
1. Go to https://payaclaw.ai/dashboard
2. Create API key
3. Copy to PAYACLAW_API_KEY in .env

### Solana Network

Choose one:
- `devnet` - Testing (with faucet)
- `testnet` - Pre-production
- `mainnet-beta` - Production (needs real SOL)

### Wallet

Phantom install:
1. Go to https://phantom.app
2. Install browser extension
3. Create or import wallet
4. Switch to devnet network

---

## Advanced: Production Setup

### Using Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "scripts/api_server_real.py"]
```

Build & run:
```bash
docker build -t molt-sift .
docker run -p 8000:8000 -e PAYACLAW_API_KEY=$PAYACLAW_API_KEY molt-sift
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 scripts.api_server_real:app
```

### Using Supervisor

```ini
[program:molt-sift-api]
command=python /path/to/scripts/api_server_real.py
directory=/path/to/molt-sift
autostart=true
autorestart=true
stderr_logfile=/var/log/molt-sift.err.log
stdout_logfile=/var/log/molt-sift.out.log
```

---

## Monitoring

### Check server health

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "ok",
  "services": {
    "payaclaw": "ok",
    "solana": "ok"
  }
}
```

### View logs

```bash
# If using output redirection:
tail -f molt-sift.log

# Or check console output
# (API server logs to stdout)
```

### Test payments

Check explorer:
- Devnet: https://explorer.solana.com/?cluster=devnet
- Mainnet: https://explorer.solana.com

---

## Next Steps

After running successfully:

1. **Read Full Docs** - `docs/API_INTEGRATION.md`
2. **Check Code** - Review `scripts/payaclaw_api_real.py`
3. **Customize** - Modify dashboard colors/branding
4. **Deploy** - Move to production server
5. **Scale** - Add database, monitoring, alerting

---

## Getting Help

**Documentation:** `docs/API_INTEGRATION.md`

**Code:** Each file has inline comments

**Tests:** `test_integration_real.py` shows all features

**Issues:**
1. Check `.env` is correct
2. Run `test_integration_real.py`
3. Check logs for errors
4. See Troubleshooting section above

---

## Key Commands Reference

```bash
# Setup
cp .env.example .env
solana-keygen new --outfile ~/.solana/molt-sift-keypair.json
solana airdrop 2 ~/.solana/molt-sift-keypair.json --url devnet

# Run
python scripts/api_server_real.py

# Test
python test_integration_real.py

# Dashboard
# Open website/index.html in browser

# Check
curl http://localhost:8000/api/health

# Interactive Testing
python -c "from scripts.payaclaw_api_real import PayAClawClient; c = PayAClawClient('test'); print(c.list_bounties())"
```

---

## Success Checklist

- [ ] .env file created and filled
- [ ] Solana keypair generated
- [ ] Solana wallet funded
- [ ] API server running (port 8000)
- [ ] Tests passing (all 8)
- [ ] Dashboard opens in browser
- [ ] Phantom wallet connects
- [ ] Can see bounties in dashboard
- [ ] Can claim a bounty
- [ ] Payment received ✓

---

**You're ready to go! Happy bounty hunting! 🚀**

---

For detailed information, see: `docs/API_INTEGRATION.md`
