# AutoRescue AI Backend — Complete Architecture

## System Overview

AutoRescue AI is a multi-agent vehicle diagnostic and roadside assistance system. The backend uses a distributed architecture with specialized agents coordinated by an Orchestrator, exposed to the Android app via HTTP API.

```
┌─────────────────────────────────────────────────────────────┐
│                     Android Mobile App                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ HTTP REST
                             ↓
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Gateway (Port 8000)                    │
│          POST /api/autorescue/check endpoint               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ uAgents Query Protocol
                         ↓
┌──────────────────────────────────────────────────────────────┐
│            Orchestrator uAgent (Port 8018)                   │
│     - Routes requests to specialist agents                   │
│     - Coordinates responses                                  │
│     - Manages workflow state                                 │
│     - Handles timeouts and errors                           │
└─┬──────────────┬──────────────┬──────────────┬───────────────┘
  │              │              │              │
  │ Diagnostic   │ Service      │ Rescue       │ Error
  │ (if needed)  │ (if needed)  │ (if needed)  │ Handling
  ↓              ↓              ↓              ↑
┌─────────┐   ┌────────┐   ┌────────┐
│Diagnose │   │Service │   │Rescue  │
│Agent    │   │Agent   │   │Agent   │
│(8011)   │   │(8013)  │   │(8015)  │
└────┬────┘   └───┬────┘   └───┬────┘
     │            │            │
     │ Rules      │ Overpass   │ Rules
     │ Based      │ OpenStreetMap
     │            │ Distance + Ranking
     └────────┬───┴────────────┘
              │
         Deterministic
          Responses
```

---

## Architecture Layers

### 1. Presentation Layer (Frontend)
- **Android Mobile App**
  - Vehicle telemetry collection (sensors, OBD-II)
  - GPS coordinates
  - User interface for diagnostic results
  - Navigation to service centres
  - Roadside assistance requests

### 2. API Gateway Layer
- **FastAPI (main.py, Port 8000)**
  - Single HTTP endpoint: `POST /api/autorescue/check`
  - Input validation (Pydantic models)
  - Inter-agent communication via uAgents query protocol
  - Response conversion to HTTP JSON
  - Error handling with proper HTTP status codes
  - Request correlation with UUIDs

### 3. Multi-Agent Orchestration Layer
- **Orchestrator uAgent (Port 8018)**
  - Central decision maker
  - Routes requests based on diagnosis severity
  - Manages workflow state (in-memory with timeout cleanup)
  - Coordinates specialist agents
  - Aggregates results into unified response

### 4. Specialist Agent Layer

#### 4a. Diagnostic Agent (Port 8011)
- **Input:** Vehicle telemetry (engine temp, battery, tyres, coolant)
- **Processing:** Deterministic rule engine
- **Output:** Severity level + safe-to-drive flag
- **Rules:**
  - Engine: ≤105°C NORMAL, 106-115 WARNING, >115 CRITICAL
  - Battery: ≥12.4V NORMAL, 12.0-12.39V WARNING, <12.0V CRITICAL
  - Tyres: ≥30 PSI NORMAL, 25-29 PSI WARNING, <25 PSI CRITICAL
  - Coolant: ≥50% NORMAL, 30-49% WARNING, <30% CRITICAL

#### 4b. Service Agent (Port 8013)
- **Input:** Vehicle location + issue component + severity
- **Data Source:** OpenStreetMap + Overpass API
- **Processing:** 
  - Search 10km radius for automotive services
  - Match issue type to business tags (tyre shops, cooling specialists, etc.)
  - Rank by multi-factor algorithm
- **Ranking Algorithm:**
  - Distance: 40% weight (closer is better)
  - Issue Relevance: 30% weight (specialization match)
  - Open Status: 20% weight (currently accepting customers)
  - Data Completeness: 10% weight (complete profile)
- **Output:** Top 5 ranked service centres with details

