<#
.SYNOPSIS
    Energy Mirror - Reproducible Demo Diagnostic and Startup Assistant.

.DESCRIPTION
    Checks runtime prerequisites, verifies database and web assets, checks for port
    conflicts, and tests running services without modifying any configuration or database.
    Does NOT install packages, delete databases, or overwrite .env files.

.EXAMPLE
    .\start_demo.ps1
    .\start_demo.ps1 -CheckOnly
#>

[CmdletBinding()]
param(
    [switch]$CheckOnly
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   ENERGY MIRROR - DEMO READINESS & STARTUP ASSISTANT" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$MobileDir = Join-Path $ProjectRoot "mobile"
$VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
$WebIndex = Join-Path $MobileDir "build\web\index.html"
$DatabasePath = Join-Path $ProjectRoot "energy_mirror.db"

$AllPrereqsPassed = $true

# 1. Check Python Virtual Environment
Write-Host "[1/5] Checking Python Virtual Environment..." -NoNewline
if (Test-Path $VenvPython) {
    $pyVer = & $VenvPython --version 2>&1
    Write-Host " [PASS] Found $pyVer" -ForegroundColor Green
} else {
    Write-Host " [FAIL] Missing $VenvPython" -ForegroundColor Red
    Write-Host "       Create backend virtualenv via: cd backend; python -m venv .venv; .\.venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    $AllPrereqsPassed = $false
}

# 2. Check Flutter Web Production Bundle
Write-Host "[2/5] Checking Flutter Web Production Bundle..." -NoNewline
if (Test-Path $WebIndex) {
    $idxSize = (Get-Item $WebIndex).Length
    Write-Host " [PASS] Found build\web\index.html ($idxSize bytes)" -ForegroundColor Green
} else {
    Write-Host " [FAIL] Missing $WebIndex" -ForegroundColor Red
    Write-Host "       Build web bundle via: cd mobile; flutter build web --release" -ForegroundColor Yellow
    $AllPrereqsPassed = $false
}

# 3. Check SQLite Database & Alembic Revision
Write-Host "[3/5] Checking SQLite Database Status..." -NoNewline
if (Test-Path $DatabasePath) {
    Write-Host " [PASS] Found energy_mirror.db" -ForegroundColor Green
} else {
    Write-Host " [WARN] energy_mirror.db not found in root (will be generated automatically on first startup)" -ForegroundColor Yellow
}

# 4. Check Port Availability (8000 and 5000)
Write-Host "[4/5] Checking Port Availability (8000, 5000)..."
$Port8000Active = $false
$Port5000Active = $false

try {
    $conn8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
    if ($conn8000) {
        $Port8000Active = $true
        Write-Host "       Port 8000 (Backend API): Active (PID: $($conn8000[0].OwningProcess))" -ForegroundColor Green
    } else {
        Write-Host "       Port 8000 (Backend API): Available (Not running)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "       Port 8000 check skipped." -ForegroundColor Gray
}

try {
    $conn5000 = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
    if ($conn5000) {
        $Port5000Active = $true
        Write-Host "       Port 5000 (Unified Server): Active (PID: $($conn5000[0].OwningProcess))" -ForegroundColor Green
    } else {
        Write-Host "       Port 5000 (Unified Server): Available (Not running)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "       Port 5000 check skipped." -ForegroundColor Gray
}

# 5. Live Endpoint Sanity Checks (if services are active)
Write-Host "[5/5] Verifying Service Endpoints..."
if ($Port8000Active) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -TimeoutSec 3 -ErrorAction Stop
        Write-Host "       [PASS] http://127.0.0.1:8000/api/v1/health -> status=$($health.status), db=$($health.database_connected)" -ForegroundColor Green
    } catch {
        Write-Host "       [FAIL] Port 8000 is open but health check failed: $($_.Exception.Message)" -ForegroundColor Red
    }

    try {
        $diag = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/diagnostics/system" -TimeoutSec 3 -ErrorAction Stop
        Write-Host "       [PASS] System Diagnostics -> db_type=$($diag.database_type), hw_mode=$($diag.hardware_mode), baseline=$($diag.unattributed_baseline_w)W" -ForegroundColor Green
    } catch {
        Write-Host "       [WARN] Diagnostics endpoint query failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "       Backend service is not running on port 8000." -ForegroundColor Gray
}

if ($Port5000Active) {
    try {
        $webResp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Host "       [PASS] http://127.0.0.1:5000/ -> HTTP $($webResp.StatusCode) (Flutter Web SPA root)" -ForegroundColor Green
    } catch {
        Write-Host "       [FAIL] Port 5000 is open but root query failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "       Unified server is not running on port 5000." -ForegroundColor Gray
}

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "                      STARTUP INSTRUCTIONS" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

if (-not $Port8000Active) {
    Write-Host "To start the FastAPI Backend (Terminal 1):" -ForegroundColor Yellow
    Write-Host "  cd `"$ProjectRoot`""
    Write-Host "  & `".\backend\.venv\Scripts\python.exe`" -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "FastAPI Backend is ALREADY RUNNING on port 8000." -ForegroundColor Green
    Write-Host ""
}

if (-not $Port5000Active) {
    Write-Host "To start the Unified Web & Proxy Server (Terminal 2):" -ForegroundColor Yellow
    Write-Host "  cd `"$ProjectRoot`""
    Write-Host "  & `".\backend\.venv\Scripts\python.exe`" unified_server.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "Unified Web Server is ALREADY RUNNING on port 5000." -ForegroundColor Green
    Write-Host ""
}

Write-Host "Browser Access URLs:" -ForegroundColor Cyan
Write-Host "  * Unified Web App (Recommended): http://localhost:5000" -ForegroundColor White
Write-Host "  * Swagger API Documentation:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "  * System Diagnostics:            http://localhost:8000/api/v1/diagnostics/system" -ForegroundColor White
Write-Host ""
Write-Host "To Stop Services:" -ForegroundColor Cyan
Write-Host "  Press Ctrl + C in the respective PowerShell windows." -ForegroundColor Gray
Write-Host ""
