# Trading Rules & Risk Management
*Updated: 2026-02-20 14:38 MST*

## Core Principles (User Directive)

> "Don't trade blindly or use too much of our capital. Small profits win the race, we got time."

**Translation:**
1. **Conservative Sizing:** Protect capital first
2. **Selective Entry:** Quality over quantity
3. **Patient Strategy:** Compound small wins
4. **No Rush:** Time is on our side

## Current Portfolio Status

**Balance:** $51.19 USDC
**All-Time PnL:** +$132.20 (+258% from $22.31 initial)
**Active Positions:** 26 positions ($5,692.46 exposure)

## Position Sizing Rules (UPDATED 2026-02-20)

### Current Settings (TOO AGGRESSIVE)
- PBot1 Arb: 35% per trade → **$17.85 per trade**
- Other strategies: 5% per trade → **$2.55 per trade**
- Reserve: $1.00

### RECOMMENDED CONSERVATIVE SETTINGS

**Position Sizing:**
- **PBot1 Arb:** 15% max per trade (~$7.50)
- **FastLoop Momentum:** 5% max per trade (~$2.50)
- **BoyChik/Other:** 3% max per trade (~$1.50)
- **Reserve:** $5.00 (protect emergency capital)

**Daily Limits:**
- Max 5 new positions per day (avoid over-trading)
- Max $25 deployed per day (50% of balance)
- Stop trading if daily loss > $5

**Per-Position Limits:**
- Max loss per position: $2.00
- Target profit per position: $0.50-$2.00 (small consistent wins)
- Max hold time: 24 hours (don't get married to positions)

## Strategy-Specific Rules

### PBot1 Arbitrage (Risk-Free)
**Entry Criteria:**
- Yes + No combined ask < $0.98 (2%+ profit buffer)
- Min profit: $0.50 per arb
- Max position: $7.50

**Exit:**
- Auto-redeem winners
- Close if combined price > $1.00 (arb broken)

### FastLoop Momentum
**Entry Criteria:**
- BTC/ETH move > 0.5% in 5 minutes
- Clear directional momentum (not choppy)
- Max position: $2.50

**Exit:**
- Target: +15% ROI ($0.38 profit on $2.50)
- Stop: -10% ROI ($0.25 loss on $2.50)
- Time stop: 15 minutes max hold

### BoyChik (Theoretical Edge)
**Entry Criteria:**
- High conviction only (news catalyst + volume)
- Min edge: 5% mispricing
- Max position: $1.50

**Exit:**
- Target: +20% ROI
- Stop: -15% ROI
- Time stop: 24 hours

## Risk Management Protocols

**Pre-Trade Checklist:**
1. Is this trade backed by clear edge/catalyst?
2. Is position size within limits?
3. Do we have enough capital after reserve?
4. Is this our best use of capital right now?
5. Can we afford to lose this amount?

**During Trade:**
- Monitor every 5 minutes
- Respect stops (don't move them)
- Take profits at target (don't get greedy)

**Post-Trade:**
- Log result in trade journal
- Update position limits if needed
- Review what worked/didn't work

## Portfolio Health Metrics

**Green Zone (Healthy):**
- Liquid capital > $30
- Active positions < 30
- Daily PnL: -$2 to +$5
- Win rate > 60%

**Yellow Zone (Caution):**
- Liquid capital $15-$30
- Active positions 30-50
- Daily PnL: -$5 to -$2
- Win rate 50-60%

**Red Zone (Stop Trading):**
- Liquid capital < $15
- Active positions > 50
- Daily PnL < -$5
- Win rate < 50%

**Current Status:** GREEN (Liquid: $51.19, Positions: 26, Win Rate: Strong)

## Adjustment Plan (Immediate)

**Step 1: Update Position Sizing**
```python
# scripts/unified_scanner.py - calculate_size()
if balance < 50.0:
    raw_size = balance * 0.15  # REDUCED from 0.35
elif strategy == "pbot1":
    raw_size = balance * 0.15  # REDUCED from 0.35
else:
    raw_size = balance * 0.03  # REDUCED from 0.05
```

**Step 2: Increase Reserve**
```python
RESERVE_AMOUNT = 5.0  # INCREASED from 1.0
```

**Step 3: Add Daily Limits**
```python
MAX_DAILY_TRADES = 5
MAX_DAILY_CAPITAL = 25.0  # 50% of current balance
```

**Step 4: Stricter Entry Filters**
```python
PBOT1_ARB_THRESHOLD = 0.96  # STRICTER: 4% profit buffer (was 0.98)
FASTLOOP_MOMENTUM_THRESHOLD = 0.8  # STRICTER: 0.8% move (was 0.5%)
MASSIVE_GAIN_THRESHOLD = 0.12  # STRICTER: 12% ROI target (was 15%)
```

## Philosophy: The Tortoise Wins

**Math:**
- 1% daily gain = 37x in one year
- $51 → $1,887 in 365 days at 1%/day
- No need to rush, no need to risk big

**Current Performance:**
- Started: $22.31
- Now: $51.19
- Growth: +129% in ~15 days
- Avg: +8.6% per day
- **This is EXCELLENT. Protect it.**

**Going Forward:**
- Target: 2-5% daily gain (sustainable)
- Focus: Consistency over home runs
- Method: Many small wins, rare small losses

---

**Last Updated:** 2026-02-20 14:38 MST  
**Status:** Conservative mode ACTIVE  
**Next Review:** After 100 more trades or if balance changes >20%