#### 4c. Rescue Agent (Port 8015)
- **Input:** Diagnosis + location (if unsafe)
- **Processing:** Deterministic assistance rules
- **Assistance Types:**
  - `NONE` — No assistance needed
  - `TOW` — Vehicle must be towed
  - `TYRE_ASSISTANCE` — Spare/repair needed
  - `BATTERY_JUMP_START` — Battery aid
  - `COOLING_SYSTEM_ASSISTANCE` — Cooling service
  - `FUEL_ASSISTANCE` — Fuel delivery
  - `ACCIDENT_EMERGENCY` — Emergency services
- **Priority Levels:**
  - `LOW` — 25 min ETA
  - `MEDIUM` — 20 min ETA
  - `HIGH` — 15 min ETA
  - `CRITICAL` — 10 min ETA
- **Output:** Assistance type, priority, dispatch ETA

### 5. Data & Integration Layer
- **PostgreSQL via Supabase** — Future for:
  - Vehicle profiles
  - Service history
  - User preferences
  - Aggregate analytics
- **OpenStreetMap / Overpass API**
  - Real-time service centre database
  - No API key required
  - Global coverage
  - Open source
- **GPS Coordinates**
  - Haversine distance calculation
  - Service centre ranking based on distance

---

## Communication Protocols

### Phase 1-2: API Validation
```
FastAPI Endpoint
    ↓
Pydantic Validation (AutoRescueApiRequest)
    ↓
Type Safety Enforcement
```

### Phase 2+: Inter-Agent Communication (uAgents)
```
Agent A sends Message
    ↓
Serialization (JSON)
    ↓
Network Transport (HTTP/TCP)
    ↓
Agent B receives Message
    ↓
Deserialization + Type Check
    ↓
Handler Processes Message
    ↓
Response Message Created
    ↓
Response Sent Back to Sender
```

### Gateway ↔ Orchestrator (Query Protocol)
```python
# Gateway (main.py)
response = await query(
    destination=ORCHESTRATOR_ADDRESS,
    message=AutoRescueRequestMessage(...),
    timeout=120  # 2 minutes max
)

# Response is decoded AutoRescueResponseMessage or Error
```

---

## Data Flow Examples

### Example 1: Healthy Vehicle

```
Android App → FastAPI
  ├─ vehicle_id: TN37AB1234
  ├─ engine_temp: 95°C
  ├─ battery: 12.7V
  ├─ tyres: 32, 32, 31, 31 PSI
  ├─ coolant: 75%
  └─ coords: 19.076, 72.8777

FastAPI → Orchestrator (AutoRescueRequestMessage)
  └─ UUID: 550e8400-...

Orchestrator → Diagnostic Agent
  └─ Check telemetry

Diagnostic Agent → Orchestrator
  ├─ Severity: NORMAL
  └─ safe_to_drive: true

Orchestrator → Gateway
  └─ status: HEALTHY

Gateway → Android App (HTTP 200)
  ├─ request_id: 550e8400-...
  ├─ status: HEALTHY
  ├─ diagnosis: { severity: NORMAL, safe_to_drive: true, ... }
  ├─ service_centres: []
  ├─ navigation_allowed: true
  └─ rescue: null
```

### Example 2: Tyre Warning (Service Recommended)

```
Android App → FastAPI
  ├─ front_left_tyre: 28 PSI  [WARNING]
  └─ other params: NORMAL

FastAPI → Orchestrator

Orchestrator → Diagnostic Agent
  └─ Check: Front-left PSI 28

Diagnostic Agent → Orchestrator
  ├─ Severity: WARNING
  ├─ Issue: Tyre pressure low
  └─ safe_to_drive: true

Orchestrator → Service Agent
  ├─ coords: 19.076, 72.8777
  ├─ issue: TYRE
  └─ severity: WARNING

Service Agent → Overpass API
  └─ Query: Tyre shops within 10km of coordinates

Overpass API → Service Agent
  └─ Returns ~27 results with names, locations, ratings, tags

Service Agent → Ranking Algorithm
  ├─ Distance: 40%
  ├─ Tyre shop relevance: 30%
  ├─ Is open: 20%
  └─ Data quality: 10%

Service Agent → Orchestrator
  └─ Top 5 centres sorted by priority_score

Orchestrator → Gateway
  ├─ status: SERVICE_RECOMMENDED
  ├─ diagnosis: { severity: WARNING, ... }
  └─ service_centres: [5 ranked locations]

Gateway → Android App (HTTP 200)
  ├─ Show diagnostic result
  └─ Display service centre map with navigation
```

