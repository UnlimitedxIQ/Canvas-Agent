# Test the Daily Canvas Planner manually
# Run this to test the automation without waiting for the scheduled task

$ScriptPath = "$env:USERPROFILE\.claude\automations\auto_canvas\planners\daily-canvas-planner.py"

Write-Host "🧪 Testing Daily Canvas Planner..." -ForegroundColor Cyan
Write-Host ""

python $ScriptPath

Write-Host ""
Write-Host "✅ Test complete! Check your Telegram for the notification." -ForegroundColor Green
