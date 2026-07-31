# AutoRescue AI - 20-Agent Service Status Checker (PowerShell)
# Robust replacement for broken batch checker

$ErrorActionPreference = "SilentlyContinue"

Write-Host ""
Write-Host "===================================================================="
Write-Host "   AutoRescue AI - 20-Agent System Status Check"
Write-Host "===================================================================="
Write-Host ""

# Define all services
$services = @(
    @{ Port = 8000; Name = "FastAPI Backend"; IsAgent = $false }
    @{ Port = 8011; Name = "Diagnostic Agent"; IsAgent = $true }
    @{ Port = 8013; Name = "Service Agent"; IsAgent = $true }
    @{ Port = 8015; Name = "Rescue Agent"; IsAgent = $true }
    @{ Port = 8018; Name = "Orchestrator Agent"; IsAgent = $true }
    @{ Port = 8020; Name = "Telemetry Agent"; IsAgent = $true }
    @{ Port = 8021; Name = "Safety Agent"; IsAgent = $true }
    @{ Port = 8022; Name = "Maintenance Agent"; IsAgent = $true }
    @{ Port = 8023; Name = "Notification Agent"; IsAgent = $true }
    @{ Port = 8024; Name = "Explanation Agent"; IsAgent = $true }
    @{ Port = 8025; Name = "Verification Agent"; IsAgent = $true }
    @{ Port = 8026; Name = "Vehicle Profile Agent"; IsAgent = $true }
    @{ Port = 8027; Name = "Battery Health Agent"; IsAgent = $true }
    @{ Port = 8028; Name = "Tyre Health Agent"; IsAgent = $true }
    @{ Port = 8029; Name = "Engine Health Agent"; IsAgent = $true }
    @{ Port = 8030; Name = "Breakdown Classification Agent"; IsAgent = $true }
    @{ Port = 8031; Name = "Passenger Safety Agent"; IsAgent = $true }
    @{ Port = 8032; Name = "Nearby Assistance Agent"; IsAgent = $true }
    @{ Port = 8033; Name = "Service Ranking Agent"; IsAgent = $true }
    @{ Port = 8034; Name = "Incident Memory Agent"; IsAgent = $true }
    @{ Port = 8035; Name = "Agent Health Monitor"; IsAgent = $true }
)

$onlineCount = 0
$offlineCount = 0
$portStatus = @{}

# Check each service
foreach ($service in $services) {
    $port = $service.Port
    $name = $service.Name

    try {
        $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue

        if ($conn) {
            # Port is listening
            $portStatus[$port] = $true

            if ($service.IsAgent) {
                $onlineCount++
            }

            Write-Host "[OK] $name - port $port"
        } else {
            $portStatus[$port] = $false

            if ($service.IsAgent) {
                $offlineCount++
            }

            Write-Host "[FAIL] $name - port $port NOT RUNNING"
        }
    } catch {
        $portStatus[$port] = $false

        if ($service.IsAgent) {
            $offlineCount++
        }

        Write-Host "[FAIL] $name - port $port (error checking)"
    }
}

Write-Host ""
Write-Host "===================================================================="
Write-Host "   Service Status Summary"
Write-Host "===================================================================="
Write-Host ""

# FastAPI health check
$fastApiOnline = $portStatus[8000]
if ($fastApiOnline) {
    Write-Host "FastAPI Port:   ONLINE"

    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 3 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $data = $response.Content | ConvertFrom-Json
            if ($data.status -eq "ok") {
                Write-Host "FastAPI Health: OK"
            } else {
                Write-Host "FastAPI Health: DEGRADED"
            }
        }
    } catch {
        Write-Host "FastAPI Health: NOT RESPONDING"
    }
} else {
    Write-Host "FastAPI Port:   OFFLINE"
    Write-Host "FastAPI Health: UNAVAILABLE"
}

Write-Host ""
Write-Host "Agents Online:  $onlineCount/20"
Write-Host "Agents Offline: $offlineCount/20"
Write-Host ""

$totalOnline = if ($fastApiOnline) { $onlineCount + 1 } else { $onlineCount }
$totalServices = 21
$totalOffline = $totalServices - $totalOnline

Write-Host "Total Services Online:  $totalOnline/$totalServices"
Write-Host "Total Services Offline: $totalOffline/$totalServices"
Write-Host ""

if ($totalOffline -eq 0) {
    Write-Host "SUCCESS All 21 services ONLINE - System ready"
} else {
    Write-Host "WARNING $totalOffline service(s) offline - Check logs"
}

Write-Host ""
Write-Host "===================================================================="
Write-Host ""
