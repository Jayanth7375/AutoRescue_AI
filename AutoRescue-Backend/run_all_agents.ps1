# AutoRescue AI - Start All Backend Services
# Correct readiness checks:
# - uAgents (8011, 8013, 8015, 8018): TCP port readiness
# - FastAPI Gateway (8000): HTTP GET /health + OpenAPI check

$ErrorActionPreference = "Stop"

$root = $PSScriptRoot

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      AutoRescue AI Backend Startup       " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# TCP port readiness check for uAgents
function Wait-ForTcpPort {
    param(
        [int]$Port,
        [int]$MaxRetries = 20
    )

    for ($i = 0; $i -lt $MaxRetries; $i++) {
        $ready = Test-NetConnection `
            -ComputerName "127.0.0.1" `
            -Port $Port `
            -InformationLevel Quiet `
            -WarningAction SilentlyContinue

        if ($ready) {
            return $true
        }

        Start-Sleep -Milliseconds 500
    }

    return $false
}

# HTTP health check for FastAPI Gateway
function Wait-ForHttpHealth {
    param(
        [int]$Port,
        [int]$MaxRetries = 20
    )

    for ($i = 0; $i -lt $MaxRetries; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/health" `
                -TimeoutSec 2 `
                -ErrorAction Stop

            if ($response.StatusCode -eq 200) {
                return $true
            }
        }
        catch {
            # Continue retrying
        }

        Start-Sleep -Milliseconds 500
    }

    return $false
}

# Check if FastAPI has the /api/autorescue/check endpoint
function Verify-OpenApiEndpoint {
    param(
        [int]$Port
    )

    try {
        $spec = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/openapi.json" `
            -TimeoutSec 2 `
            -ErrorAction Stop

        $paths = $spec.paths.PSObject.Properties.Name
        return ($paths -contains "/api/autorescue/check")
    }
    catch {
        return $false
    }
}

function Start-AutoRescueAgent {
    param(
        [string]$Name,
        [string]$Command,
        [int]$Port
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

    Write-Host ("  Waiting for port {0}..." -f $Port) -ForegroundColor Gray

    if (Wait-ForTcpPort -Port $Port) {
        Write-Host "READY: $Name" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "FAILED: $Name did not become ready" -ForegroundColor Red
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        return $false
    }
}

function Start-FastApiGateway {
    param(
        [string]$Name,
        [string]$Command,
        [int]$Port
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

    Write-Host ("  Waiting for HTTP health on port {0}..." -f $Port) -ForegroundColor Gray

    if (Wait-ForHttpHealth -Port $Port) {
        Write-Host ("  Verifying /api/autorescue/check endpoint..." -f $Port) -ForegroundColor Gray

        if (Verify-OpenApiEndpoint -Port $Port) {
            Write-Host "READY: $Name" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "FAILED: $Name missing /api/autorescue/check endpoint" -ForegroundColor Red
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            return $false
        }
    }
    else {
        Write-Host "FAILED: $Name did not respond to /health" -ForegroundColor Red
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        return $false
    }
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

# Start Diagnostic Agent
if (-not (Start-AutoRescueAgent `
    -Name "Diagnostic Agent :8011" `
    -Command "uv run python run_diagnostic_agent.py" `
    -Port 8011)) {
    exit 1
}
Write-Host ""

# Start Service Agent
if (-not (Start-AutoRescueAgent `
    -Name "Service Agent :8013" `
    -Command "uv run python run_service_agent.py" `
    -Port 8013)) {
    exit 1
}
Write-Host ""

# Start Rescue Agent
if (-not (Start-AutoRescueAgent `
    -Name "Rescue Agent :8015" `
    -Command "uv run python run_rescue_agent.py" `
    -Port 8015)) {
    exit 1
}
Write-Host ""

# Start Orchestrator Agent
if (-not (Start-AutoRescueAgent `
    -Name "Orchestrator Agent :8018" `
    -Command "uv run python run_orchestrator_agent.py" `
    -Port 8018)) {
    exit 1
}
Write-Host ""


# Start FastAPI Gateway
if (-not (Start-FastApiGateway `
    -Name "FastAPI Gateway :8000" `
    -Command "uv run uvicorn main:app --host 0.0.0.0 --port 8000" `
    -Port 8000)) {
    exit 1
}
Write-Host ""

Write-Host "==========================================" -ForegroundColor Green
Write-Host " AutoRescue AI services have been started " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  FastAPI Gateway     : http://127.0.0.1:8000"
Write-Host "  Swagger UI          : http://127.0.0.1:8000/docs"
Write-Host ""
Write-Host "  Agents (4-Agent Stable Demo Architecture):" -ForegroundColor Cyan
Write-Host "    Diagnostic Agent    : port 8011"
Write-Host "    Service Agent       : port 8013"
Write-Host "    Rescue Agent        : port 8015"
Write-Host "    Orchestrator Agent  : port 8018"

Write-Host ""
Write-Host "Next step:" -ForegroundColor Yellow
Write-Host "  uv run python test_gateway.py"
Write-Host "  uv run python test_chat.py"
Write-Host "  uv run python test_multi_agent.py"
Write-Host ""

# Keep script running
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

while ($true) {
    Start-Sleep -Seconds 5
}
