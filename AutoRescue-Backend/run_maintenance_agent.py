#!/usr/bin/env python3
"""Run maintenance Agent."""
import sys
sys.path.insert(0, "/c/Users/Jayanth/Downloads/AutoRescueAI/AutoRescue-Backend")

from agents.maintenance_uagent import agent

if __name__ == "__main__":
    agent.run()
