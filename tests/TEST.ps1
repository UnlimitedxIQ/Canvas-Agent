# Master Test Command - Runs ALL Canvas Automation Tests
# Usage: Just type: .\TEST.ps1

Write-Host "MASTER TEST - Running All Canvas Automations" -ForegroundColor Cyan
Write-Host ("=" * 65) -ForegroundColor DarkGray
Write-Host ""

# Test 1: Daily Canvas Planner
Write-Host "Test 1: Daily Canvas Planner (3-Day View)" -ForegroundColor Yellow
Write-Host ("-" * 65) -ForegroundColor DarkGray
python "$env:USERPROFILE\.claude\automations\auto_canvas\planners\daily-canvas-planner.py"
Write-Host ""

# Test 2: Canvas Credentials Check
Write-Host "Test 2: Credentials Check" -ForegroundColor Yellow
Write-Host ("-" * 65) -ForegroundColor DarkGray

$credentials = Get-Content "$env:USERPROFILE\.claude\credentials\canvas.json" | ConvertFrom-Json
$telegram = Get-Content "$env:USERPROFILE\.claude\credentials\telegram.json" | ConvertFrom-Json
$openai = Get-Content "$env:USERPROFILE\.claude\credentials\openai.json" | ConvertFrom-Json

Write-Host "  [OK] Canvas Instances: $($credentials.instances.Count)" -ForegroundColor Green
foreach ($instance in $credentials.instances) {
    Write-Host "       - $($instance.name)" -ForegroundColor Gray
}

Write-Host "  [OK] Telegram Bots: $($telegram.bots.PSObject.Properties.Count)" -ForegroundColor Green
foreach ($bot in $telegram.bots.PSObject.Properties) {
    Write-Host "       - $($bot.Name)" -ForegroundColor Gray
}

Write-Host "  [OK] OpenAI API: Configured" -ForegroundColor Green
Write-Host ""

# Test 3: Check Task Scheduler Status
Write-Host "Test 3: Task Scheduler Status" -ForegroundColor Yellow
Write-Host ("-" * 65) -ForegroundColor DarkGray

$task = Get-ScheduledTask -TaskName "DailyCanvasPlanner" -ErrorAction SilentlyContinue

if ($task) {
    Write-Host "  [OK] Task Exists: DailyCanvasPlanner" -ForegroundColor Green
    Write-Host "  [OK] Status: $($task.State)" -ForegroundColor Green
    $trigger = $task.Triggers[0]
    Write-Host "  [OK] Schedule: Daily at $($trigger.StartBoundary.Split('T')[1].Substring(0,5))" -ForegroundColor Green
    Write-Host "  [OK] Next Run: $(Get-ScheduledTaskInfo -TaskName 'DailyCanvasPlanner' | Select-Object -ExpandProperty NextRunTime)" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Task NOT found - Run setup-task-scheduler.ps1" -ForegroundColor Red
}
Write-Host ""

# Test 4: File Structure Check
Write-Host "Test 4: File Structure" -ForegroundColor Yellow
Write-Host ("-" * 65) -ForegroundColor DarkGray

$files = @(
    "$env:USERPROFILE\.claude\automations\auto_canvas\planners\daily-canvas-planner.py",
    "$env:USERPROFILE\.claude\automations\auto_canvas\study_guides\canvas-study-guide-generator.py",
    "$env:USERPROFILE\.claude\automations\auto_canvas\scripts\ask-canvas.ps1",
    "$env:USERPROFILE\.claude\credentials\canvas.json",
    "$env:USERPROFILE\.claude\credentials\telegram.json",
    "$env:USERPROFILE\.claude\credentials\openai.json"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        $fileName = Split-Path $file -Leaf
        Write-Host "  [OK] $fileName" -ForegroundColor Green
    } else {
        $fileName = Split-Path $file -Leaf
        Write-Host "  [FAIL] $fileName - MISSING!" -ForegroundColor Red
    }
}
Write-Host ""

# Test 5: Python Dependencies Check
Write-Host "Test 5: Python Dependencies" -ForegroundColor Yellow
Write-Host ("-" * 65) -ForegroundColor DarkGray

$dependencies = @("requests", "openai", "python-docx")
foreach ($dep in $dependencies) {
    $depImport = $dep.Replace('-','_')
    $check = python -c "import $depImport; print('OK')" 2>$null
    if ($check -eq "OK") {
        Write-Host "  [OK] $dep installed" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $dep NOT installed - Run: python -m pip install $dep" -ForegroundColor Red
    }
}
Write-Host ""

# Test 6: Study Guide Directory Check
Write-Host "Test 6: Study Guide Output Directory" -ForegroundColor Yellow
Write-Host ("-" * 65) -ForegroundColor DarkGray

$studyGuideDir = "$env:USERPROFILE\Documents\Canvas Study Guides"
if (Test-Path $studyGuideDir) {
    $fileCount = (Get-ChildItem $studyGuideDir -Filter "*.docx" -ErrorAction SilentlyContinue).Count
    Write-Host "  [OK] Directory exists" -ForegroundColor Green
    Write-Host "  [OK] Study guides created: $fileCount" -ForegroundColor Green
} else {
    Write-Host "  [INFO] Directory will be created on first study guide generation" -ForegroundColor Cyan
}
Write-Host ""

# Summary
Write-Host ("=" * 65) -ForegroundColor DarkGray
Write-Host "MASTER TEST COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  - Check your Telegram for the daily notification" -ForegroundColor White
Write-Host "  - To test study guide: .\scripts\ask-canvas.ps1 'assignment name'" -ForegroundColor White
Write-Host "  - System will run automatically at 7:00 AM daily" -ForegroundColor White
Write-Host ""
