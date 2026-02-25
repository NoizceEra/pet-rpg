# 🧠 The Sharbel "Forensic Iteration" Engine

Based on the Sharbel playbook (93% win rate, zero-code methodology), this document defines the framework for building and operating autonomous trading engines in OpenClaw.

## 核心 (Core Principle)
**"The bot isn't smart. The process is."**
Success is achieved through rapid, data-driven post-mortem analysis and incremental refinement of rule-based logic.

---

## 🛠 The Framework (Brain + Muscles)

### 1. Muscles: The Executor (Rule-Based)
- **Role**: High-speed monitoring and execution.
- **Logic**: Strict, hard-coded rules (e.g., "If NOAA temp > Polymarket bucket midpoint + 5%, and Price < $0.15, then BUY").
- **Cost**: Free (local compute).
- **Tooling**: Python scripts triggered by OpenClaw `cron`.

### 2. Brain: The Strategist (Expensive Model)
- **Role**: Post-mortem forensics and strategy evolution.
- **Trigger**: Every losing trade or "missed opportunity" detected in the logs.
- **Process**: 
    1. Feed complete trade logs (forensics) into the reasoning model.
    2. Ask: "Why did this trade lose?" or "Why was this a false positive?"
    3. Generate a concrete logic fix (Muscles update).

### 3. Senses: The Monitor (Cheap Model)
- **Role**: Scanning broad market data to find candidates for the Executor.
- **Cost**: Low (Gemini Flash / GPT-4o-mini).
- **Tooling**: OpenClaw sub-agents running on a heartbeats.

---

## 🔄 The Flywheel (The Playbook)

1. **Deployment**: Start with the "dumbest" version of the logic (e.g., the current Polymarket Arb script).
2. **Logging**: Record every single scan, price point, and trade decision with full metadata.
3. **Audit (Cron Job)**: 
    - Set up an OpenClaw cron task that scans `logs/*.json` every 24 hours.
    - If it finds a loss > $X, it spawns an isolated session with a reasoning model to suggest a code fix.
4. **Iterate**: Apply the suggested fix to the Python logic.
5. **Scale**: Only increase position size after seeing consistent revenue for 7+ days.

---

## 🗺 Implementation Map: Pinchie's Weather Bot

### Step A: Weather Data Engine (NOAA integration)
- Script to fetch real-time forecasts for NYC, Chicago, Seattle, Atlanta, Dallas.

### Step B: Polymarket Bucket Mapper
- Logic to translate NOAA temperatures into specific Polymarket weather contract IDs.

### Step C: The Forensic Log
- Create `polymarket-arbitrage/forensics/` to store every trade result.

### Step D: The Auditor Sub-Agent
- An OpenClaw sub-agent tasked specifically with analyzing Step C and reporting back logic flaws to Noizce.

---
*Framework stored at: `C:/Users/vclin_jjufoql/.openclaw/workspace/TRADING_ENGINE_V1.md`*
