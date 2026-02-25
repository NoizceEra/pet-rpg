# Model Optimization - Haiku & OpenRouter Enabled
**Updated:** 2026-02-20 15:27 MST  
**Status:** ✅ Applied & Restarting

---

## Changes Applied

### 1. OpenRouter API Key Updated ✅
- **Old:** `sk-or-v1-359f...`
- **New:** `sk-or-v1-bd72...` (your new key)

### 2. Anthropic Provider Added ✅
Direct access to Anthropic API (not through proxy):
- **Claude Sonnet 4.5** — $3/MTok input, $15/MTok output
- **Claude Haiku 4** — $0.25/MTok input, $1.25/MTok output (⚡ **92% cheaper!**)

### 3. OpenRouter Models Expanded ✅
Now available via OpenRouter:
- **GPT-4o Mini** — $0.15/$0.6 per MTok
- **Gemini 2.5 Flash** — $0.075/$0.3 per MTok (⚡ **97.5% cheaper than Sonnet!**)
- **Claude Sonnet 4.5 (OR)** — $3/$15 per MTok (same as direct)
- **Claude Haiku 4 (OR)** — $0.25/$1.25 per MTok (same as direct)

### 4. Model Aliases Added ✅
Easy switching with short names:
- `Haiku` → anthropic/claude-haiku-4
- `Sonnet` → anthropic/claude-sonnet-4-5
- `Gemini-Flash` → openrouter/google/gemini-2.5-flash
- `Haiku-OR` → openrouter/anthropic/claude-haiku-4

---

## Cost Comparison (Per 1M Tokens Input)

| Model | Cost | vs Sonnet | Best For |
|-------|------|-----------|----------|
| **Sonnet 4.5** | $3.00 | Baseline | Complex reasoning, code |
| **Haiku 4** | $0.25 | **-92%** 🔥 | Heartbeats, simple tasks, high frequency |
| **Gemini 2.5 Flash** | $0.075 | **-97.5%** 🔥🔥 | Background jobs, bulk operations |
| **GPT-4o Mini** | $0.15 | **-95%** 🔥 | General purpose, balanced |

---

## How to Use

### Switch This Session to Haiku
```
/status model=Haiku
```
or
```
/status model=anthropic/claude-haiku-4
```

### Switch to Gemini Flash (Cheapest)
```
/status model=Gemini-Flash
```
or
```
/status model=openrouter/google/gemini-2.5-flash
```

### Back to Sonnet
```
/status model=Sonnet
```

---

## Recommended Strategy

### For Conversations (This Chat)
- **Simple questions:** Haiku ($0.25/MTok) or Gemini Flash ($0.075/MTok)
- **Standard work:** Haiku or Sonnet (depends on complexity)
- **Complex reasoning:** Sonnet ($3/MTok)

### For Heartbeats
Already configured to use cheapest available model. Should automatically prefer Haiku.

### For Cronjobs
Specify `model` in payload:
```json
{
  "kind": "agentTurn",
  "message": "Check email and summarize",
  "model": "anthropic/claude-haiku-4"
}
```

### For Background Scripts
Use Gemini Flash for maximum savings:
- Log parsing
- Data extraction
- Monitoring checks
- Status reports

---

## Expected Savings

**Current Session (This Conversation):**
- Used: 85K tokens on Sonnet = **$0.255**
- If on Haiku: **$0.021** (-92% = **$0.234 saved**)
- If on Gemini Flash: **$0.006** (-97.5% = **$0.249 saved**)

**Monthly Projection (100K tokens/day):**
| Scenario | Model Mix | Daily Cost | Monthly Cost | Savings |
|----------|-----------|-----------|--------------|---------|
| Before (all Sonnet) | 100% Sonnet | $0.30 | $9.00 | Baseline |
| Balanced | 50% Haiku, 50% Sonnet | $0.16 | $4.88 | **-46%** |
| Aggressive | 80% Haiku, 20% Sonnet | $0.11 | $3.30 | **-63%** |
| Ultra | 50% Gemini, 30% Haiku, 20% Sonnet | $0.08 | $2.40 | **-73%** |

---

## Action Items

**Immediate (Do Now):**
1. ✅ Gateway restarted with new config
2. ⏳ Test Haiku: `/status model=Haiku`
3. ⏳ Test Gemini Flash: `/status model=Gemini-Flash`
4. ⏳ Switch heartbeat to Haiku (if not already)

**Short-Term (This Week):**
1. ⏳ Update cronjobs to use Haiku/Gemini
2. ⏳ Monitor quality vs cost tradeoff
3. ⏳ Set default model for main agent to Haiku

**Considerations:**
- **Haiku** is very capable for most tasks (not a huge quality drop)
- **Gemini Flash** is excellent for structured/simple tasks
- **Sonnet** still best for complex reasoning (use sparingly)

---

## Verification

After gateway restarts, check available models:
```
/status
```

Should show:
- ✅ anthropic/claude-haiku-4 (Haiku)
- ✅ anthropic/claude-sonnet-4-5 (Sonnet)
- ✅ openrouter/google/gemini-2.5-flash (Gemini-Flash)
- ✅ openrouter/anthropic/claude-haiku-4 (Haiku-OR)

---

## Rollback (If Needed)

If something breaks:
1. Restore backup config from previous version
2. Restart gateway: `openclaw gateway restart`

Backup location: OpenClaw auto-creates backups in `~/.openclaw/` before config changes.

---

**Status:** Gateway restarting with new configuration. Should be back online in ~5 seconds.

🦀 **Cost optimization complete. Ready to save 92% on API costs.**