### Example 3: Engine Overheating (Assistance Required)

```
Android App → FastAPI
  ├─ engine_temp: 122°C  [CRITICAL]
  └─ other params: OK

FastAPI → Orchestrator

Orchestrator → Diagnostic Agent

Diagnostic Agent → Orchestrator
  ├─ Severity: CRITICAL
  ├─ Issue: Engine overheating
  └─ safe_to_drive: false

Orchestrator → Service Agent
  ├─ severity: CRITICAL
  └─ issue: ENGINE_COOLING

Service Agent → Orchestrator
  └─ Top 5 cooling specialists

Orchestrator → Rescue Agent
  ├─ Severity: CRITICAL
  ├─ Issue: Engine overheating
  └─ safe_to_drive: false

Rescue Agent → Orchestrator
  ├─ Assistance type: TOW
  ├─ Priority: CRITICAL
  ├─ Can drive: false
  ├─ Tow required: true
  └─ ETA: 10 minutes

Orchestrator → Gateway
  ├─ status: ASSISTANCE_REQUIRED
  ├─ diagnosis: CRITICAL
  ├─ service_centres: [top cooling specialists]
  └─ rescue: { type: TOW, priority: CRITICAL, ... }

Gateway → Android App (HTTP 200)
  ├─ Show CRITICAL alert
  ├─ Disable navigation ("Vehicle cannot be driven safely")
  ├─ Display tow truck dispatch (ETA 10 min)
  ├─ Show nearest cooling centre as destination
  └─ Show contact info for dispatch
```

---

## Status Decision Tree

### Orchestrator Decision Logic

```
Request received
    │
    ├─→ Send to Diagnostic Agent
    │
    ├─→ Is severity NORMAL? → Return HEALTHY
    │
    ├─→ Send to Service Agent
    │
    ├─→ Is safe_to_drive = true? → Return SERVICE_RECOMMENDED
    │
    ├─→ Send to Rescue Agent
    │
    └─→ Return ASSISTANCE_REQUIRED with rescue details
```

### Status Values

| Status | Condition | Actions |
|--------|-----------|---------|
| `HEALTHY` | All systems NORMAL | No service or rescue needed |
| `SERVICE_RECOMMENDED` | Warning/Non-critical issues | Show service centres, navigation allowed |
| `ASSISTANCE_REQUIRED` | Critical issue + unsafe to drive | Show rescue dispatch + centres, disable navigation |

---

## Error Handling

### Gateway Error Responses

| HTTP Code | Cause | Response |
|-----------|-------|----------|
| 200 | Success | AutoRescueApiResponse |
| 422 | Invalid input | Pydantic validation error |
| 503 | Orchestrator unreachable | Service unavailable |
| 504 | Orchestrator timeout | Timeout after 120s |
| 500 | Orchestrator error | Orchestrator error message |

### Orchestrator Error Handling

| Scenario | Action |
|----------|--------|
| Diagnostic Agent timeout | Return ASSISTANCE_REQUIRED (safe fallback) |
| Service Agent timeout | Return empty service_centres |
| Rescue Agent timeout | Return null rescue |
| Invalid diagnosis | Return error message with request_id |

---

## Configuration

### Environment Variables (.env)

