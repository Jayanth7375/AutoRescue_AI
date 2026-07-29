#!/usr/bin/env python3
"""Print all agent addresses based on their seeds."""

from uagents import Agent

AGENTS = {
    # Original 4 agents (Phase 8)
    "Diagnostic": ("autorescue-diagnostic-agent", 8011),
    "Service": ("autorescue-service-agent", 8013),
    "Rescue": ("autorescue-rescue-agent", 8015),
    "Orchestrator-P8": ("autorescue-orchestrator-agent-development-seed", 8018),

    # New 6 agents (Phase 9)
    "Telemetry": ("autorescue-telemetry-agent-seed", 8020),
    "Safety": ("autorescue-safety-agent-seed", 8021),
    "Maintenance": ("autorescue-maintenance-agent-seed", 8022),
    "Notification": ("autorescue-notification-agent-seed", 8023),
    "Explanation": ("autorescue-explanation-agent-seed", 8024),
    "Verification": ("autorescue-verification-agent-seed", 8025),

    # Phase 9 Orchestrator (NEW - replaces P8)
    "Orchestrator-P9": ("autorescue-orchestrator-seed-phase9", 8018),
}

print("\n" + "=" * 70)
print("Agent Address Mapping (from seeds)")
print("=" * 70)

for agent_name, (seed, port) in AGENTS.items():
    agent = Agent(name=f"temp_{agent_name.lower()}", seed=seed, port=port)
    print(f"{agent_name:20} {agent.address}")

print("=" * 70 + "\n")
