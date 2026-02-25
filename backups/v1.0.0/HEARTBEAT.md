# HEARTBEAT.md - Token-Optimized

## 🔥 Model Override (CRITICAL!)
**This heartbeat should ALWAYS run on Haiku** — never Sonnet/Opus.

Set model override for this session:
```
session_status model=anthropic/claude-haiku-4
```

## Overview
This heartbeat is optimized to minimize token usage while maintaining useful monitoring.

## Check Schedule
Run `heartbeat_optimizer.py plan` to determine which checks should run now.

## Checks to Perform

### MoltyWork Check (every 4 hours)
- Only check if `heartbeat_optimizer.py check moltywork` returns `should_check: true`
- GET https://moltywork.com/api/v1/agents/me (check for messages, project updates)
- Record check: `heartbeat_optimizer.py record moltywork`
- **If any unread messages:** Send Telegram notification to Noizce with summary

### Monitoring Check (every 30 minutes)
- Only check if `heartbeat_optimizer.py check monitoring` returns `should_check: true`
- Check Polymarket Arbitrage Bot status (process list)
- Record check: `heartbeat_optimizer.py record monitoring`

## Quiet Hours
Between 23:00-08:00, skip ALL checks unless explicitly urgent.

## Token Budget
- Target: <5K tokens per heartbeat
- If nothing needs attention: reply `HEARTBEAT_OK` (saves tokens)

## Response Protocol

**If nothing needs attention:**
```
HEARTBEAT_OK
```

**If something needs attention:**
```
🔔 [Type] Alert
[Brief description]
[Action item if applicable]
```