```env
# Diagnostic Agent
DIAGNOSTIC_AGENT_SEED=...
DIAGNOSTIC_AGENT_ADDRESS=agent1qf...
DIAGNOSTIC_AGENT_PORT=8011

# Service Agent
SERVICE_AGENT_SEED=...
SERVICE_AGENT_ADDRESS=agent1qg...
SERVICE_AGENT_PORT=8013

# Rescue Agent
RESCUE_AGENT_SEED=...
RESCUE_AGENT_ADDRESS=agent1qv...
RESCUE_AGENT_PORT=8015

# Orchestrator
ORCHESTRATOR_AGENT_SEED=...
ORCHESTRATOR_AGENT_ADDRESS=agent1qw...
ORCHESTRATOR_AGENT_PORT=8018

# External APIs
OVERPASS_API_URL=https://overpass.openstreetmap.fr/api/interpreter

# Test Coordinates
TEST_SERVICE_LATITUDE=19.0760
TEST_SERVICE_LONGITUDE=72.8777
```

---

## Scalability & Performance

### Current Design (MVP)
- **Single Orchestrator** handles sequential requests
- **In-memory workflow state** with automatic cleanup
- **No database** for orchestration (only future logging)
- **No caching** (fresh data each request)
- **No message queue** (synchronous query protocol)

### Scaling Path
1. **Add Redis** for workflow state (if Orchestrator instances multiply)
2. **Add message queue** (RabbitMQ/Kafka) for async workflows
3. **Add PostgreSQL** for analytics, user history, service performance
4. **Add monitoring** (Prometheus, Grafana) for agent metrics
5. **Deploy on Kubernetes** for high availability

### Performance Targets
- Diagnostic: <50ms
- Service search: <2s (Overpass API limit)
- Rescue decision: <100ms
- Total request: <5s (120s gateway timeout is conservative)

---

## Security Considerations

### Current Implementation
- ✓ No authentication (internal service, protected by network)
- ✓ Input validation via Pydantic
- ✓ No sensitive data in logs
- ✓ No SQL injection (no database in MVP)
- ✓ No API key exposure (Overpass is public, no key needed)

### Production Hardening
- [ ] Add API key authentication (for Android app)
- [ ] Add rate limiting (prevent abuse)
- [ ] Add HTTPS (TLS encryption)
- [ ] Add request signing (prevent tampering)
- [ ] Add audit logging (compliance)
- [ ] Add secrets management (e.g., AWS Secrets Manager)

---

## Testing Strategy

### Phase Testing
| Phase | Test File | Type |
|-------|-----------|------|
| 1 | test_api.py | FastAPI endpoint validation |
| 2 | test_phase2_simple.py | Diagnostic uAgent communication |
| 3 | test_service_agent.py | Service discovery + ranking |
| 4 | test_rescue_agent.py | Rescue decision rules |
| 5 | test_orchestrator.py | Multi-agent workflow |
| 6 | test_gateway.py | HTTP gateway integration |

### Test Scenarios
1. **Healthy** — All systems normal
2. **Warning** — Non-critical issue (service recommended)
3. **Critical** — Unsafe to drive (assistance required)
4. **Multiple Issues** — Highest severity reported
5. **Edge Cases** — Boundary values (e.g., exactly 30 PSI tyre)

---

## File Structure

