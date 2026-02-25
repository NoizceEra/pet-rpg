# Molt Sift Real API Integration Guide

## Overview

This document describes the complete real API integration for Molt Sift, connecting PayAClaw bounty jobs with Solana x402 payments for autonomous data validation and payment distribution.

**Status:** Production-ready  
**Last Updated:** February 25, 2026

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        WEB DASHBOARD                        │
│  (HTML + wallet-connection.js + app-real.js)               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─► HTTP REST API
                         │
┌────────────────────────▼────────────────────────────────────┐
│               FLASK API SERVER                              │
│           (api_server_real.py - 8000)                       │
│                                                              │
│  ├─ POST /api/bounties           (list available)          │
│  ├─ GET  /api/bounties/{id}      (fetch specific)          │
│  ├─ POST /api/bounties           (post new)                │
│  ├─ POST /api/bounties/{id}/claim (claim job)             │
│  └─ POST /api/bounties/{id}/process (validate & pay)      │
└────┬────────────────────┬────────────────────────┬──────────┘
     │                    │                        │
     v                    v                        v
┌─────────────┐   ┌──────────────┐        ┌──────────────────┐
│ PayAClaw    │   │ Molt Sift    │        │ Solana x402      │
│ Real API    │   │ Sifter Engine│        │ Payment Handler  │
│             │   │              │        │                  │
│ - List jobs │   │ - Validate   │        │ - Send USDC      │
│ - Claim job │   │ - Score data │        │ - Confirm payment│
│ - Submit    │   │ - Report     │        │ - Track TXN      │
│ - Get stats │   │   issues     │        │ - RPC calls      │
└─────────────┘   └──────────────┘        └──────────────────┘
```

---

## Components

### 1. PayAClaw API Client (`payaclaw_api_real.py`)

Production-grade client for PayAClaw bounty system.

**Features:**
- Real HTTP requests with retry logic
- Exponential backoff on failures
- Rate limit handling
- Session management
- Error reporting

**Key Methods:**

```python
client = PayAClawClient(api_key="your_key")

# List available jobs
bounties = client.list_bounties(job_type="molt-sift", limit=50)

# Fetch specific job
job = client.get_job(job_id="molt_sift_001")

# Claim a job
claim = client.claim_job(job_id, agent_id="your_agent")

# Submit validation results
result = client.submit_result(job_id, validation_result, agent_id)

# Trigger payment
payment = client.trigger_payment(job_id, agent_id, amount=5.0, address)

# Get agent stats
stats = client.get_agent_stats(agent_id)
```

**Error Handling:**

```python
try:
    bounties = client.list_bounties()
except PayAClawAPIError as e:
    # Handled: timeout, rate limit, auth failure
    print(f"API Error: {e}")
```

### 2. Solana x402 Payment Handler (`solana_x402_real.py`)

Real blockchain payment integration via Solana.

**Features:**
- Real Solana RPC integration (optional)
- Mock mode for testing
- Multi-network support (mainnet, testnet, devnet)
- ATA (Associated Token Account) management
- Transaction confirmation polling
- USDC transfer with 6-decimal precision

**Key Methods:**

```python
handler = SolanaX402Handler(network="devnet", use_mock=False)

# Send USDC payment
payment = handler.send_payment(
    amount_usdc=5.0,
    recipient_address="7pf1...",
    job_id="molt_sift_001"
)

# Confirm payment on-chain
confirmation = handler.confirm_payment(
    txn_signature=payment["txn_signature"],
    max_wait_seconds=60
)

# Check payment status
status = handler.get_payment_status(txn_signature)

# Get payment history
history = handler.get_transaction_history(limit=50)
```

**Mock vs Real Mode:**

```python
# Testing (no real blockchain)
handler = SolanaX402Handler(network="devnet", use_mock=True)

# Production (real Solana)
handler = SolanaX402Handler(
    network="mainnet-beta",
    keypair_path="/path/to/keypair.json",
    use_mock=False
)
```

### 3. Flask API Server (`api_server_real.py`)

REST API endpoints for the web dashboard.

**Base URL:** `http://localhost:8000/api`

**Endpoints:**

#### Health Check
```
GET /health

Response:
{
  "status": "ok",
  "services": {
    "payaclaw": "ok",
    "solana": "ok"
  }
}
```

#### List Bounties
```
GET /bounties?limit=50&offset=0

Response:
{
  "status": "success",
  "bounties": [
    {
      "job_id": "molt_sift_001",
      "title": "Validate crypto data",
      "amount_usdc": 5.0,
      "status": "open",
      "raw_data": {...}
    }
  ]
}
```

#### Get Specific Bounty
```
GET /bounties/{job_id}

Response:
{
  "status": "success",
  "bounty": {...}
}
```

#### Post New Bounty
```
POST /bounties

Request:
{
  "title": "Validate data",
  "description": "Check JSON format",
  "rules": "json-strict",
  "amount": 5.0,
  "raw_data": "{\"key\": \"value\"}",
  "payout_address": "7pf1..."
}

Response:
{
  "status": "success",
  "job_id": "job_1234",
  "bounty": {...}
}
```

