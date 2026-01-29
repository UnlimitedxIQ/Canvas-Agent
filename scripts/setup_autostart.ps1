# Setup Canvas Bot to autostart on Windows login
$taskName = "CanvasAutomationBot"
$scriptPath = "C:\\Users\\bryso\\.claude\\automations\\auto_canvas\\scripts\\start_bot.bat"

# Remove existing task if it exists
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Create the action
$action = New-ScheduledTaskAction -Execute $scriptPath

# Create the trigger (at logon)
$trigger = New-ScheduledTaskTrigger -AtLogon

# Create the principal (run with highest privileges)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Canvas Automation Telegram Bot Server"

Write-Host "Task '$taskName' created successfully!" -ForegroundColor Green
Write-Host "The bot will start automatically when you log in." -ForegroundColor Cyan
Write-Host ""
Write-Host "To start it now, run:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
