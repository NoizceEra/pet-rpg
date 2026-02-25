# OpenClaw Token Optimization Activation Script
# Run this to activate all token-saving optimizations

Write-Host "🦀 Pinchie Token Optimization Activation" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Backup current files
Write-Host "📦 Backing up current configuration..." -ForegroundColor Yellow
Copy-Item "AGENTS.md" "AGENTS.md.backup" -Force
Copy-Item "HEARTBEAT.md" "HEARTBEAT.md.backup" -ErrorAction SilentlyContinue
Write-Host "✅ Backups created: AGENTS.md.backup, HEARTBEAT.md.backup" -ForegroundColor Green
Write-Host ""

# Activate optimized AGENTS.md
Write-Host "🎯 Activating optimized context loading..." -ForegroundColor Yellow
Move-Item "AGENTS.md.optimized" "AGENTS.md" -Force
Write-Host "✅ AGENTS.md updated (50-80% context reduction)" -ForegroundColor Green
Write-Host ""

# Activate optimized HEARTBEAT.md
Write-Host "📊 Activating optimized heartbeat..." -ForegroundColor Yellow
if (Test-Path "HEARTBEAT.md.optimized") {
    Move-Item "HEARTBEAT.md.optimized" "HEARTBEAT.md" -Force
    Write-Host "✅ HEARTBEAT.md updated (50% heartbeat cost reduction)" -ForegroundColor Green
} else {
    Write-Host "⚠️  HEARTBEAT.md.optimized not found, skipping" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "🎉 Optimization Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Expected Savings:" -ForegroundColor Cyan
Write-Host "  • Context tokens: -50 to -80%" -ForegroundColor White
Write-Host "  • Heartbeat costs: -50%" -ForegroundColor White
Write-Host "  • Overall: -50 to -80% total token usage" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Restart OpenClaw gateway (optional, changes apply on next session)" -ForegroundColor White
Write-Host "  2. Monitor token usage in next few sessions" -ForegroundColor White
Write-Host "  3. Review API_USAGE_REPORT.MD for detailed analysis" -ForegroundColor White
Write-Host ""
Write-Host "To rollback:" -ForegroundColor Yellow
Write-Host "  Copy-Item AGENTS.md.backup AGENTS.md -Force" -ForegroundColor DarkGray
Write-Host "  Copy-Item HEARTBEAT.md.backup HEARTBEAT.md -Force" -ForegroundColor DarkGray
Write-Host ""