```
AutoRescue-Backend/
├── main.py                          # FastAPI gateway
├── run_diagnostic_agent.py          # Diagnostic startup
├── run_service_agent.py             # Service startup
├── run_rescue_agent.py              # Rescue startup
├── run_orchestrator_agent.py        # Orchestrator startup
│
├── models/
│   ├── __init__.py
│   ├── telemetry.py                 # Vehicle telemetry
│   ├── diagnosis.py                 # Diagnostic results
│   └── autorescue_api.py            # HTTP API models
│
├── agents/
│   ├── __init__.py
│   ├── messages.py                  # All message types
│   ├── diagnostic_agent.py          # Diagnostic wrapper
│   ├── diagnostic_uagent.py         # Diagnostic uAgent
│   ├── service_uagent.py            # Service uAgent
│   ├── rescue_uagent.py             # Rescue uAgent
│   └── orchestrator_uagent.py       # Orchestrator uAgent
│
├── orchestration/
│   ├── __init__.py
│   └── workflow_store.py            # Workflow state management
│
├── tools/
│   ├── diagnostic_rules.py          # Diagnostic logic
│   ├── distance.py                  # Haversine calculation
│   ├── places_tool.py               # Overpass API integration
│   ├── rescue_rules.py              # Rescue logic
│   └── service_ranker.py            # Service ranking
│
├── tests/
│   ├── test_api.py                  # Phase 1 tests
│   ├── test_phase2_simple.py        # Phase 2 tests
│   ├── test_service_agent.py        # Phase 3 tests
│   ├── test_rescue_agent.py         # Phase 4 tests
│   ├── test_orchestrator.py         # Phase 5 tests
│   └── test_gateway.py              # Phase 6 tests
│
├── .env                             # Environment configuration
├── .env.example                     # Example configuration
├── requirements.txt                 # Python dependencies
│
├── ARCHITECTURE.md                  # This file
├── PHASE_6_COMPLETE.md             # Phase 6 documentation
└── README.md                        # Quick start guide
```

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Gateway | FastAPI | HTTP REST endpoint |
| Multi-Agent | uAgents Framework | Distributed agent orchestration |
| Validation | Pydantic | Type-safe request/response models |
| Async | asyncio | Non-blocking I/O |
| Geolocation | Haversine Formula | Distance calculation |
| Service Discovery | OpenStreetMap Overpass API | Free, open service database |
| Environment | python-dotenv | Configuration management |
| Testing | pytest, httpx | Automated testing |
| Server | Uvicorn | ASGI application server |
| Language | Python 3.9+ | Implementation language |

---

## Design Principles

1. **Separation of Concerns**
   - Each agent has single responsibility (diagnostic, service search, rescue)
   - Gateway is only HTTP translation layer
   - Orchestrator is only coordinator

2. **Stateless Architecture**
   - No persistent database in MVP
   - Workflow state is in-memory with timeout cleanup
   - Each request is independently processed

3. **Deterministic Logic**
   - No LLMs or probabilistic inference
   - All decisions based on explicit rules
   - Repeatable, debuggable results

4. **Fault Tolerance**
   - Orchestrator handles agent timeouts gracefully
   - Gateway has fallback responses
   - Proper error propagation with context

5. **Simplicity**
   - No premature optimization
   - Synchronous query protocol (simple request-response)
   - No message queues or event streams (yet)

---

## Integration with Android App

### Setup
1. Update app to call `http://<server>:8000/api/autorescue/check`
2. Send telemetry as JSON (AutoRescueApiRequest)
3. Parse response (AutoRescueApiResponse)

### Response Handling
```kotlin
when (response.status) {
    "HEALTHY" -> {
        // Show "All systems normal" message
        // Allow navigation
    }
    "SERVICE_RECOMMENDED" -> {
        // Show service centres
        // Display distance, ratings, navigation
        // Allow navigation
    }
    "ASSISTANCE_REQUIRED" -> {
        // Show rescue dispatch details
        // Display ETA, contact info
        // Disable navigation (safety)
        // Show nearest service centre as destination
    }
}
```

---

## Future Enhancements

### Phase 7: Persistence
- Add PostgreSQL for analytics
- Store vehicle history
- Track service patterns
- Generate recommendations

### Phase 8: AI Features
- ML-based predictive maintenance
- Anomaly detection in vehicle metrics
- Personalized recommendations

### Phase 9: Ecosystem
- Integrate with actual dispatch services
- Payment processing
- Insurance integration
- Real-time tracking

### Phase 10: Enterprise
- Multi-tenant support
- Fleet management
- Advanced analytics
- Custom rules engine

---

## Summary

AutoRescue AI Backend is a **scalable, distributed, rule-based vehicle diagnostic system** that:
- ✓ Analyzes vehicle health in real-time
- ✓ Finds nearby service centres via OSM
- ✓ Determines roadside assistance needs
- ✓ Provides unified response to mobile app
- ✓ Uses deterministic logic (no LLM, no randomness)
- ✓ Handles concurrent requests with correlation IDs
- ✓ Scales from MVP to enterprise

**All 6 phases complete. Ready for production integration.**
