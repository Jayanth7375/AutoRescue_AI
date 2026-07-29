import asyncio
from agents.diagnostic_uagent import diagnostic_uagent
from agents.messages import VehicleTelemetryMessage, DiagnosticResponseMessage

async def test():
    print("Diagnostic Agent test (direct instantiation):")
    print(f"Agent name: {diagnostic_uagent.name}")
    print(f"Agent address: {diagnostic_uagent.address}")
    
asyncio.run(test())
