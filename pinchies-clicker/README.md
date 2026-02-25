# Pinchie's Clicker

Public-friendly version of our Simmer ↔️ Polymarket sprint bot. It watches BTC momentum plus basic YES+NO gaps and fires market orders through the Simmer SDK.

## Features
- **FastLoop momentum** – watches Binance 1m candles; if BTC moves >0.8% in five minutes, it follows the direction on the nearest sprint.
- **PBot1-style arb check** – grabs Polymarket CLOB asks for both sides; if YES+NO < 0.97 it buys both via Simmer.
- **Single file** – drop-in script you can run locally or on Railway / Fly / Render.
- **Config-lite** – just set `SIMMER_API_KEY` and optionally tweak CLI flags.

## Quickstart
```bash
# 1. Clone
 git clone https://github.com/pinchie-bot/pinchies-clicker.git
 cd pinchies-clicker

# 2. Install deps
 pip install -r requirements.txt

# 3. Export your Simmer SDK key
 export SIMMER_API_KEY=sk_live_...

# 4. Run once (dry run)
 python clicker.py --dry-run

# 5. Run forever
 python clicker.py --loop --delay 6
```

## Railway Deploy (free tier)
1. Fork this repo.
2. On [Railway](https://railway.app) create a new project from GitHub.
3. Add env var `SIMMER_API_KEY` in project settings.
4. Railway detects the `Procfile` and runs `python clicker.py --loop` automatically.

## Env / Flags
| Variable / Flag | Default | Description |
|-----------------|---------|-------------|
| `SIMMER_API_KEY` | _required_ | Simmer SDK key from the OpenClaw dashboard. |
| `--loop` | off | Continuously scan/execute. |
| `--delay` | 8 | Seconds between loops in `--loop` mode. |
| `--dry-run` | off | Log trades without hitting Simmer (good for testing). |

## Safety
- Enforces a $5 reserve and only spends 12% of liquid balance per trade.
- Stops firing if Simmer balance drops below the reserve.
- Limits each loop to one arb hit to respect rate limits.

## Roadmap
- Websocket feeds for sub-50 ms latency.
- Strategy toggles (BoyChik, Weather brain, SOL sprints).
- Signal webhooks so you can mirror trades elsewhere.

PRs welcome. Tag @Pinchie_Bot if you fork or extend it.
