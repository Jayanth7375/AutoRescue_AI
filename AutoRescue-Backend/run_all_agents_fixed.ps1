# AutoRescue AI - Start All Backend Services (Fixed Version)
# Starts:
# 1. Diagnostic Agent
# 2. Service Agent
# 3. Rescue Agent
# 4. Orchestrator Agent
# 5. FastAPI Gateway

$ErrorActionPreference = "Stop"

$root = $PSScriptRoot

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      AutoRescue AI Backend Startup       " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

function Start-AutoRescueProcess {
    param(
        [string]$Name,
        [string]$Command,
        [int]$Port = 0,
        [bool]$CheckHealth = $false
    )

    Write-Host "Starting $Name..." -ForegroundColor Yellow

    $fullCommand = "Set-Location -LiteralPath `"$root`"; & { $Command } 2>&1"

    $process = Start-Process `
        -FilePath "powershell.exe" `
        -ArgumentList @(
            "-NoExit",
            "-Command",
            $fullCommand
        ) `
        -PassThru

    Write-Host ("  Process started (PID: {0})" -f $process.Id) -ForegroundColor Gray
    Start-Sleep -Seconds 3

    if ($CheckHealth -and $Port -gt 0) {
        $maxRetries = 20
        $retry = 0
        $healthCheckPassed = $false

        Write-Host ("  Health checking on port {0}..." -f $Port) -ForegroundColor Gray

        while ($retry -lt $maxRetries) {
            try {
                $response = Invoke-WebRequest -Uri ("http://127.0.0.1:{0}/health" -f $Port) -TimeoutSec 2 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Write-Host "$Name health check PASSED" -ForegroundColor Green
                    $healthCheckPassed = $true
                    break
                }
            }
            catch {
                $retry++
                if ($retry -lt $maxRetries) {
                    Write-Host ("    Attempt {0}/{1}..." -f $retry, $maxRetries) -ForegroundColor Gray
                    Start-Sleep -Seconds 1
                }
            }
        }

        if (-not $healthCheckPassed) {
            Write-Host ""
            Write-Host ("FAILED: {0} did not respond to health check after {1} attempts" -f $Name, $maxRetries) -ForegroundColor Red
            Write-Host ("  Killing process PID {0}..." -f $process.Id) -ForegroundColor Yellow
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            Write-Host ""
            Write-Host "Troubleshooting:" -ForegroundColor Yellow
            Write-Host ("  1. Check if port {0} is already in use" -f $Port)
            Write-Host ("  2. Check agent logs in spawned PowerShell windows")
            Write-Host "  3. Verify .env has correct configuration"
            Write-Host ""
            exit 1
        }
    }
    else {
        Write-Host "$Name started successfully" -ForegroundColor Green
    }

    Write-Host ""
    return $process
}

# Cleanup: Kill any existing processes on these ports first
Write-Host "Pre-startup: Cleaning up any existing processes..." -ForegroundColor Yellow
$ports = @(8011, 8013, 8015, 8018, 8000)
foreach ($p in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        Write-Host ("  Stopping PID {0} on port {1}..." -f $conn.OwningProcess, $p) -ForegroundColor Gray
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "Waiting 3 seconds for ports to release..." -ForegroundColor Gray
Start-Sleep -Seconds 3
Write-Host ""

# ------------------------------------------
# Diagnostic Agent
# ------------------------------------------

Start-AutoRescueProcess `
    -Name "Diagnostic Agent :8011" `
    -Command "uv run python run_diagnostic_agent.py" `
    -Port 8011 `
    -CheckHealth $true

# ------------------------------------------
# Service Agent
# ------------------------------------------

Start-AutoRescueProcess `
    -Name "Service Agent :8013" `
    -Command "uv run python run_service_agent.py" `
    -Port 8013 `
    -CheckHealth $true

# ------------------------------------------
# Rescue Agent
# ------------------------------------------

Start-AutoRescueProcess `
    -Name "Rescue Agent :8015" `
    -Command "uv run python run_rescue_agent.py" `
    -Port 8015 `
    -CheckHealth $true

# ------------------------------------------
# Orchestrator Agent
# ------------------------------------------

Start-AutoRescueProcess `
    -Name "Orchestrator Agent :8018" `
    -Command "uv run python run_orchestrator_agent.py" `
    -Port 8018 `
    -CheckHealth $true

# Give all agents time to fully initialize
Write-Host "Waiting 5 seconds for agents to fully initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host ""

# ------------------------------------------
# FastAPI Gateway
# ------------------------------------------

Start-AutoRescueProcess `
    -Name "FastAPI Gateway :8000" `
    -Command "uv run uvicorn main:app --host 0.0.0.0 --port 8000" `
    -Port 8000 `
    -CheckHealth $true

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host " AutoRescue AI services have been started " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  FastAPI Gateway     : http://127.0.0.1:8000"
Write-Host "  Swagger UI          : http://127.0.0.1:8000/docs"
Write-Host "  Diagnostic Agent    : port 8011"
Write-Host "  Service Agent       : port 8013"
Write-Host "  Rescue Agent        : port 8015"
Write-Host "  Orchestrator Agent  : port 8018"

Write-Host ""
Write-Host "Next step:" -ForegroundColor Yellow
Write-Host "  uv run python test_gateway.py"
Write-Host ""

# Keep script running
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

while ($true) {
    Start-Sleep -Seconds 5
}
