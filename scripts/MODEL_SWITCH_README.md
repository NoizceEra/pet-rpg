# Automatic Model Switcher

Switch between Qwen Portal (cloud) and Ollama (local) models to save tokens.

## Quick Commands

```bash
# Check current model status
python scripts/auto_model_switch.py --check

# Switch to local Ollama (zero token cost)
python scripts/auto_model_switch.py --force-ollama

# Switch back to Qwen Portal
python scripts/auto_model_switch.py --force-qwen

# List all configured models
python scripts/auto_model_switch.py --list
```

## OpenClaw Commands

You can also switch models directly in chat:

```
/model ollama-flash        # Switch to Ollama GLM-4.7-Flash
/model qwen                # Switch to Qwen Portal
session_status model=ollama/glm-4.7-flash:latest
```

## Automatic Monitoring (Optional)

To set up automatic switching when token usage is high, add this to your cron:

```bash
# Check every 30 minutes during work hours (8 AM - 6 PM)
*/30 8-18 * * * python C:\Users\vclin_jjufoql\.openclaw\workspace\scripts\auto_model_switch.py --check
```

## Available Models

| Model | Alias | Size | Location |
|-------|-------|------|----------|
| qwen-portal/coder-model | qwen | - | Cloud (unlimited) |
| ollama/glm-4.7-flash:latest | ollama-flash | 29.9B | Local |
| ollama/qwen3:8b | ollama-qwen | 8.2B | Local |
| ollama/llama3.2:3b | ollama-llama3b | 3.2B | Local |
| ollama/llama3.2:1b | ollama-llama1b | 1.2B | Local |

## When to Switch

**Stay on Qwen (default):**
- Normal development work
- Complex reasoning tasks
- When you have token budget remaining

**Switch to Ollama:**
- Token usage > 80%
- Simple tasks (file edits, quick questions)
- When you need to conserve tokens
- Long coding sessions

**Recommended workflow:**
1. Start session on Qwen (best quality)
2. Monitor token usage with `--check`
3. Switch to `ollama-flash` when approaching limits
4. Switch back to Qwen for complex tasks when needed
