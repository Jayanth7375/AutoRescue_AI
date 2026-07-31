"""Agent Health Monitor - Monitor all 20 agent statuses."""

import os
import logging
import asyncio
from uagents import Agent, Context
from dotenv import load_dotenv
from datetime import datetime

from agents.messages import (
    AgentHealthRequest,
    AgentHealthResponse,
)

load_dotenv()
logger = logging.getLogger(__name__)

AGENT_SEED = os.getenv("AGENT_HEALTH_MONITOR_SEED", "autorescue-agent-health-seed")
AGENT_PORT = int(os.getenv("AGENT_HEALTH_MONITOR_PORT", "8035"))

agent = Agent(
    name="autorescue_agent_health_monitor",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{AGENT_PORT}/submit"],
)

# All 20 agents to monitor
AGENTS_TO_MONITOR = {
    "Orchestrator": "8018",
    "Telemetry": "8020",
    "Diagnostic": "8011",
    "Safety": "8021",
    "Maintenance": "8022",
    "Service": "8013",
    "Rescue": "8015",
    "Notification": "8023",
    "Explanation": "8024",
    "Verification": "8025",
    "Vehicle Profile": "8026",
    "Battery Health": "8027",
    "Tyre Health": "8028",
    "Engine Health": "8029",
    "Breakdown Classification": "8030",
    "Passenger Safety": "8031",
    "Nearby Assistance": "8032",
    "Service Ranking": "8033",
    "Incident Memory": "8034",
    "Agent Health Monitor": "8035",
}


async def check_agent_health(port: str) -> str:
    """Check if agent is responding on port."""
    try:
        # Simplified check - in production would do actual health endpoint call
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", int(port)))
        sock.close()
        return "ONLINE" if result == 0 else "OFFLINE"
    except:
        return "OFFLINE"


@agent.on_query(model=AgentHealthRequest, replies={AgentHealthResponse})
async def handle_health_check(ctx: Context, sender: str, msg: AgentHealthRequest):
    """Check health of all agents."""
    try:
        logger.info(f"[AGENT-HEALTH] Health check request {msg.request_id}")

        agents_status = []
        online_count = 0

        for agent_name, port in AGENTS_TO_MONITOR.items():
            status = await check_agent_health(port)
            agents_status.append({
                "name": agent_name,
                "port": port,
                "status": status,
            })
            if status == "ONLINE":
                online_count += 1

        response = AgentHealthResponse(
            request_id=msg.request_id,
            total_agents=len(AGENTS_TO_MONITOR),
            online=online_count,
            agents=agents_status,
            timestamp=datetime.now().isoformat(),
        )

        logger.info(f"[AGENT-HEALTH] Health check: {online_count}/{len(AGENTS_TO_MONITOR)} online")
        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"[AGENT-HEALTH] Error: {str(e)}")
        response = AgentHealthResponse(
            request_id=msg.request_id,
            total_agents=len(AGENTS_TO_MONITOR),
            online=0,
            agents=[],
            timestamp=datetime.now().isoformat(),
        )
        await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info("=" * 60)
    logger.info("Agent Health Monitor started")
    logger.info(f"Monitoring {len(AGENTS_TO_MONITOR)} agents")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
