#!/usr/bin/env python3
import json
import sys
from pathlib import Path

CONFIG_PATH = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace\mode_config.json")

def toggle(mode):
    if not CONFIG_PATH.exists():
        data = {"current_mode": "solo_pinchie", "factory_sync": False}
    else:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
    
    if mode == "shared":
        data["current_mode"] = "shared_brain"
        data["factory_sync"] = True
    else:
        data["current_mode"] = "solo_pinchie"
        data["factory_sync"] = False
        
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"Mode switched to: {data['current_mode']}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        toggle(sys.argv[1])
    else:
        print("Usage: python toggle_mode.py <solo|shared>")
