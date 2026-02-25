# API Usage & Token Optimization Report
*Updated: 2026-02-20 14:34 MST*

## Current Status
- **Model:** anthropic/claude-sonnet-4-5 ($3.00/MTok)
- **Session Tokens:** 42.3K (this conversation)
- **Available Budget:** Not tracked (token_tracker needs integration)

## Immediate Optimizations Implemented ✅

### 1. Context Loading Strategy
**Status:** Optimized AGENTS.md generated
- **Location:** `AGENTS.md.optimized`
- **Action Required:** Review and replace current AGENTS.md
- **Expected Savings:** 50-80% context token reduction

**Key Changes:**
- Lazy loading: Only load SOUL.md + IDENTITY.md by default
- Conditional loading: Load MEMORY.md, USER.md, TOOLS.md only when needed
- Never auto-load: docs/*, old memory logs, knowledge base

### 2. Heartbeat Optimization
**Status:** Template created
- **Location:** `HEARTBEAT.md.optimized`
- **Action Required:** Review and replace current HEARTBEAT.md
- **Expected Savings:** 50% reduction in heartbeat costs

**Key Features:**
- Smart interval tracking (email: 60min, calendar: 2hr, weather: 4hr)
- Quiet hours (23:00-08:00): Skip all checks
- HEARTBEAT_OK when nothing to report (minimal tokens)
- **Model enforcement: ALWAYS use Haiku for heartbeats**

### 3. Model Routing Rules
**Communication patterns → ALWAYS cheap model:**
- Greetings: hi, hey, hello
- Thanks: thanks, thank you, thx
- Acknowledgments: ok, sure, got it
- Short responses: yes, no, yep

**Background tasks → Cheap model:**
- Heartbeat checks
- Log parsing
- Data extraction
- Monitoring

**Standard work → Sonnet (current model)**
- Code writing
- File operations
- Explanations

**Complex reasoning → Opus (use sparingly)**
- Architecture design
- Deep analysis

## Action Plan

### Immediate (Do Now)
1. ✅ Generated optimized AGENTS.md → **Review and activate**
2. ✅ Created optimized HEARTBEAT.md → **Review and activate**
3. Switch heartbeat session to Haiku (if available) or cheapest model
4. Set model override for cronjobs to Haiku

### Short Term (This Week)
1. Monitor token usage patterns (use `context_optimizer.py recommend` before sessions)
2. Identify high-frequency interactions → route to cheap models
3. Audit cronjobs: Ensure all use Haiku unless content quality matters

### Long Term (Next Month)
1. Integrate token_tracker.py with real usage data
2. Consider multi-provider strategy (OpenRouter Gemini 2.5 Flash = $0.075/MTok)
3. Implement budget caps and alerts

## Cost Projections

**Current Baseline** (hypothetical 100K tokens/day):
- 50K context + 50K conversation
- All Sonnet: $0.30/day = **$9/month**

**With Optimizations:**
- 10K context (-80%) + 50K conversation (mixed models)
- Estimated: $0.09/day = **$2.70/month**
- **Savings: 70% ($6.30/month)**

**Aggressive Strategy** (using Gemini Flash for background):
- 10K context + mixed providers
- Estimated: $0.03/day = **$0.90/month**
- **Savings: 90% ($8.10/month)**

## Tools Available

```bash
# Check what context is needed for a prompt
cd skills/openclaw-token-optimizer
python scripts/context_optimizer.py recommend "<prompt>"

# Suggest appropriate model for a task
python scripts/model_router.py "<task description>"

# Check heartbeat schedule
python scripts/heartbeat_optimizer.py plan

# Check budget status
python scripts/token_tracker.py check
```

## Next Steps

**Review the optimized files:**
1. `AGENTS.md.optimized` — Context loading strategy
2. `HEARTBEAT.md.optimized` — Optimized heartbeat template

**Activate optimizations:**
```bash
# Backup current
cp AGENTS.md AGENTS.md.backup
cp HEARTBEAT.md HEARTBEAT.md.backup

# Activate optimized
mv AGENTS.md.optimized AGENTS.md
mv HEARTBEAT.md.optimized HEARTBEAT.md
```

**Test:**
- Next heartbeat should use minimal tokens
- Simple conversations should skip loading docs/memory
- Complex tasks should load only what's needed

---

**Expected Impact:** 50-80% token reduction across all operations.
