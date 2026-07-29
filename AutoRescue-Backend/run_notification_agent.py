#!/usr/bin/env python3
"""Run notification Agent."""
import sys
sys.path.insert(0, "/c/Users/Jayanth/Downloads/AutoRescueAI/AutoRescue-Backend")

from agents.notification_uagent import agent

if __name__ == "__main__":
    agent.run()
