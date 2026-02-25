#!/usr/bin/env python3
"""Monitor configured Simmer wallets for new/increased positions."""
import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import requests

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")
CONFIG_PATH = Path("whale_targets.json")
STATE_DIR = Path("whale_states")
LOG_PATH = Path("logs/whale_signals.log")
DEFAULT_DELTA_PCT = 5.0

STATE_DIR.mkdir(exist_ok=True)
LOG_PATH.parent.mkdir(exist_ok=True)


def timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def load_config() -> List[Dict]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing {CONFIG_PATH} — add at least one target wallet")
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("whale_targets.json must be a list of target definitions")
    return data


def fetch_positions(address: str) -> List[Dict]:
    url = f"https://api.simmer.markets/api/sdk/wallet/{address}/positions"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    return payload.get("positions", [])


def load_state(address: str) -> Dict[str, float]:
    state_file = STATE_DIR / f"{address.lower()}.json"
    if not state_file.exists():
        return {}
    try:
        with open(state_file, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_state(address: str, state: Dict[str, float]) -> None:
    state_file = STATE_DIR / f"{address.lower()}.json"
    with open(state_file, "w", encoding="utf-8") as fh:
        json.dump(state, fh)


def record_signal(target: Dict, position: Dict, reason: str) -> None:
    line = (
        f"[{timestamp()}] {target.get('label', target['address'])}: {reason} — "
        f"{position.get('market_title')} | Side={position.get('side')} | Shares={position.get('shares')}"
    )
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def evaluate_target(target: Dict) -> None:
    address = target.get("address")
    if not address:
        print(f"[{timestamp()}] Skipping {target.get('label')} — no address yet", flush=True)
        return

    min_delta = float(target.get("min_delta_pct", DEFAULT_DELTA_PCT))
    positions = fetch_positions(address)
    previous_state = load_state(address)
    current_state = {}

    for pos in positions:
        token_id = pos.get("token_id") or pos.get("market_id")
        side = pos.get("side")
        shares = float(pos.get("shares", 0))
        if not token_id or not side:
            continue
        key = f"{token_id}:{side}"
        current_state[key] = shares

        prev = previous_state.get(key, 0.0)
        if shares <= 0:
            continue
        if prev == 0:
            record_signal(target, pos, "NEW POSITION")
        else:
            growth_pct = ((shares - prev) / prev) * 100 if prev else 100.0
            if growth_pct >= min_delta:
                record_signal(target, pos, f"ADD {growth_pct:.1f}%")

    save_state(address, current_state)


def run_once():
    targets = load_config()
    if not SIMMER_API_KEY:
        raise RuntimeError("SIMMER_API_KEY not set")
    for target in targets:
        evaluate_target(target)


def main():
    parser = argparse.ArgumentParser(description="Monitor whale wallets via Simmer")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between loops when --loop is set")
    args = parser.parse_args()

    if args.loop:
        while True:
            run_once()
            time.sleep(max(5, args.interval))
    else:
        run_once()


if __name__ == "__main__":
    main()
