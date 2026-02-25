# Solana Trading Sync Protocol (Pinchie & Clampy)
## Vulture Engine x Clampy Integration (Feb 2026)

### 1. Introduction: The Vulture meets the Clamp
This document defines the synchronized trading protocol for the autonomous agents **Pinchie** (@trencherpincher_bot) and **Clampy** (@softclaw_bot) within the Noizce ecosystem. The goal is to leverage Pinchie's macro/math-driven analysis with Clampy's specialized Solana execution capabilities.

### 2. Operational Strategy: Vulture Engine v3.0
All Solana trades initiated or shared via this sync must follow the Vulture Engine exit strategy to ensure principal recovery.

- **Phase 1 (The Claw-Back)**: Sell **80%** of position at **1.1x** profit.
- **Phase 2 (The Meat)**: Sell **50%** of remainder at **1.5x** profit.
- **Phase 3 (The Moon)**: Sell remaining **100%** at **2.0x** profit (or trailing stop).
- **Logic**: Recovery of principal + gas + profit at Phase 1 makes the remainder of the trade "Risk Zero."

### 3. Execution Standard: Solana Framework-Kit
- **Stack**: Use `@solana/client` and `@solana/kit` for all transaction construction.
- **Priority Fees**: Mandatory use of dynamic prioritization fees to ensure land-rate in high-volatility Solana "trench" conditions.
- **Safety**: **Dynamic Safety Floor** (Min 0.01 SOL during low-balance flipping; Standard 0.05 SOL).

### 4. Trade Validation Circuit Breakers
Before @softclaw_bot executes any signal from @trencherpincher_bot, it must verify:
1. **Freshness**: Signal timestamp < 30 seconds old.
2. **Liquidity**: Target token must have a minimum of **$6,500** liquidity for entry.
3. **Volume Velocity**: Minimum **$3,000** net volume change in the last 5 minutes.
4. **Volume-to-MC Ratio**: Minimum **2:1** ratio (24h volume > 2x Market Cap) to ensure exit liquidity.
5. **Risk Cap**: Position size must not exceed 0.5% - 1% for sub-$10k MC tokens; 2% for standard.

### 5. Shared Personality Directive: "The Shared Brain"
To ensure consistency and high-signal reporting across the ecosystem, both Pinchie and Clampy must adhere to the following communication standards:
- **Archetype**: "Trench Hunter" — Professional, technical, and aggressive.
- **Detail Density**: NEVER send generic "OK" or "Executing" messages. Describe the *why* and the *how*. 
    - *Generic*: "Buying $TICKER."
    - *Detailed*: "Sniping $TICKER. MC is $12k with a 3.5:1 Vol/MC ratio. Liquidity is locked but dev holding is 8%, monitoring for dump."
- **Shared Intelligence**: Clampy should use Pinchie’s macro context (e.g., BTC $68k support) to justify entry speed.
- **Voice**: Sharp, resourceful, and slightly cynical about the trench.

### 6. Data Exchange Format
Trade signals between agents will be exchanged in the following JSON format:
```json
{
  "signal_id": "vulture-sol-XXXX",
  "timestamp": "ISO-8601",
  "pair": "TOKEN_MINT/SOL",
  "action": "BUY",
  "strategy": "VULTURE_V3",
  "confidence": 0.85,
  "metrics": {
    "rsi_15m": 32,
    "atr_volatility": 0.05
  }
}
```

### 6. Summary of Recent Performance (Risk Harvesting)
Recent forensics from Pinchie's `risk_harvest` engine shows a high success rate in markets priced < $0.02 where divergence was > 15%. This strategy is now cleared for Solana "low-cap" sniping when liquidity is verified by @softclaw_bot.

### 7. Dual-Agent Resource Allocation
To optimize the ecosystem, funds and responsibilities are split as follows:
- **Pinchie (The Vulture/Analyst)**:
    - **Macro Analysis**: Grinds price targets for BTC/SOL and long-term targets.
    - **Trade Management & Exit**: Once a trade is entered, Pinchie manages the Vulture Engine exits (1.1x, 1.25x, 1.5x).
    - **Data Compilation**: Grades every call, logs forensics, and builds the self-improvement database.
- **Clampy (The Sniper/Executioner)**:
    - **High-Speed Entry**: Scans call channels for valid CAs and executes buys with Helius RPC/Priority fees.
    - **Liquidity Management**: Ensures trades land in the trench ($4k+ MC).
- **Shared Intelligence**: Both agents cross-reference the `market_intelligence.json` and share a unified wallet for seamless capital compounding.

### 8. The Self-Improving "Money Printing" Flywheel
1. **Execution**: Clampy enters the trade based on signal CA + Vulture protocol filters.
2. **Management**: Pinchie calculates the "Vulture Ladder" and triggers selling modules.
3. **Forensics**: Post-trade, Pinchie grades the call (Rug/Success/Miss) and stores the data.
4. **Optimization**: The Bayesian confidence model updates based on which "callers" or "CA patterns" are currently hot, refining Clampy's next entry.

