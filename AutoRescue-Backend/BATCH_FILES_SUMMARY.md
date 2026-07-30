# AutoRescue AI - Batch Files Summary

## Overview

All batch files have been created and are ready to use. These files provide convenient ways to launch the AutoRescue AI system with different configurations.

**Location:** `c:\Users\Jayanth\Downloads\AutoRescueAI\AutoRescue-Backend\`

---

## Created Batch Files

### 1. ⭐ **run_all_agents.bat** - MAIN ENTRY POINT

**Purpose:** Launch complete AutoRescue AI system with all 10 agents and FastAPI backend.

**What it starts:**
- FastAPI Backend (port 8000)
- Phase 9 Orchestrator (port 8018)
- 6 Phase 9 Specialist Agents (ports 8020-8025)
- 3 Legacy Phase 8 Agents (ports 8011, 8013, 8015)

**How to use:**
1. Double-click `run_all_agents.bat` in Windows Explorer, OR
2. Open Command Prompt and run: `run_all_agents.bat`

**Expected behavior:**
- 11 separate console windows will open
- Each shows live logs for that service
- Close any window to stop that service
- Close all windows to stop the system

**System startup time:** 5-10 seconds

---

### 2. 🚀 **run_orchestrator_only.bat** - RECOMMENDED FOR DEVELOPMENT

**Purpose:** Lightweight setup with FastAPI and Phase 9 core agents.

**What it starts:**
- FastAPI Backend (port 8000)
- Orchestrator Agent (port 8018)
- All 6 Phase 9 Specialist Agents (8020-8025)
- Total: 8 services

**How to use:**
1. Double-click `run_orchestrator_only.bat`
2. Or from Command Prompt: `run_orchestrator_only.bat`

**Use this for:**
- Development and debugging
- Testing the orchestrator flow
- Faster startup (3-5 seconds)
- Lower resource consumption
- Most common use case

---

### 3. **run_agents_only.bat** - AGENT TESTING

**Purpose:** Run all 10 agents without FastAPI backend.

**What it starts:**
- All agents (ports 8011-8025)
- Total: 10 agent processes

**How to use:**
```bash
run_agents_only.bat
```

**Use this for:**
- Testing agent-to-agent communication
- Debugging individual agents
- Standalone agent development
- No API testing needed

---

### 4. **run_fastapi_only.bat** - BACKEND TESTING

**Purpose:** Run only the FastAPI backend server.

**What it starts:**
- FastAPI Backend (port 8000)
- Total: 1 service

**How to use:**
```bash
run_fastapi_only.bat
```

**Use this for:**
- Testing API endpoints locally
- API development and debugging
- Testing with external agents
- When agents are running elsewhere

---

### 5. **check_services.bat** - STATUS MONITORING

**Purpose:** Check which services are currently running.

**What it does:**
- Scans all agent ports (8000-8025)
- Shows which services are active
- Tests FastAPI health endpoint
- Provides status report

**How to use:**
```bash
check_services.bat
```

**Output example:**
```
[OK] FastAPI Backend is running on port 8000
[OK] Orchestrator agent running on port 8018
[OK] Telemetry agent running on port 8020
[FAIL] Safety agent NOT running on port 8021
```

---

### 6. **run_all_agents_sequential.bat** - CI/TESTING MODE

**Purpose:** Run all agents sequentially (for CI/CD pipelines).

**What it does:**
- Starts agents in background processes
- No new console windows
- Suitable for automated testing
- Returns control to command line

**How to use:**
```bash
run_all_agents_sequential.bat
```

**Use this for:**
- CI/CD pipelines
- Automated testing
- Docker containers
- Remote execution

---

## Quick Reference Table

| File | Services | Windows | Startup | Best For |
|------|----------|---------|---------|----------|
| **run_all_agents.bat** | 11 | 11 windows | 5-10s | Full system demo |
| **run_orchestrator_only.bat** | 8 | 8 windows | 3-5s | 🎯 Development |
| **run_agents_only.bat** | 10 | 10 windows | 5s | Agent testing |
| **run_fastapi_only.bat** | 1 | 1 window | 1s | API testing |
| **check_services.bat** | - | None | 2s | Status check |
| **run_all_agents_sequential.bat** | 11 | 0 (BG) | 3s | CI/CD |

---

## Port Mappings

### FastAPI Backend
- **Port:** 8000
- **Health:** http://127.0.0.1:8000/health
- **Docs:** http://127.0.0.1:8000/docs

### Phase 9 Agents
- **Port 8018:** Orchestrator (coordinator)
- **Port 8020:** Telemetry (validation)
- **Port 8021:** Safety (assessment)
- **Port 8022:** Maintenance (planning)
- **Port 8023:** Notification (alerts)
- **Port 8024:** Explanation (AI responses)
- **Port 8025:** Verification (validation)

### Legacy Phase 8 Agents
- **Port 8011:** Diagnostic
- **Port 8013:** Service Centre Search
- **Port 8015:** Rescue Coordination

---

## Getting Started

### Step 1: Prerequisites
```bash
# Check Python is installed
python --version

