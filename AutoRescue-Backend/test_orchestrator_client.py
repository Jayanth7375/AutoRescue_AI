"""Test client using gateway agent pattern for orchestrator communication."""

import asyncio
import os
from dotenv import load_dotenv
from uagents import Agent, Context

from agents.messages import (
    AutoRescueRequestMessage,
    AutoRescueResponseMessage,
    AutoRescueErrorMessage,
)

load_dotenv()

ORCHESTRATOR_AGENT_ADDRESS = os.getenv("ORCHESTRATOR_AGENT_ADDRESS")

# Create a simple client agent
client_agent = Agent(
    name="test_client_agent",
    seed="test-client-seed-12345",
    port=8099,
    endpoint=["http://127.0.0.1:8099/submit"],
)

# Store response for testing
test_response = None


@client_agent.on_message(model=AutoRescueResponseMessage)
async def handle_orchestrator_response(ctx: Context, sender: str, msg: AutoRescueResponseMessage):
    """Handle response from orchestrator."""
    global test_response
    test_response = msg
    print(f"\n✓ Received AutoRescueResponseMessage from Orchestrator")
    print(f"  Status: {msg.status}")
    print(f"  Request ID: {msg.request_id}")


@client_agent.on_message(model=AutoRescueErrorMessage)
async def handle_orchestrator_error(ctx: Context, sender: str, msg: AutoRescueErrorMessage):
    """Handle error from orchestrator."""
    global test_response
    test_response = msg
    print(f"\n✗ Received AutoRescueErrorMessage from Orchestrator")
    print(f"  Error: {msg.error}")


async def test_orchestrator():
    """Test orchestrator via send_and_receive within agent context."""
    global test_response

    # Create test message
    request = AutoRescueRequestMessage(
        request_id="test-123",
        vehicle_id="TN37AB1234",
        engine_temperature=95.0,
        battery_voltage=12.7,
        front_left_tyre_psi=32.0,
        front_right_tyre_psi=32.0,
        rear_left_tyre_psi=31.0,
        rear_right_tyre_psi=31.0,
        coolant_level=75.0,
        latitude=19.076,
        longitude=72.8777,
    )

    print(f"Starting test with orchestrator at {ORCHESTRATOR_AGENT_ADDRESS}")
    print(f"Request ID: {request.request_id}")

    # Use the client agent's context to send_and_receive
    async def run_in_context():
        ctx = client_agent._ctx
        if ctx is None:
            print("Error: Client agent context not available")
            return

        try:
            print(f"\nSending message to Orchestrator...")
            response = await ctx.send_and_receive(
                destination=ORCHESTRATOR_AGENT_ADDRESS,
                message=request,
                timeout=30,
            )

            print(f"\nReceived response type: {type(response).__name__}")

            if isinstance(response, AutoRescueResponseMessage):
                print(f"✓ Status: {response.status}")
                print(f"  Diagnosis: {response.diagnosis.severity}")
                print(f"  Service Centres: {len(response.service_centres)}")
                print(f"  Navigation Allowed: {response.navigation_allowed}")
                if response.rescue:
                    print(f"  Rescue Type: {response.rescue.assistance_type}")
                return True

            elif isinstance(response, AutoRescueErrorMessage):
                print(f"✗ Error: {response.error}")
                return False

            else:
                print(f"Unexpected response type: {response}")
                return False

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Schedule the test
    client_agent._session.tasks.add(run_in_context())

    # Run the agent briefly
    await asyncio.sleep(2)


if __name__ == "__main__":
    print("=" * 60)
    print("Orchestrator Client Test (using Gateway Pattern)")
    print("=" * 60)

    # Start the client agent and run test
    async def main():
        # Note: This won't work because agent needs to be running
        # We need to use the agent's context properly
        print("This test requires the client agent to be running")
        print("For now, this just demonstrates the pattern")

    asyncio.run(main())
