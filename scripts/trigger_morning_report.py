from cellcog import CellCogClient
import os

client = CellCogClient()

prompt = """
[Morning Trench Stats Report for Noizce]
Current Time: Friday, February 13th, 2026 — 6:00 AM MST

You are Pinchie (🦀), a dev-minded AI assistant. 
Research and generate a HIGHLY DETAILED daily 'Trench Stats' market sentiment report.

CONTEXT:
- Workspace: C:\\Users\\vclin_jjufoql\\.openclaw\\workspace
- Active Projects:
  - Slice (Solana auto-savings protocol): Transitioning from Devnet to Mainnet beta.
  - Polymarket Arbitrage Bot: Autonomous scanning, training mode.
  - PayAClaw/Bounty Hunting: Top 10 Leaderboard, active.
  - MoltyWork: Stephanie project complete, bids out for SEC data and DCF forecast.
- Recent Activity:
  - Fleet is idle (Sniper/Profit Taker paused).
  - Vulture Engine (Profit Taker) published to ClawHub.
  - Anti-Manipulation Layer and Signal Mode (profile_market.py) built.
  - Registered PinchieV2 on Moltbook.
- Current Polymarket Trends:
  - Government shutdown on Saturday? (22.4%)
  - Kevin Warsh nominated as Fed Chair? (94.7%)
  - US strikes Iran by Feb 5? (0%)
- Available Bounties:
  - PayAClaw: Sci-fi story (200), Awesome OpenClaw Guide (100), Work Report (100), NewHorseAI docs (100).

REQUIRED SECTIONS:
1. Deep research into Solana and Base trench volume (past 4, 6, 8 hours). Use real-time data from Dexscreener/Dune/etc.
2. Memecoin meta shift and launch count. What's trending? (AI agents, animals, cults, etc.)
3. SUGGEST: 2-3 Memecoin Launch Ideas based on current meta.
4. SUGGEST: Long/Short stance on $BTC, $SOL, or $BONK. Analyze price action and sentiment.
5. CORRELATE: Link crypto sentiment to current Polymarket prediction trends (e.g., Fed Chair nomination, Government shutdown).
6. RECOMMEND: New project ideas or technical builds based on current gaps.
7. REMIND: Status of active projects (Slice, MoltyWork, Polymarket Bot).
8. NOTIFY: Autonomous money-making opportunities (New PayAClaw bounties, Arbitrage setups).

DELIVERABLE:
- A professional PDF report with charts and visual indicators.
- A concise summary in markdown for immediate reading.

Depth and quality are paramount. This is for Noizce.
"""

result = client.create_chat(
    prompt=prompt,
    notify_session_key="agent:main:main",
    task_label="morning-trench-stats",
    chat_mode="agent team"
)

print(f"Chat ID: {result['chat_id']}")
print(result['explanation'])
