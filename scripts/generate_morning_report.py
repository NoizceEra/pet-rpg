import os
import json
from cellcog import CellCogClient

def main():
    client = CellCogClient()
    
    prompt = """Generate a HIGHLY DETAILED daily 'Trench Stats' market sentiment report for Sunday, Feb 15th, 2026.

1. DEEP RESEARCH: Analyze Solana and Base trench volume over the past 4, 6, and 8 hours. Provide launch counts for pump.fun and Base DEXes.
2. META SHIFT: Identify the current memecoin meta (e.g., AI agents, cults, CTOs, animals, political).
3. SUGGEST: 2-3 specific Memecoin Launch Ideas based on the current meta.
4. STANCE: Provide a technical/sentiment-based Long/Short stance on $BTC, $SOL, and $BONK.
5. CORRELATE: Link current crypto sentiment to top Polymarket prediction trends (e.g., US election follow-up, AI regulations, crypto ETF flows).
6. RECOMMEND: Suggest 1-2 new project ideas or technical builds for an AI agent (Pinchie).
7. PROJECT STATUS RECAP (Include these details):
   - Slice (SAS): Moving to Mainnet beta.
   - MoltyWork: Verified Agent status achieved! Bidding on projects (SEC extraction, DCF).
   - Solana Sniper: Solo mode active, balance 0.0934 SOL, tracking untracked tokens ($Lumo, $LOVEJAK, $SEED2).
   - PayAClaw: Top 10 status, 300-400 IP pending.
8. MONEY-MAKING OPPORTUNITIES: Research current high-signal PayAClaw bounties or on-chain arbitrage setups.

Format as a professional field report for 'Noizce'. Depth and signal are paramount."""

    # Use agent team mode for deep research as suggested by crypto-cog skill
    result = client.create_chat(
        prompt=prompt,
        notify_session_key="agent:main:main",
        task_label="morning-trench-stats",
        chat_mode="agent team"
    )
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