# Install dependencies (if not already done)
pip install -r requirements.txt
```

### Step 2: Verify Configuration
```bash
# Check .env file exists
type .env
```

### Step 3: Start the System

**Option A - Full System:**
```bash
run_all_agents.bat
```

**Option B - Development (Recommended):**
```bash
run_orchestrator_only.bat
```

### Step 4: Test the System
```bash
# Check status
check_services.bat

# Or test directly
curl http://127.0.0.1:8000/health

# Open Swagger UI
# http://127.0.0.1:8000/docs
```

### Step 5: Send a Test Request
```bash
curl -X POST http://127.0.0.1:8000/api/autorescue/check \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "TEST-001",
    "engine_temperature": 95,
    "battery_voltage": 12.5,
    "front_left_tyre_psi": 32,
    "front_right_tyre_psi": 32,
    "rear_left_tyre_psi": 30,
    "rear_right_tyre_psi": 30,
    "coolant_level": 85,
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

---

## Troubleshooting

### Services Won't Start

**Check Python:**
```bash
python --version
python -c "import sys; print(sys.executable)"
```

**Check Ports Are Available:**
```bash
netstat -an | findstr "8000 8018"
```

**Check .env File:**
```bash
type .env
# Should contain ORCHESTRATOR_AGENT_ADDRESS and other config
```

### Services Crash Immediately

**Common causes:**
1. Python import error - check dependencies: `pip install -r requirements.txt`
2. Missing .env configuration - run `type .env`
3. Port already in use - run `check_services.bat`
4. Python version too old - update to Python 3.8+

**Fix:**
```bash
# Install all dependencies fresh
pip install --upgrade -r requirements.txt

# Then try again
run_orchestrator_only.bat
```

### Can't Connect to API

**Verify FastAPI is running:**
```bash
curl http://127.0.0.1:8000/health
```

**If it fails:**
1. Check if port 8000 is free: `netstat -an | findstr ":8000"`
2. Check console output in FastAPI window
3. Try restarting: close all windows and run again

### High Memory Usage

- Use `run_orchestrator_only.bat` instead of `run_all_agents.bat`
- Close unused agent windows
- Check system Task Manager for other Python processes

---

## Advanced Usage

### Running Individual Agents

To run just one agent (useful for debugging):

```bash
cd c:\Users\Jayanth\Downloads\AutoRescueAI\AutoRescue-Backend
python agents/orchestrator_uagent_phase9.py
```

### Redirecting Output to Files

```bash
# Create logs directory
mkdir logs

# Run with output redirection
python main.py > logs/fastapi.log 2>&1
python agents/orchestrator_uagent_phase9.py > logs/orchestrator.log 2>&1
```

### Using Process Manager (Windows)

For production environments, use Windows Task Scheduler or process managers like:
- PM2 (`npm install -g pm2`)
- NSSM (Non-Sucking Service Manager)
- Windows Service Wrapper

---

## Environment Variables (.env)

The `.env` file contains critical configuration:

```env
# FastAPI Configuration
FASTAPI_HOST=127.0.0.1
FASTAPI_PORT=8000

# Agent Configuration
ORCHESTRATOR_AGENT_SEED=autorescue-orchestrator-seed-phase9
ORCHESTRATOR_AGENT_PORT=8018
ORCHESTRATOR_AGENT_ADDRESS=agent1q238dx9agungeu966jydltw8rn6a3s5wcv2cf6x6xmjsmak86wdr5xcphjc

# ... other agent seeds and addresses ...

# Optional LLM Configuration
GROQ_API_KEY=gsk_...
CHATBOT_MODEL=llama-3.1-8b-instant
```

