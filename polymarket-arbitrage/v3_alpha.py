#!/usr/bin/env python3
"""
Autonomous execution engine for Polymarket Arbitrage & Strategy.
V3.0 - ALPHA INTELLIGENCE MODE
Integrates with CellCog (Crypto-Cog) for deep research pass on potential arbs.
"""

import json
import time
import sys
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows encoding issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from alpha_evaluator import AlphaEvaluator

load_dotenv(override=True)

# Constants
MAX_POSITION_SIZE = 5.60
MIN_NET_EDGE = 3.0
TAKER_FEE = 0.02
HOST = "https://clob.polymarket.com"
CHAIN_ID = 137

# Workspace Paths
WORKSPACE_DIR = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace\polymarket-arbitrage")
FORENSICS_DIR = WORKSPACE_DIR / "forensics"
STATE_FILE = WORKSPACE_DIR / "alpha_state.json"

class AlphaEngine:
    def __init__(self):
        self.evaluator = AlphaEvaluator()
        self.researched_markets = self.load_state()
        self.client = self.get_client()

    def get_client(self):
        creds = ApiCreds(
            api_key=os.getenv("POLYMARKET_API_KEY"),
            api_secret=os.getenv("POLYMARKET_API_SECRET"),
            api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE")
        )
        # Using signature_type=1 (POLY_PROXY) for Magic Link accounts
        return ClobClient(
            host=HOST, 
            key=os.getenv("POLYMARKET_PRIVATE_KEY"), 
            chain_id=CHAIN_ID, 
            creds=creds,
            signature_type=int(os.getenv("POLYMARKET_SIGNATURE_TYPE", "1")),
            funder=os.getenv("POLYMARKET_FUNDER")
        )

    def load_state(self):
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                return set(json.load(f))
        return set()

    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(list(self.researched_markets), f)

    def log_trade(self, market_name, strategy, size, risk_score, details=None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "market": market_name,
            "strategy": strategy,
            "size": size,
            "status": "PAPER_ENTERED",
            "risk_score": risk_score,
            "details": details
        }
        filename = f"trade_{strategy}_{int(time.time() * 1000)}.json"
        with open(FORENSICS_DIR / filename, "w", encoding='utf-8') as f:
            json.dump(entry, f, indent=2)

    def strategy_alpha_intelligence(self, market, trigger_reason):
        question = market.get('question')
        if not question or question in self.researched_markets:
            return

        tokens = market.get('tokens', [])
        outcomes = [t['outcome'] for t in tokens]
        
        # Trigger deep research pass
        result = self.evaluator.evaluate_market(question, outcomes)
        
        if result:
            self.researched_markets.add(question)
            self.save_state()
            
            provider = result.get("provider")
            details = {
                "trigger": trigger_reason,
                "provider": provider,
                "outcomes": outcomes
            }
            
            if provider == "cellcog":
                details["chat_id"] = result.get("id")
            elif provider == "perplexity":
                details["data_summary"] = result.get("data")[:200]
            elif provider == "manual":
                # Print to stdout so the user sees it in the heartbeat/logs
                print(f"\n[MANUAL RESEARCH NEEDED] {question}")
                print(f"Trigger: {trigger_reason}")
                sys.stdout.flush()

            self.log_trade(question, "alpha_intelligence", 0, 80, details)

    def run(self):
        print("Engine V3.0 - ALPHA INTELLIGENCE MODE")
        print("Scanning for math arbs, risk harvests, and alpha signals...")
        sys.stdout.flush()
        
        while True:
            try:
                resp = self.client.get_sampling_markets()
                markets = resp.get('data', []) if isinstance(resp, dict) else []
                
                if not markets:
                    time.sleep(10)
                    continue

                print(f"[{datetime.now().strftime('%H:%M:%S')}] Scanned {len(markets)} markets.")
                sys.stdout.flush()
                
                for m in markets:
                    try:
                        # 1. Math Arb Check
                        tokens = m.get('tokens', [])
                        if len(tokens) >= 2:
                            prices = [t.get('price') for t in tokens if t.get('price') is not None]
                            if len(prices) == len(tokens):
                                prob_sum = sum(prices) * 100
                                net_profit = (100 - prob_sum) - (TAKER_FEE * 100 * len(tokens))
                                
                                if net_profit >= MIN_NET_EDGE:
                                    self.log_trade(m['question'], "math_arb", MAX_POSITION_SIZE * len(tokens), 50, {"profit": net_profit})
                                    # Trigger Alpha Brain for high-edge arbs
                                    if net_profit > 5.0:
                                        self.strategy_alpha_intelligence(m, f"High-profit Arb: {net_profit:.1f}%")

                        # 2. Risk Harvesting Check
                        for token in tokens:
                            price = token.get('price')
                            if price is not None and price < 0.02:
                                self.log_trade(m['question'], "risk_harvest", MAX_POSITION_SIZE, 15, {"outcome": token['outcome'], "price": price})
                                # Trigger Alpha Brain for extreme dips (risk harvests)
                                self.strategy_alpha_intelligence(m, f"Risk Harvest (Price: {price})")

                    except Exception as e:
                        pass
                
                self.save_state()
                
            except Exception as e:
                print(f"Engine Error: {e}")
                
            time.sleep(60) # Scan every minute

if __name__ == "__main__":
    FORENSICS_DIR.mkdir(exist_ok=True)
    engine = AlphaEngine()
    engine.run()
