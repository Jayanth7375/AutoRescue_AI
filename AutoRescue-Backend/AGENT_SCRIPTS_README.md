# AutoRescue AI - Agent Orchestration Scripts

This directory contains several `.bat` scripts to easily launch and manage all AutoRescue AI services and agents.

## Quick Start

### For Complete System Setup
Run all agents and FastAPI backend with a single command:

```bash
run_all_agents.bat
```

This starts:
- FastAPI backend (port 8000)
- Phase 9 Orchestrator (port 8018)
- 6 specialist agents (ports 8020-8025)
- 3 legacy Phase 8 agents (ports 8011, 8013, 8015)

### For Development/Testing

**Orchestrator-only mode** (recommended for development):
```bash
run_orchestrator_only.bat
```

**Agents only** (no FastAPI):
```bash
run_agents_only.bat
```

**FastAPI only** (no agents):
```bash
run_fastapi_only.bat
```

**Check service status**:
```bash
check_services.bat
```

---

## Available Scripts

### 1. **run_all_agents.bat** ⭐ Main Entry Point

Launches the complete AutoRescue AI system with all 10 agents and FastAPI backend.

**What it starts:**
- FastAPI Backend (port 8000)
- Orchestrator Agent (port 8018)
- Telemetry Agent (port 8020)
- Safety Agent (port 8021)
- Maintenance Agent (port 8022)
- Notification Agent (port 8023)
- Explanation Agent (port 8024)
- Verification Agent (port 8025)
- Diagnostic Agent (port 8011) - Legacy
- Service Agent (port 8013) - Legacy
- Rescue Agent (port 8015) - Legacy

**Usage:**
```bash
run_all_agents.bat
```

Each service runs in its own console window with live logs.

**When to use:**
- Production deployments
- Full system testing
- Complete feature demonstrations

---

### 2. **run_orchestrator_only.bat** Recommended for Development

Lightweight setup with FastAPI and Phase 9 orchestrator system only.

**What it starts:**
- FastAPI Backend (port 8000)
- Orchestrator Agent (port 8018)
- All 6 Phase 9 specialist agents (8020-8025)

**Usage:**
```bash
run_orchestrator_only.bat
```

**When to use:**
- Development and debugging
- Testing the orchestrator flow
- Faster startup time
- Reduced resource consumption

---

### 3. **run_agents_only.bat** Agent Testing

Runs all 10 agents without the FastAPI backend.

**What it starts:**
- All agents (ports 8011-8025)

**Usage:**
```bash
run_agents_only.bat
```

**When to use:**
- Testing agent-to-agent communication
- Debugging individual agents
- Standalone agent development

---

### 4. **run_fastapi_only.bat** Backend Testing

Runs only the FastAPI backend server.

**What it starts:**
- FastAPI Backend (port 8000)

**Usage:**
```bash
run_fastapi_only.bat
```

**When to use:**
- Testing API endpoints locally
- Testing with external agents
- Development without full orchestration

---

### 5. **check_services.bat** Status Monitoring

Checks which services are currently running and their status.

**Usage:**
```bash
check_services.bat
```

**Output:**
- Shows status of all ports
- Indicates which agents are running
- Checks FastAPI health endpoint

**When to use:**
- Verifying all services started successfully
- Troubleshooting connection issues
- Before running integration tests

---

## Configuration

### Prerequisites

1. **Python 3.8+** installed and in PATH
2. **.env file** with required configuration (see `.env.example`)
3. **Dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables

The `.env` file must contain:

```env
# FastAPI Configuration
FASTAPI_HOST=127.0.0.1
FASTAPI_PORT=8000

# Orchestrator
ORCHESTRATOR_AGENT_SEED=autorescue-orchestrator-seed-phase9
ORCHESTRATOR_AGENT_PORT=8018
ORCHESTRATOR_AGENT_ADDRESS=agent1q...

# Phase 9 Agents
TELEMETRY_AGENT_SEED=autorescue-telemetry-agent-seed
TELEMETRY_AGENT_PORT=8020
TELEMETRY_AGENT_ADDRESS=agent1q...

# ... (other agents)

# Optional: LLM Configuration
GROQ_API_KEY=gsk_...
CHATBOT_MODEL=llama-3.1-8b-instant
```

See `.env.example` for complete template.

---

## API Endpoints

### FastAPI Backend (http://127.0.0.1:8000)

**Health Check:**
```bash
curl http://127.0.0.1:8000/health
```

**API Documentation:**
```
http://127.0.0.1:8000/docs         # Swagger UI
http://127.0.0.1:8000/redoc        # ReDoc
```