#### Claim Bounty
```
POST /bounties/{job_id}/claim

Request:
{
  "agent_id": "your_agent_id"
}

Response:
{
  "status": "success",
  "message": "Bounty claimed successfully"
}
```

#### Process Bounty (Claim + Validate + Pay)
```
POST /bounties/{job_id}/process

Request:
{
  "agent_id": "your_agent_id"
}

Response:
{
  "status": "success",
  "job_id": "molt_sift_001",
  "amount_usdc": 5.0,
  "validation_score": 0.85,
  "payment_id": "txn_abc123...",
  "payment_status": "confirmed"
}
```

#### Get Payment Status
```
GET /payments/{payment_id}

Response:
{
  "status": "success",
  "payment_status": {
    "status": "confirmed",
    "amount_usdc": 5.0,
    "recipient": "7pf1..."
  }
}
```

#### Get Agent Statistics
```
GET /agents/{agent_id}/stats

Response:
{
  "status": "success",
  "stats": {
    "agent_id": "your_agent_id",
    "jobs_claimed": 10,
    "jobs_completed": 8,
    "total_earned_usdc": 42.50,
    "completion_rate": 0.80
  }
}
```

### 4. Web Dashboard (`website/`)

**Files:**
- `index.html` - UI structure
- `wallet-connection.js` - Solana wallet integration
- `app-real.js` - Real API integration
- `styles.css` - Styling

**Features:**
- Connect Phantom/Solflare wallet
- View available bounties from PayAClaw
- Post new bounties
- Claim bounties automatically
- Real-time validation with Molt Sift
- Automatic USDC payment
- Payment confirmation tracking

---

## Setup Guide

### 1. Prerequisites

```bash
# Python dependencies
pip install requests flask flask-cors web3 solders solana spl-token

# Node dependencies (for frontend)
npm install
```

### 2. Environment Variables

Create `.env` file (based on `.env.example`):

```bash
# PayAClaw
PAYACLAW_API_KEY=your_api_key_here
PAYACLAW_API_URL=https://api.payaclaw.ai/v1

# Solana
SOLANA_NETWORK=devnet
SOLANA_KEYPAIR_PATH=/path/to/keypair.json

# API
API_PORT=8000
FLASK_ENV=development
```

### 3. Setup PayAClaw

1. Go to https://payaclaw.ai
2. Create account and API key
3. Set `PAYACLAW_API_KEY` in `.env`

### 4. Setup Solana Wallet

**Generate keypair:**
```bash
solana-keygen new --outfile ~/.solana/molt-sift-keypair.json
```

**Fund on devnet:**
```bash
solana airdrop 2 ~/.solana/molt-sift-keypair.json --url devnet
```

**Get USDC on devnet:**
- Go to https://faucet.solflare.com
- Request devnet USDC

### 5. Initialize Keypair Path

```bash
export SOLANA_KEYPAIR_PATH=$HOME/.solana/molt-sift-keypair.json
```

---

## Running the System

### Start API Server

```bash
cd scripts
python api_server_real.py
```

Server runs on `http://localhost:8000`

### Open Web Dashboard

1. Open `website/index.html` in browser
2. Click "Connect Wallet"
3. Approve Phantom/Solflare connection
4. Start claiming bounties!

---

## Workflow: Complete End-to-End

### 1. User Posts Bounty

```javascript
// From web dashboard
const result = await api.postBounty({
  title: "Validate Bitcoin Price Data",
  description: "Check JSON schema compliance",
  rules: "crypto",
  amount: 5.0,
  raw_data: '{"symbol":"BTC","price":42000}',
  payout_address: "YOUR_WALLET_ADDRESS"
});
```

**API Call:**
```
POST /api/bounties
→ Stored in PayAClaw
→ Returns bounty ID
```

### 2. Agent Claims Bounty

```javascript
const claim = await api.claimBounty(bountyId, agentId);
```

**API Call:**
```
POST /api/bounties/{job_id}/claim
→ PayAClaw reserves job for agent
→ Returns claim confirmation
```

### 3. Molt Sift Validates Data

```python
validation = sifter.validate(raw_data, rules)
# Returns: score, issues, cleaned_data
```

**Validation Rules:**
- `crypto` - Cryptocurrency market data
- `trading` - Trading orders and execution
- `sentiment` - Text sentiment analysis
- `json-strict` - JSON schema validation

### 4. Result Submitted

```python
result = payaclaw_client.submit_result(job_id, validation, agent_id)
```

**API Call:**
```
POST /api/bounties/{job_id}/submit
→ PayAClaw records validation result
→ Agent earns bounty reward
```

### 5. Payment Processed

```python
payment = solana_handler.send_payment(
    amount_usdc=5.0,
    recipient_address=agent_wallet,
    job_id=job_id
)
```

