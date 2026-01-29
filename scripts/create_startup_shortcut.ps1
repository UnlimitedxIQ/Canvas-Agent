# Create a startup shortcut for Canvas Automation Bot
$startupFolder = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupFolder "Canvas Automation Bot.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "C:\\Users\\bryso\\.claude\\automations\\auto_canvas\\scripts\\start_bot.bat"
$Shortcut.WorkingDirectory = "C:\Users\bryso\.claude\automations\auto_canvas"
$Shortcut.WindowStyle = 7  # Minimized
$Shortcut.Description = "Canvas Automation Telegram Bot"
$Shortcut.Save()

Write-Host "Startup shortcut created at:" -ForegroundColor Green
Write-Host "  $shortcutPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "The bot will now start automatically (minimized) when you log in." -ForegroundColor Green
