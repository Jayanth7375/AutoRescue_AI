try:
    from uagents.network import ErrorMessage
    print("? ErrorMessage imported successfully from uagents.network")
except ImportError as e:
    print(f"? Cannot import from uagents.network: {e}")

try:
    from uagents import ErrorMessage
    print("? ErrorMessage imported successfully from uagents")
except ImportError as e:
    print(f"? Cannot import from uagents: {e}")

try:
    from uagents_core.types import ErrorMessage
    print("? ErrorMessage imported successfully from uagents_core.types")
except ImportError as e:
    print(f"? Cannot import from uagents_core.types: {e}")

# Check what's available
import uagents
print("\nAvailable in uagents:", [x for x in dir(uagents) if "error" in x.lower()])
