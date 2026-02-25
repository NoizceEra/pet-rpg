#!/usr/bin/env python3
import sys
import json
from pathlib import Path

# This script is intended to be called by the agent to generate the UI payload
# It prints a JSON that the agent can use in the 'message' tool.

def generate_ui():
    menu = {
        "text": "🦅 *THE VULTURE: COMMAND & CONTROL*\n\nSelect a preset or tune specific parameters below.",
        "buttons": [
            [
                {"text": "🛡️ Conservative", "callback_data": "/vulture_preset_conservative"},
                {"text": "⚖️ Moderate", "callback_data": "/vulture_preset_moderate"},
                {"text": "🦍 Ape", "callback_data": "/vulture_preset_ape"}
            ],
            [
                {"text": "📊 Status", "callback_data": "/vulture_status"},
                {"text": "💼 Positions", "callback_data": "/vulture_positions"},
                {"text": "🛑 Stop All", "callback_data": "/vulture_stop"}
            ],
            [
                {"text": "📉 Set Stop Loss", "callback_data": "/vulture_menu_sl"},
                {"text": "🚀 Set Max Buy", "callback_data": "/vulture_menu_buy"},
                {"text": "🔄 Refresh", "callback_data": "/vulture"}
            ]
        ]
    }
    print(json.dumps(menu))

if __name__ == "__main__":
    generate_ui()
