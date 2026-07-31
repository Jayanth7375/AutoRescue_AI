"""Incident Memory Agent - Store and retrieve incidents."""

import os
import logging
import sqlite3
from datetime import datetime
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    IncidentMemoryRequest,
    IncidentMemoryResponse,
)

load_dotenv()
logger = logging.getLogger(__name__)

AGENT_SEED = os.getenv("INCIDENT_MEMORY_AGENT_SEED", "autorescue-incident-memory-seed")
AGENT_PORT = int(os.getenv("INCIDENT_MEMORY_AGENT_PORT", "8034"))

agent = Agent(
    name="autorescue_incident_memory_agent",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{AGENT_PORT}/submit"],
)

# Initialize SQLite database
DB_PATH = "incidents.db"


def init_db():
    """Initialize incidents database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            request_id TEXT,
            vehicle_id TEXT,
            timestamp TEXT,
            issue TEXT,
            severity TEXT,
            affected_component TEXT,
            safe_to_drive BOOLEAN,
            rescue_required BOOLEAN,
            maintenance_urgency TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


@agent.on_query(model=IncidentMemoryRequest, replies={IncidentMemoryResponse})
async def handle_memory(ctx: Context, sender: str, msg: IncidentMemoryRequest):
    """Handle incident memory operations."""
    try:
        logger.info(f"[INCIDENT-MEMORY] Request {msg.request_id} operation={msg.operation}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        incidents = []
        repeated_faults = []

        if msg.operation == "STORE_INCIDENT":
            if msg.incident_data:
                cursor.execute("""
                    INSERT INTO incidents (
                        incident_id, request_id, vehicle_id, timestamp, issue,
                        severity, affected_component, safe_to_drive,
                        rescue_required, maintenance_urgency
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    msg.request_id,
                    msg.request_id,
                    msg.vehicle_id,
                    datetime.now().isoformat(),
                    msg.incident_data.get("issue"),
                    msg.incident_data.get("severity"),
                    msg.incident_data.get("affected_component"),
                    msg.incident_data.get("safe_to_drive", True),
                    msg.incident_data.get("rescue_required", False),
                    msg.incident_data.get("maintenance_urgency"),
                ))
                conn.commit()

        elif msg.operation == "GET_RECENT":
            cursor.execute("""
                SELECT * FROM incidents WHERE vehicle_id = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (msg.vehicle_id, msg.limit))
            incidents = [dict(zip([d[0] for d in cursor.description], row))
                        for row in cursor.fetchall()]

        elif msg.operation == "GET_REPEATED":
            cursor.execute("""
                SELECT affected_component, COUNT(*) as count
                FROM incidents WHERE vehicle_id = ?
                GROUP BY affected_component HAVING count > 1
                ORDER BY count DESC
            """, (msg.vehicle_id,))
            repeated_faults = [{"component": row[0], "count": row[1]}
                              for row in cursor.fetchall()]

        conn.close()

        response = IncidentMemoryResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            operation=msg.operation,
            incidents=incidents,
            repeated_faults=repeated_faults,
            success=True,
        )

        logger.info(f"[INCIDENT-MEMORY] Response: {msg.operation} success")
        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"[INCIDENT-MEMORY] Error: {str(e)}")
        response = IncidentMemoryResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            operation=msg.operation,
            success=False,
        )
        await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info("=" * 60)
    logger.info("Incident Memory Agent started")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info(f"Database: {DB_PATH}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
