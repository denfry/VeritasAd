# VeritasAd Full Modernization Setup Script (2026)
# PowerShell version for Windows.

Write-Host "рџљЂ Starting VeritasAd Modernization Setup..." -ForegroundColor Cyan

# 1. Initialize UV for all Python components
$dirs = @("backend", "bot", "parsers")
foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        Write-Host "рџ“¦ Setting up UV in $dir..." -ForegroundColor Green
        cd $dir
        uv sync
        cd ..
    }
}

# 2. Frontend setup
if (Test-Path "frontend") {
    Write-Host "рџ–јпёЏ Setting up Frontend (Next.js 15 + React 19)..." -ForegroundColor Yellow
    cd frontend
    Write-Host "Next steps: Run 'cd frontend; npm install' to finalize frontend update."
    cd ..
}

Write-Host "тЬ… Modernization complete!" -ForegroundColor Cyan
Write-Host "Use 'uv run <command>' in python dirs to start services."
Write-Host "Use 'npm run dev -- --turbo' in frontend dir for fast development."