**Main Endpoints:**
- `POST /api/autorescue/check` - Vehicle diagnostic check
- `POST /api/chat` - Chat with AutoRescue AI
- `GET /api/rescue/nearby` - Find nearby assistance places
- `POST /diagnose` - Direct diagnostic analysis

### Agent Communication

Agents communicate via the uAgents framework on their respective ports:

| Agent | Port | Purpose |
|-------|------|---------|
| Orchestrator | 8018 | Coordinates all other agents |
| Telemetry | 8020 | Validates vehicle telemetry |
| Safety | 8021 | Assesses safety conditions |
| Maintenance | 8022 | Plans maintenance actions |
| Notification | 8023 | Generates notifications |
| Explanation | 8024 | Provides AI explanations |
| Verification | 8025 | Verifies results |
| Diagnostic | 8011 | Diagnostic analysis (legacy) |
| Service | 8013 | Service centre search (legacy) |
| Rescue | 8015 | Rescue coordination (legacy) |

---

## Workflow

### Phase 9 Processing Flow

```
Client Request
    ↓
FastAPI Gateway (port 8000)
    ↓
Orchestrator Agent (port 8018)
    ├→ Telemetry Validation (8020)
    ├→ Safety Assessment (8021)
    ├→ Maintenance Planning (8022)
    ├→ Notifications (8023)
    ├→ Explanations (8024)
    └→ Verification (8025)
    ↓
Response to Client
```

---

## Troubleshooting

### Services Won't Start

1. **Check Python Installation:**
   ```bash
   python --version
   ```

2. **Verify .env File:**
   ```bash
   type .env
   ```

3. **Check Port Availability:**
   ```bash
   netstat -an | findstr "8000 8011 8013 8015 8018 8020 8021 8022 8023 8024 8025"
   ```

### Services Fail to Connect

1. **Check if FastAPI is running:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```

2. **Verify agent addresses in .env match running agents**

3. **Check firewall settings** - Ensure local ports are not blocked

### Import Errors

Install missing dependencies:
```bash
pip install -r requirements.txt
```

### High Resource Usage

- Use `run_orchestrator_only.bat` for lighter setup
- Close unused console windows
- Monitor system resources while agents are running

---

## Testing the System

### 1. Verify All Services Are Running

```bash
check_services.bat
```

### 2. Test FastAPI Health

```bash
curl http://127.0.0.1:8000/health
```

### 3. Send a Test Request

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

### 4. Use Swagger UI

Open: http://127.0.0.1:8000/docs

- Browse available endpoints
- Test requests interactively
- View response schemas

---

## Log Files

Each service logs to its own console window. To save logs:

1. **Right-click** in console window
2. Select **Edit → Select All**
3. Copy logs to a file

Or redirect output when starting manually:
```bash
python agents/orchestrator_uagent_phase9.py > logs/orchestrator.log 2>&1
```

---

## Performance Tips

### For Development

```bash
run_orchestrator_only.bat
```
- Faster startup
- Lower memory usage
- Sufficient for most development

### For Production

```bash
run_all_agents.bat
```
- Complete feature set
- Full redundancy
- All agents available

### For CI/CD

```bash
run_fastapi_only.bat
```
- Test API without agents
- Faster pipeline
- Lighter container images

---

## Advanced: Manual Agent Startup

If you need to start a specific agent:

```bash
REM Navigate to backend directory
cd AutoRescue-Backend

REM Start a specific agent
python agents/orchestrator_uagent_phase9.py
python agents/telemetry_uagent.py
python agents/safety_uagent.py

REM In another terminal, start FastAPI
python main.py
```

---

## System Requirements

- **Windows 7+** or Windows Server
- **Python 3.8+**
- **RAM:** 2GB minimum, 4GB+ recommended
- **Disk Space:** 500MB minimum
- **Ports:** 8000-8025 must be available
- **Network:** Local network connectivity (127.0.0.1)

---

## Support

For issues or questions:

1. Check the logs in console windows
2. Run `check_services.bat` to verify status
3. Review `.env` configuration
4. Check Python and dependency versions

---

## Version Info

- **Phase:** Phase 9 Production Orchestration
- **Agents:** 10 (6 Phase 9 + 3 Legacy + 1 Orchestrator)
- **API:** FastAPI with Swagger/ReDoc
- **Framework:** uAgents for agent communication
- **Database:** PostgreSQL (configured in main app)

---

## Next Steps

1. **Start the system:**
   ```bash
   run_all_agents.bat
   ```

2. **Wait 3-5 seconds** for initialization

3. **Test the API:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```

4. **Open API docs:**
   ```
   http://127.0.0.1:8000/docs
   ```

5. **Send a test request** using the Swagger UI or curl

---

Last Updated: 2026-07-30
AutoRescue AI Development Team
