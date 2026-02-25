#!/usr/bin/env python3
"""
Automatic model switcher - switches to Ollama when token usage is high.
Usage: python scripts/auto_model_switch.py [--force-ollama|--force-qwen|--check]
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

CONFIG_FILE = Path(r"C:\Users\vclin_jjufoql\.openclaw\openclaw.json")
STATE_FILE = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace\memory\model-switch-state.json")

# Models
QWEN_MODEL = "qwen-portal/coder-model"
OLLAMA_MODEL = "ollama/glm-4.7-flash:latest"

def load_state():
    """Load model switch state."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "current_model": QWEN_MODEL,
        "switched_to_ollama": False,
        "last_switch": None,
        "switch_count": 0
    }

def save_state(state):
    """Save model switch state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def load_config():
    """Load OpenClaw config."""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """Save OpenClaw config."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def switch_model(model_name, reason="manual"):
    """Switch to specified model."""
    config = load_config()
    config['agents']['defaults']['model']['primary'] = model_name
    save_config(config)
    
    state = load_state()
    state["current_model"] = model_name
    state["switched_to_ollama"] = (model_name == OLLAMA_MODEL)
    state["last_switch"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if reason != "check":
        state["switch_count"] += 1
    save_state(state)
    
    return True

def check_status():
    """Print current model status."""
    config = load_config()
    state = load_state()
    current = config['agents']['defaults']['model']['primary']
    
    # Use UTF-8 encoding for output
    print("=" * 50, flush=True)
    print("[CRAB] Pinchie Model Switcher", flush=True)
    print("=" * 50, flush=True)
    print(f"Current model: {current}", flush=True)
    print(f"Ollama active: {state['switched_to_ollama']}", flush=True)
    print(f"Switch count: {state['switch_count']}", flush=True)
    print(f"Last switch: {state['last_switch'] or 'Never'}", flush=True)
    print("=" * 50, flush=True)
    print("\nAvailable models:", flush=True)
    print("  - qwen-portal/coder-model (alias: qwen) - Cloud, unlimited", flush=True)
    print("  - ollama/glm-4.7-flash:latest (alias: ollama-flash) - Local, 29.9B", flush=True)
    print("  - ollama/qwen3:8b (alias: ollama-qwen) - Local, 8.2B", flush=True)
    print("  - ollama/llama3.2:3b (alias: ollama-llama3b) - Local, 3.2B", flush=True)
    print("  - ollama/llama3.2:1b (alias: ollama-llama1b) - Local, 1.2B", flush=True)
    print("=" * 50, flush=True)
    print("\nCommands:", flush=True)
    print("  --force-ollama   : Switch to local Ollama (GLM-4.7-Flash)", flush=True)
    print("  --force-qwen     : Switch back to Qwen Portal", flush=True)
    print("  --check          : Show current status (default)", flush=True)
    print("  --list           : List all available models", flush=True)
    print("=" * 50, flush=True)

def main():
    args = sys.argv[1:]
    
    if "--force-ollama" in args:
        print("Switching to Ollama (GLM-4.7-Flash)...", flush=True)
        switch_model(OLLAMA_MODEL, "force-ollama")
        print(f"[OK] Switched to {OLLAMA_MODEL}", flush=True)
        print("  You can now continue working with zero token cost!", flush=True)
    elif "--force-qwen" in args:
        print("Switching to Qwen Portal...", flush=True)
        switch_model(QWEN_MODEL, "force-qwen")
        print(f"[OK] Switched to {QWEN_MODEL}", flush=True)
    elif "--list" in args:
        config = load_config()
        models = config.get('agents', {}).get('defaults', {}).get('models', {})
        print("\nConfigured model aliases:", flush=True)
        for model, info in models.items():
            alias = info.get('alias', 'none')
            print(f"  {model} => {alias}", flush=True)
    else:
        check_status()

if __name__ == "__main__":
    main()
