#!/usr/bin/env python3
"""Run Phase 9 Orchestrator Agent."""
import sys
sys.path.insert(0, "/c/Users/Jayanth/Downloads/AutoRescueAI/AutoRescue-Backend")

from agents.orchestrator_uagent_phase9 import agent

if __name__ == "__main__":
    agent.run()