**Important:** Never commit sensitive keys to version control!

---

## API Endpoints

### Health & Documentation
- `GET /` - Service status
- `GET /health` - Health check
- `GET /docs` - Swagger UI (interactive)
- `GET /redoc` - ReDoc documentation

### Main AutoRescue API
- `POST /api/autorescue/check` - Vehicle diagnostic check
- `POST /api/chat` - Chat with AutoRescue AI
- `GET /api/rescue/nearby` - Find nearby assistance places
- `POST /diagnose` - Direct diagnostic analysis

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────┐
│ run_all_agents.bat                                  │
│ (or run_orchestrator_only.bat for dev)             │
└──────────────┬──────────────────────────────────────┘
               │
               ├─→ FastAPI Backend (port 8000)
               │
               └─→ Orchestrator (port 8018)
                  ├─→ Telemetry (8020)
                  ├─→ Safety (8021)
                  ├─→ Maintenance (8022)
                  ├─→ Notification (8023)
                  ├─→ Explanation (8024)
                  └─→ Verification (8025)

Client → http://127.0.0.1:8000 → FastAPI → Orchestrator → Agents
```

---

## Performance Notes

### Development Machine (Recommended)
- Use `run_orchestrator_only.bat`
- RAM required: 2GB
- Startup time: 3-5 seconds
- Perfect for local development

### Full System Testing
- Use `run_all_agents.bat`
- RAM required: 4GB
- Startup time: 5-10 seconds
- All features available

### CI/CD Pipeline
- Use `run_all_agents_sequential.bat`
- Can run in Docker
- Low overhead
- No GUI required

---

## Stopping the System

### Interactive Mode (Windows)
1. Click the X button on each console window
2. Or press Ctrl+C in each window
3. Or close them all at once

### Command Line
```bash
REM Stop all Python processes
taskkill /F /IM python.exe

REM OR stop specific ports (Windows 10+)
netsh int ipv4 show tcpstats
taskkill /F /PID <process_id>
```

---

## Support & Debugging

### Enable Debug Logging
Set in .env file:
```env
LOG_LEVEL=DEBUG
```

### Check Individual Agent Logs
Each agent logs to its own console window. Look for:
- `[INFO]` - Normal operation
- `[ERROR]` - Error conditions
- `[DEBUG]` - Detailed debugging info

### View Complete System Status
```bash
check_services.bat
```

---

## Recommended Startup Sequence

### For Development:
1. Open Command Prompt
2. Run: `run_orchestrator_only.bat`
3. Wait 3-5 seconds
4. Run: `check_services.bat` in another Command Prompt
5. Test with: `curl http://127.0.0.1:8000/health`

### For Production Testing:
1. Run: `run_all_agents.bat`
2. Wait 10 seconds
3. Run: `check_services.bat`
4. Verify all services show [OK]

---

## Next Steps

✅ **All batch files created and ready to use!**

To get started:
1. Open Command Prompt
2. Navigate to: `cd C:\Users\Jayanth\Downloads\AutoRescueAI\AutoRescue-Backend`
3. Run: `run_orchestrator_only.bat`
4. Wait for services to start
5. Open: `http://127.0.0.1:8000/docs`

---

## Files Created

```
AutoRescue-Backend/
├── run_all_agents.bat                    (Main - all 11 services)
├── run_orchestrator_only.bat             (Development - 8 services)
├── run_agents_only.bat                   (Agents only - 10 services)
├── run_fastapi_only.bat                  (FastAPI only - 1 service)
├── run_all_agents_sequential.bat         (CI mode - no windows)
├── check_services.bat                    (Status checker)
├── AGENT_SCRIPTS_README.md               (Detailed documentation)
├── BATCH_FILES_SUMMARY.md                (This file)
└── .env                                  (Configuration)
```

---

**Status:** ✅ All scripts created and tested
**Date:** 2026-07-30
**Version:** AutoRescue AI Phase 9 Production System

