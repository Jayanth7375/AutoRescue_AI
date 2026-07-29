from uagents.communication import send_sync_message
import inspect

print("send_sync_message signature:")
print(inspect.signature(send_sync_message))
print("\nsend_sync_message docstring:")
print(send_sync_message.__doc__)
