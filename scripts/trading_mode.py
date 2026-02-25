#!/usr/bin/env python3
import json
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace")
CONFIG_FILE = WORKSPACE_ROOT / "trading_config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def show_status():
    cfg = load_config()
    print("\n=== THE VULTURE: TRADE CONTROLLER ===")
    print(f"Active Mode: {cfg['active_mode']}")
    print(f"Global Safety Floor: {cfg['global']['safety_floor_sol']} SOL")
    print(f"Global Max Buy: {cfg['global']['max_buy_sol']} SOL")
    
    # NEW: Semantic/Profile Overview
    if "semantic" in cfg:
        s = cfg["semantic"]
        print(f"\n[Profile: {s.get('type', 'auto').upper()}]")
        print(f"  Risk: {s.get('risk', 'medium')}")
        print(f"  Sell Pattern: {s.get('pattern', 'scale-out')}")
        print(f"  Project Type: {s.get('project', 'small cap')}")
        print(f"  Duration: {s.get('duration_hours', 4)}h")

    sn = cfg['sniper']
    print(f"\n[Sniper/Entry]")
    print(f"  Entry Mode: {sn.get('entry_mode', 'pump')}")
    print(f"  Risk Threshold: {sn['risk_threshold']}/100")
    print(f"  Min Volume (1h): ${sn['min_volume_h1']:,}")
    
    v = cfg['vulture']
    print(f"\n[Vulture/Exit]")
    print(f"  Loop Interval: {v['loop_interval_seconds']}s")
    print(f"  Stop Loss: {v['stop_loss']['roi_threshold']}x ROI")
    print(f"  Exit Stages:")
    for stage in v['exit_stages']:
        print(f"    {stage['label']}: {stage['roi']}x -> Sell {stage['sell_percent']}%")
    print("========================================\n")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        show_status()
    elif sys.argv[1] == "preset":
        # Usage: trading_mode.py preset <name>
        name = sys.argv[2].lower()
        cfg = load_config()
        
        presets = {
            "conservative": {
                "semantic": {"type": "conservative", "risk": "small", "pattern": "swing", "project": "large cap"},
                "sniper": {"risk_threshold": 30, "entry_mode": "dip", "dip_buy_threshold": 0.50},
                "vulture": {"stop_loss": {"roi_threshold": 0.85}}
            },
            "moderate": {
                "semantic": {"type": "moderate", "risk": "medium", "pattern": "scale-out", "project": "small cap"},
                "sniper": {"risk_threshold": 60, "entry_mode": "dip", "dip_buy_threshold": 0.40},
                "vulture": {"stop_loss": {"roi_threshold": 0.70}}
            },
            "ape": {
                "semantic": {"type": "ape", "risk": "degen", "pattern": "full_clip", "project": "nano cap"},
                "sniper": {"risk_threshold": 90, "entry_mode": "pump", "min_volume_h1": 5000},
                "vulture": {"stop_loss": {"roi_threshold": 0.50}, "exit_stages": [{"roi": 2.0, "sell_percent": 100, "label": "Moon or Dust"}]}
            }
        }
        
        if name in presets:
            p = presets[name]
            # Deep merge simple logic
            for section in p:
                for key, val in p[section].items():
                    if isinstance(val, dict) and key in cfg[section]:
                        cfg[section][key].update(val)
                    else:
                        cfg[section][key] = val
            save_config(cfg)
            print(f"Preset applied: {name.upper()}")
            show_status()
        else:
            print(f"Unknown preset: {name}")

    elif sys.argv[1] == "set":
        # Usage: trading_mode.py set <path> <value>
        # e.g. trading_mode.py set sniper.enabled false
        path = sys.argv[2].split(".")
        val = sys.argv[3]
        
        # Try to parse value as int/float/bool
        if val.lower() == "true": val = True
        elif val.lower() == "false": val = False
        else:
            try:
                if "." in val: val = float(val)
                else: val = int(val)
            except: pass
            
        cfg = load_config()
        ref = cfg
        for part in path[:-1]:
            ref = ref[part]
        ref[path[-1]] = val
        save_config(cfg)
        print(f"Updated {sys.argv[2]} to {val}")
        show_status()
