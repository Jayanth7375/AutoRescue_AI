"""In-memory workflow state management for orchestration."""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class WorkflowState:
    """Represents the state of a multi-agent orchestration workflow."""

    request_id: str
    vehicle_id: str
    original_sender: str

    # Input data
    telemetry: dict = field(default_factory=dict)
    latitude: float = 0.0
    longitude: float = 0.0

    # Workflow stages
    current_stage: str = "INITIAL"  # INITIAL, DIAGNOSTIC, SERVICE, RESCUE, COMPLETE

    # Responses from specialist agents
    diagnostic_response: Optional[dict] = None
    service_response: Optional[dict] = None
    rescue_response: Optional[dict] = None

    # Timing
    created_at: float = field(default_factory=time.time)
    diagnostic_received_at: Optional[float] = None
    service_received_at: Optional[float] = None
    rescue_received_at: Optional[float] = None

    # Workflow metadata
    diagnostic_timeout: float = 60.0  # seconds (uAgents startup can be slow)
    service_timeout: float = 120.0  # seconds (Overpass can be slow)
    rescue_timeout: float = 60.0  # seconds

    def is_expired(self) -> bool:
        """Check if workflow has exceeded its timeout for current stage."""
        now = time.time()

        if self.current_stage == "DIAGNOSTIC":
            return (now - self.created_at) > self.diagnostic_timeout

        elif self.current_stage == "SERVICE":
            if self.diagnostic_received_at is None:
                return False
            return (now - self.diagnostic_received_at) > self.service_timeout

        elif self.current_stage == "RESCUE":
            if self.service_received_at is None:
                return False
            return (now - self.service_received_at) > self.rescue_timeout

        return False

    def elapsed_seconds(self) -> float:
        """Get elapsed time since workflow creation."""
        return time.time() - self.created_at


class WorkflowStore:
    """In-memory store for orchestration workflow states."""

    def __init__(self):
        """Initialize the workflow store."""
        self.workflows: dict[str, WorkflowState] = {}
        logger.info("Workflow store initialized")

    def create_workflow(
        self,
        request_id: str,
        vehicle_id: str,
        original_sender: str,
        telemetry: dict,
        latitude: float,
        longitude: float,
    ) -> WorkflowState:
        """Create and store a new workflow."""
        workflow = WorkflowState(
            request_id=request_id,
            vehicle_id=vehicle_id,
            original_sender=original_sender,
            telemetry=telemetry,
            latitude=latitude,
            longitude=longitude,
        )

        self.workflows[request_id] = workflow
        logger.info(f"Created workflow {request_id} for vehicle {vehicle_id}")
        return workflow

    def get_workflow(self, request_id: str) -> Optional[WorkflowState]:
        """Retrieve a workflow by request ID (does not auto-delete on expiration)."""
        return self.workflows.get(request_id)

    def update_stage(self, request_id: str, stage: str) -> Optional[WorkflowState]:
        """Update workflow to new stage."""
        workflow = self.get_workflow(request_id)

        if not workflow:
            logger.error(f"Workflow {request_id} not found for stage update")
            return None

        workflow.current_stage = stage
        logger.info(f"Workflow {request_id} moved to stage {stage}")
        return workflow

    def save_diagnostic_response(self, request_id: str, response: dict) -> Optional[WorkflowState]:
        """Save diagnostic response to workflow."""
        workflow = self.get_workflow(request_id)

        if not workflow:
            return None

        workflow.diagnostic_response = response
        workflow.diagnostic_received_at = time.time()
        logger.info(f"Saved diagnostic response for {request_id}")
        return workflow

    def save_service_response(self, request_id: str, response: dict) -> Optional[WorkflowState]:
        """Save service response to workflow."""
        workflow = self.get_workflow(request_id)

        if not workflow:
            return None

        workflow.service_response = response
        workflow.service_received_at = time.time()
        logger.info(f"Saved service response for {request_id}")
        return workflow

    def save_rescue_response(self, request_id: str, response: dict) -> Optional[WorkflowState]:
        """Save rescue response to workflow."""
        workflow = self.get_workflow(request_id)

        if not workflow:
            return None

        workflow.rescue_response = response
        workflow.rescue_received_at = time.time()
        workflow.current_stage = "COMPLETE"
        logger.info(f"Saved rescue response for {request_id}")
        return workflow

    def delete_workflow(self, request_id: str) -> bool:
        """Remove completed workflow from memory."""
        if request_id in self.workflows:
            del self.workflows[request_id]
            logger.info(f"Deleted workflow {request_id}")
            return True

        return False

    def cleanup_expired_workflows(self) -> int:
        """Remove all expired workflows. Call periodically."""
        expired = [
            request_id
            for request_id, workflow in self.workflows.items()
            if workflow.is_expired()
        ]

        for request_id in expired:
            self.delete_workflow(request_id)

        if expired:
            logger.warning(f"Cleaned up {len(expired)} expired workflows")

        return len(expired)

    def get_stats(self) -> dict:
        """Get workflow store statistics."""
        return {
            "total_workflows": len(self.workflows),
            "stages": {},
        }


# Global workflow store instance
_workflow_store: Optional[WorkflowStore] = None


def get_workflow_store() -> WorkflowStore:
    """Get or create the global workflow store."""
    global _workflow_store

    if _workflow_store is None:
        _workflow_store = WorkflowStore()

    return _workflow_store
