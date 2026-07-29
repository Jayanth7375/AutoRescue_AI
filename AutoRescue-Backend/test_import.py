try:
    import sys
    sys.path.insert(0, '.')
    from agents.messages import AutoRescueRequestMessage
    from agents.orchestrator_uagent import orchestrate_sync
    print("? Import successful")
except Exception as e:
    print(f"? Import failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
