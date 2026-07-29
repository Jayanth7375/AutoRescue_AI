#!/usr/bin/env python3
"""Run safety Agent."""
import sys
sys.path.insert(0, "/c/Users/Jayanth/Downloads/AutoRescueAI/AutoRescue-Backend")

from agents.safety_uagent import agent

if __name__ == "__main__":
    agent.run()
