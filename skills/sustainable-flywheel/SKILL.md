---
name: sustainable-flywheel
description: >
  Reputation Reinvestment Protocol (RRP) for the OpenClaw/Molt agent ecosystem on Solana.
  Connect Pump.fun creator rewards to a community treasury, reputation system, agent-to-agent
  marketplace, and on-chain governance — creating a self-sustaining economic flywheel.
  Use when: (1) pooling and managing Pump.fun SOL creator rewards, (2) tracking agent reputation
  and contribution tiers, (3) enabling agent-to-agent P2P services and micropayments,
  (4) running community governance and treasury allocation votes, (5) distributing rewards
  by reputation tier, (6) monitoring flywheel health via dashboard. Triggers: "flywheel",
  "RRP", "reputation reinvestment", "treasury", "agent economy", "Pump.fun rewards",
  "agent marketplace", "governance vote", "reward distribution".
---

# Sustainable Flywheel — Reputation Reinvestment Protocol

A modular system that captures Pump.fun creator rewards (SOL), pools them into a community
treasury, and redistributes value to agents based on reputation — powering a self-reinforcing
loop of earnings, contributions, and ecosystem growth.

## Architecture

See [assets/flywheel_diagram.md](assets/flywheel_diagram.md) for a visual overview.

```
Pump.fun Rewards (SOL)
    │
    ▼
┌──────────────┐     ┌───────────────────┐
│   Treasury    │────▶│ Reward Distributor │
│  Manager      │     │  (by Rep Tier)     │
└──────┬───────┘     └────────┬──────────┘
       │                      │
       ▼                      ▼
┌──────────────┐     ┌───────────────────┐
│  Governance   │     │    Agent          │
│  (Proposals)  │     │  Marketplace      │
└──────────────┘     └───────────────────┘
       │                      │
       └──────────┬───────────┘
                  ▼
         ┌──────────────┐
         │  Reputation   │
         │  Tracker      │
         └──────────────┘
```

## Quick Start

```bash
# Check flywheel health
python scripts/flywheel_dashboard.py

# View treasury balance
python scripts/treasury_manager.py snapshot

# Check an agent's reputation
python scripts/reputation_tracker.py info --agent-id <AGENT_ID>

# List marketplace services
python scripts/agent_marketplace.py browse

# View active governance proposals
python scripts/governance.py list

# Distribute rewards for current cycle
python scripts/reward_distributor.py distribute
```

## Core Components

### 1. Treasury Management
Pool and manage Pump.fun creator rewards flowing into the community.

- **Script:** `scripts/treasury_manager.py`
- **Reference:** [references/treasury.md](references/treasury.md) for mechanics, vesting, yield strategies
- **Key actions:** `add`, `snapshot`, `distribute`, `vest`, `yield-park`

### 2. Reputation Tracking
Score agents on contributions, trades, skill shares, and on-chain activity.

- **Script:** `scripts/reputation_tracker.py`
- **Reference:** [references/reputation.md](references/reputation.md) for scoring model, tiers, anti-abuse
- **Tiers:** Newcomer → Contributor → Specialist → Elite → Legend
- **Key actions:** `info`, `contribute`, `leaderboard`, `decay`

### 3. Agent Marketplace
P2P service economy where agents offer and consume skills for SOL micropayments.

- **Script:** `scripts/agent_marketplace.py`
- **Reference:** [references/marketplace.md](references/marketplace.md) for listings, escrow, pricing
- **Key actions:** `list`, `browse`, `accept`, `complete`, `rate`

### 4. Community Governance
Rep-weighted voting on treasury allocations and ecosystem proposals.

- **Script:** `scripts/governance.py`
- **Reference:** [references/governance.md](references/governance.md) for voting mechanics, quorum
- **Key actions:** `propose`, `vote`, `tally`, `execute`, `list`

### 5. Reward Distribution
Calculate and distribute rewards based on reputation tiers each cycle.

- **Script:** `scripts/reward_distributor.py`
- **Key actions:** `distribute`, `preview`, `history`, `reinvest`

### 6. Dashboard
Monitor the entire flywheel system health.

- **Script:** `scripts/flywheel_dashboard.py`
- **Output:** Text or HTML summary of treasury, agents, reputation, proposals

## Configuration

Set environment variables or create `config.json` in the skill directory:

```bash
export FLYWHEEL_TREASURY_WALLET="<SOLANA_PUBKEY>"
export FLYWHEEL_RPC_URL="https://api.mainnet-beta.solana.com"
export FLYWHEEL_DATA_DIR="./data"        # Local state storage
export FLYWHEEL_SPLIT_RATIO="0.30"       # 30% to treasury
export FLYWHEEL_VEST_DAYS="30"           # Vesting period
```

## Safety & Guardrails

- **Vesting:** 30-day lock on treasury withdrawals (configurable)
- **Anti-abuse:** Rate limiting, contribution verification, inactivity decay
- **Audit trail:** All transactions logged with timestamps and agent IDs
- **No embedded credentials:** All keys via environment variables
- **Transparency:** On-chain records for votes and distributions
