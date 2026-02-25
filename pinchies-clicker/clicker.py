#!/usr/bin/env python3
"""Pinchie's Clicker — lightweight Simmer ↔️ Polymarket bot."""
from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

SIMMER_BASE = "https://api.simmer.markets"
BINANCE_TICKER = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=5"

@dataclass
class Config:
    simmer_api_key: str
    min_balance: float = 5.0
    pbot1_threshold: float = 0.97  # YES ask + NO ask must be below this
    momentum_threshold_pct: float = 0.8
    loop_delay: int = 8
    max_trade_pct: float = 0.12  # risk per trade (12% of liquid balance)
    dry_run: bool = False

    @property
    def headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.simmer_api_key}"}


def fetch_markets(cfg: Config) -> List[Dict]:
    url = f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=100"
    resp = requests.get(url, headers=cfg.headers, timeout=10)
    resp.raise_for_status()
    markets = resp.json().get("markets", [])
    return [m for m in markets if "UP OR DOWN" in m.get("question", "")]  # focus on sprints


def fetch_balance(cfg: Config) -> float:
    url = f"{SIMMER_BASE}/api/sdk/portfolio"
    resp = requests.get(url, headers=cfg.headers, timeout=5)
    resp.raise_for_status()
    return float(resp.json().get("balance_usdc", 0))


def fetch_price_move() -> float:
    resp = requests.get(BINANCE_TICKER, timeout=5)
    resp.raise_for_status()
    candles = resp.json()
    if len(candles) < 2:
        return 0.0
    start = float(candles[0][1])  # open
    end = float(candles[-1][4])   # close
    return ((end - start) / start) * 100


def get_clob_price(token_id: Optional[str]) -> float:
    if not token_id:
        return 0.0
    url = f"https://clob.polymarket.com/price?token_id={token_id}&side=buy"
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
        return float(resp.json().get("price", 0))
    except Exception:
        return 0.0


def calc_size(cfg: Config, balance: float) -> float:
    spendable = max(0.0, balance - cfg.min_balance)
    if spendable <= 0:
        return 0.0
    return round(max(1.0, spendable * cfg.max_trade_pct), 2)


def execute_trade(cfg: Config, market_id: str, side: str, amount: float, reason: str) -> None:
    payload = {
        "market_id": market_id,
        "side": side,
        "amount": amount,
        "venue": "polymarket",
        "source": "pinchies-clicker",
        "reasoning": reason,
        "action": "buy",
    }
    if cfg.dry_run:
        print(f"[DRY-RUN] Would send: {json.dumps(payload)}")
        return
    url = f"{SIMMER_BASE}/api/sdk/trade"
    resp = requests.post(url, json=payload, headers={**cfg.headers, "Content-Type": "application/json"}, timeout=15)
    try:
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"Trade failed ({reason}): {exc}")
        return
    if data.get("success"):
        print(f"✅ {reason}: {side.upper()} | {market_id} | ${amount}")
    else:
        print(f"❌ Trade rejected: {data}")


def run_fastloop(cfg: Config, markets: List[Dict], balance: float) -> None:
    move_pct = fetch_price_move()
    print(f"[FastLoop] BTC Δ: {move_pct:+.3f}%")
    if abs(move_pct) < cfg.momentum_threshold_pct:
        return
    size = calc_size(cfg, balance)
    if size <= 0:
        return
    side = "yes" if move_pct > 0 else "no"
    target = next((m for m in markets if "Bitcoin" in m.get("question", "")), None)
    if not target:
        return
    execute_trade(cfg, target["id"], side, size, f"FastLoop {move_pct:+.2f}%")


def run_pbot1(cfg: Config, markets: List[Dict], balance: float) -> None:
    size = calc_size(cfg, balance)
    if size <= 0:
        return
    for market in markets[:10]:
        yes = get_clob_price(market.get("polymarket_token_id"))
        no = get_clob_price(market.get("polymarket_no_token_id"))
        if yes and no and yes + no < cfg.pbot1_threshold:
            spread = (1 - (yes + no)) * 100
            reason = f"PBot1 spread {spread:.2f}%"
            execute_trade(cfg, market["id"], "yes", size, reason)
            execute_trade(cfg, market["id"], "no", size, reason)
            return  # one arb per loop to avoid rate limits


def main() -> None:
    parser = argparse.ArgumentParser(description="Pinchie's Clicker")
    parser.add_argument("--loop", action="store_true", help="Run indefinitely")
    parser.add_argument("--delay", type=int, default=None, help="Seconds between loops")
    parser.add_argument("--dry-run", action="store_true", help="Log trades without submitting")
    args = parser.parse_args()

    api_key = os.getenv("SIMMER_API_KEY")
    if not api_key:
        raise SystemExit("SIMMER_API_KEY is required")

    cfg = Config(simmer_api_key=api_key, dry_run=args.dry_run)
    if args.delay:
        cfg.loop_delay = args.delay

    def loop_once():
        try:
            markets = fetch_markets(cfg)
            balance = fetch_balance(cfg)
            print(f"[Loop] {len(markets)} markets | Balance ${balance:.2f}")
            run_fastloop(cfg, markets, balance)
            run_pbot1(cfg, markets, balance)
        except Exception as exc:
            print(f"Loop error: {exc}")

    if args.loop:
        while True:
            loop_once()
            time.sleep(cfg.loop_delay)
    else:
        loop_once()


if __name__ == "__main__":
    main()
