# Windows Task Scheduler Setup for Daily Canvas Planner
# This script creates a scheduled task that runs every morning at 7:00 AM

$TaskName = "DailyCanvasPlanner"
$ScriptPath = "$env:USERPROFILE\.claude\automations\auto_canvas\planners\daily-canvas-planner.py"
$PythonPath = (Get-Command python).Source

# Create the action (run Python script)
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath

# Create the trigger (daily at 7:00 AM)
$Trigger = New-ScheduledTaskTrigger -Daily -At 7:00AM

# Create settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
Register-ScheduledTask -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Automatically checks Canvas for assignments due today and sends Telegram notifications with action plans" `
    -Force

Write-Host "✅ Task '$TaskName' created successfully!" -ForegroundColor Green
Write-Host "📅 Will run daily at 7:00 AM" -ForegroundColor Cyan
Write-Host "🔧 To modify: Open Task Scheduler and search for '$TaskName'" -ForegroundColor Yellow
Write-Host ""
Write-Host "To test the task now, run:" -ForegroundColor Magenta
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
