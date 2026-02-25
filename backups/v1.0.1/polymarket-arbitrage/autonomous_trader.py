#!/usr/bin/env python3
"""
AUTONOMOUS POLYMARKET TRADING BOT V1.0
Live trading with kill switch at $0 balance.

Starting capital: $10
Strategy: Orderbook arbitrage + Risk harvesting
Position sizing: Dynamic based on edge + risk score
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

load_dotenv()

# ===================== CONFIGURATION =====================
STARTING_CAPITAL = 10.0
MIN_BALANCE_TO_CONTINUE = 0.10  # Stop if below $0.10
MIN_EDGE_TO_TRADE = 2.0  # Minimum 2% profit
MAX_POSITION_SIZE = 3.0  # Max $3 per trade
MIN_POSITION_SIZE = 0.50  # Min $0.50 per trade