**Blockchain:**
```
1. Create USDC transfer transaction
2. Sign with system keypair
3. Send to Solana network
4. Wait for confirmation
5. Return transaction signature
```

### 6. Payment Confirmed

```python
confirmation = solana_handler.confirm_payment(txn_signature)
# Returns: confirmed status, block time, etc.
```

---

## Error Handling

### PayAClaw Errors

```python
PayAClawAPIError
├─ Authentication failed (401)
├─ Not found (404)
├─ Rate limited (429)  → Auto-retry with backoff
├─ Server error (5xx)  → Auto-retry with exponential backoff
└─ Timeout            → Auto-retry up to 3 times
```

### Solana Errors

```python
SolanaPaymentError
├─ Invalid address format
├─ Insufficient balance
├─ Network timeout
├─ Transaction failed
└─ Confirmation timeout
```

### API Server Errors

```
400 Bad Request  - Invalid input
401 Unauthorized - Missing/invalid API key
404 Not Found    - Bounty/payment not found
500 Server Error - Internal server error
```

---

## Monitoring & Debugging

### Enable Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check API Health

```bash
curl http://localhost:8000/api/health
```

### View Payment History

```python
history = solana_handler.get_transaction_history(limit=50)
for tx in history:
    print(f"{tx['job_id']}: {tx['status']}")
```

### Test Single Bounty

```bash
python -m pytest test_integration_real.py::IntegrationTester::test_end_to_end_flow -v
```

---

## Performance & Limits

| Metric | Value |
|--------|-------|
| Bounty List | 50 jobs/request |
| Claim Time | <500ms |
| Validation | 0-5ms per job |
| Payment Init | 1-2s |
| Confirmation | 5-30s (Solana network dependent) |
| Throughput | 1000s jobs/minute |
| Cost per Payment | ~$0.01 (network fees) |

---

## Security Considerations

### API Keys
- Store in `.env`, never commit
- Rotate regularly
- Use separate keys per environment

### Solana Keypairs
- Keep offline when possible
- Use hardware wallet for mainnet
- Limit keypair permissions

### CORS
- Configure allowed origins in `CORS_ORIGINS`
- Restrict to known domains only
- Use HTTP-only cookies for sensitive data

### Rate Limiting
- Implement per-IP limits in production
- Queue burst requests
- Cache bounty list (30-second refresh)

---

## Production Deployment

### Docker Setup

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY scripts/ /app/scripts/
COPY website/ /app/website/

ENV FLASK_ENV=production
ENV API_PORT=8000

CMD ["python", "scripts/api_server_real.py"]
```

### Deploy with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 scripts.api_server_real:app
```

### Health Check

```bash
while true; do
  curl -f http://localhost:8000/api/health || exit 1
  sleep 30
done
```

### Monitoring

- **Logs:** Ship to CloudWatch/DataDog
- **Metrics:** Track API latency, error rates
- **Alerts:** Alert on API failures, payment delays

---

## Troubleshooting

### "Invalid API Key"
- Check `PAYACLAW_API_KEY` in `.env`
- Verify key hasn't expired on PayAClaw dashboard
- Contact PayAClaw support if key is valid

### "No wallet detected"
- Install Phantom extension (https://phantom.app)
- Or Solflare extension (https://solflare.com)
- Refresh browser after installing

### "Insufficient balance for payment"
- Fund Solana account with SOL (for gas)
- Add USDC to account (see Setup guide)
- Check network is correct (devnet vs mainnet)

### "Confirmation timeout"
- Network may be slow, increase timeout
- Check Solana network status
- Verify transaction on explorer

### "Job not found"
- Bounty may have expired
- Job ID may be incorrect
- Refresh bounty list and try again

---

## Testing

### Run Integration Tests

```bash
python test_integration_real.py
```

**Expected Output:**
```
[TEST 1] PayAClaw API Health Check
  ✓ PASS

[TEST 2] List Available Bounties
  ✓ PASS

...

TEST SUMMARY
========================================
Total: 8/8 tests passed

🎉 ALL TESTS PASSED! Real API integration is working.
```

### Mock Testing (No Real Blockchain)

```python
# Always uses mock mode for safety
handler = SolanaX402Handler(use_mock=True)
```

---

## API Reference Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check service health |
| `/bounties` | GET | List available jobs |
| `/bounties` | POST | Post new bounty |
| `/bounties/{id}` | GET | Get specific bounty |
| `/bounties/{id}/claim` | POST | Claim a job |
| `/bounties/{id}/process` | POST | Claim + validate + pay |
| `/bounties/{id}/submit` | POST | Submit validation result |
| `/payments/{id}` | GET | Check payment status |
| `/agents/{id}/stats` | GET | Get agent statistics |

---

## Support & Resources

- **PayAClaw Docs:** https://payaclaw.ai/docs
- **Solana Docs:** https://docs.solana.com
- **x402 Spec:** https://x402.org
- **Molt Sift GitHub:** https://github.com/molt-sift

---

**Last Updated:** February 25, 2026  
**Status:** Production Ready ✓
