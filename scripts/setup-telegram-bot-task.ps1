# Setup Scheduled Task for Telegram Bot Listener
# Runs at login, auto-restarts on failure

$scriptPath = Join-Path $env:USERPROFILE ".claude\automations\auto_canvas\bots\telegram-bot-listener.py"

$action = New-ScheduledTaskAction -Execute "pythonw.exe" -Argument "`"$scriptPath`""

$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
    -TaskName "TelegramCanvasBot" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Telegram bot listener for Canvas automation - responds to TEST command" `
    -Force

Write-Host "Scheduled task 'TelegramCanvasBot' created!" -ForegroundColor Green
Write-Host "The bot will start automatically when you log in." -ForegroundColor Cyan
Write-Host ""
Write-Host "To start it now, run:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName 'TelegramCanvasBot'" -ForegroundColor White
