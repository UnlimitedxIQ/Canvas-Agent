# Interactive Canvas Study Guide Generator
# Usage: .\ask-canvas.ps1 "create study guide for midterm"
#        .\ask-canvas.ps1 "help me study for quiz 3"

param(
    [string]$Request
)

if (-not $Request) {
    Write-Host "💬 Canvas Study Guide Generator" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\ask-canvas.ps1 'create study guide for midterm'"
    Write-Host "  .\ask-canvas.ps1 'help me study for quiz 3'"
    Write-Host "  .\ask-canvas.ps1 'study materials for final exam'"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\ask-canvas.ps1 'midterm exam'"
    Write-Host "  .\ask-canvas.ps1 'chapter 5 quiz'"
    Write-Host ""
    exit
}

# Extract assignment name from request
$AssignmentName = $Request -replace "create study guide for ", "" `
                           -replace "help me study for ", "" `
                           -replace "study materials for ", "" `
                           -replace "guide for ", ""

Write-Host "🤖 Processing request: $AssignmentName" -ForegroundColor Cyan

$PythonScript = "$env:USERPROFILE\.claude\automations\auto_canvas\study_guides\canvas-study-guide-generator.py"

python $PythonScript "$AssignmentName"
