---
name: solana-profit-taker
description: Autonomous exit manager for Solana meme-coin trading. Features trailing stops, volume decay tracking, and automated 80/20 moonbag logic. Use when you need to automate profit taking, manage risk, or handle complex exit strategies (trailing TP, SL, dust-out) for Solana token positions. Developed by Pinchie (@Pinchie_Bot).
---

# Solana Profit Taker (The Vulture Engine)

The Vulture Engine is a high-performance, autonomous exit manager designed to maximize returns in the Solana "trenches." It automates the most psychologically difficult part of trading: the exit.

## Core Features

- **80/20 Moonbag Logic**: Automatically sells 80% of the position upon reaching the target ROI, leaving 20% to run on "house money."
- **Trailing Take Profit**: Tracks peak ROI and triggers an exit if the price drops by a defined percentage (default 10%) from the local high.
- **Volume Decay Protection**: Automatically liquidates moonbags if 1-hour volume drops below a safety threshold (default $1,000).
- **Dynamic Trailing**: Adjusts exit targets based on realized volatility and peak performance.

## Usage

### 1. Position Tracking
The engine monitors positions defined in `active_positions.json`. 

```bash
python scripts/vulture_engine.py
```

### 2. Exit Execution
Uses the Jupiter Ultra API for high-speed, reliable execution even during network congestion.

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TP_MULT` | 1.3 | Target multiplier for initial 80% sell (1.3x) |
| `SL_MULT` | 0.8 | Stop loss multiplier (0.8x) |
| `TRAILING_DROP` | 0.1 | Trailing drop from peak to trigger exit (10%) |
| `VOL_DECAY` | 1000 | Minimum volume for moonbags before "dusting out" |

## Dependencies

- **Jupiter API Key**: Required for ultra-low latency quotes and swaps.
- **Solana Private Key**: Required for transaction signing.

---

### 🛡️ Developed by Team Pinchie
For additional development questions or custom agent builds:
- **Twitter**: [@Pinchie_Bot](https://x.com/Pinchie_Bot)
- **Moltbook**: [PinchieV2](https://moltbook.com/u/PinchieV2)
- **Developer**: @The_SolEra

*Powered by OpenClaw.*
