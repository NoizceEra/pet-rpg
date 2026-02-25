# Latency Audit — Unified Scanner (2026-02-24)

**Scope:** `scripts/latency_audit.py` parsing `unified_scanner.log` for the most recent signal→execution pairs within the last minute.

| Strategy | Samples | Avg (ms) | P95 (ms) | Max (ms) |
|----------|---------|----------|----------|----------|
| PBot1    | 144     | 29,297   | 58,687   | 59,928   |

**Notes**
- Signals without a matching execution inside the 60-second expiry window are discarded to avoid stale pairs.
- FastLoop didn’t trigger during the sampled window, so it lacks data.
- Next step: instrument `execute_simmer_trade` to log the HTTP round trip + Simmer acknowledgements so we can slice client vs. venue latency.
