"""Comprehensive Phase 2 uAgent testing script."""

import os
import sys
import time
import subprocess
import threading
import logging
from pathlib import Path
from uuid import uuid4

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).parent


def wait_for_agent_startup(port=8001, timeout=15):
    """Wait for agent to start by checking if it's listening."""
    import socket
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                logger.info(f"Agent is listening on port {port}")
                return True
        except Exception:
            pass
        time.sleep(0.5)

    return False


def extract_agent_address(output):
    """Extract agent address from startup output."""
    for line in output.split('\n'):
        if 'Agent Address:' in line:
            # Format: "Agent Address: agent1..."
            parts = line.split('Agent Address:')
            if len(parts) > 1:
                return parts[1].strip()
    return None


def run_diagnostic_agent_subprocess():
    """Start Diagnostic Agent in subprocess and return process + address."""
    logger.info("Starting Diagnostic Agent in subprocess...")

    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'

    proc = subprocess.Popen(
        [sys.executable, 'run_diagnostic_agent.py'],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    # Wait for startup and capture output
    agent_address = None
    startup_output = []
    start_time = time.time()
    timeout = 15

    while time.time() - start_time < timeout:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.5)
            continue

        startup_output.append(line)
        logger.info(line.rstrip())

        # Try to extract address
        if 'Agent Address:' in line:
            agent_address = extract_agent_address(line)
            if agent_address:
                logger.info(f"Found agent address: {agent_address}")

        # Check if agent is ready
        if 'Waiting for' in line or 'listening' in line.lower():
            if agent_address:
                break

        if agent_address and time.time() - start_time > 5:
            break

    if not agent_address:
        logger.warning("Could not extract agent address from startup output")
        # Try alternative extraction
        full_output = '\n'.join(startup_output)
        agent_address = extract_agent_address(full_output)

    return proc, agent_address


def test_agent_communication(agent_address):
    """Test agent-to-agent communication."""
    if not agent_address:
        logger.error("No agent address available for testing")
        return False

    logger.info("\n" + "=" * 60)
    logger.info("Phase 2: Testing uAgent Communication")
    logger.info("=" * 60)

    # Update .env with agent address
    env_file = PROJECT_ROOT / '.env'
    env_content = env_file.read_text()
    env_content = env_content.replace('DIAGNOSTIC_AGENT_ADDRESS=', f'DIAGNOSTIC_AGENT_ADDRESS={agent_address}')
    env_file.write_text(env_content)
    logger.info(f"Updated .env with agent address: {agent_address}")

    # Import and run test client
    os.environ['DIAGNOSTIC_AGENT_ADDRESS'] = agent_address

    logger.info("Starting test client...")
    logger.info("Sending engine overheating telemetry (should return CRITICAL)...")

    # Start test client with a reasonable timeout
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'

    proc = subprocess.Popen(
        [sys.executable, 'tests/agent_client.py'],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    test_output = []
    test_passed = False
    start_time = time.time()
    timeout = 20

    while time.time() - start_time < timeout:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            time.sleep(0.2)
            continue

        test_output.append(line)
        logger.info(line.rstrip())

        # Check for test result
        if '✓ TEST PASSED' in line:
            test_passed = True

    # Cleanup
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except:
        proc.kill()

    return test_passed


def main():
    """Main test orchestration."""
    logger.info("=" * 60)
    logger.info("AutoRescue AI Backend - Phase 2 Testing")
    logger.info("=" * 60)

    # Start diagnostic agent
    agent_proc, agent_address = run_diagnostic_agent_subprocess()

    if not agent_address:
        logger.error("Failed to start Diagnostic Agent or extract its address")
        agent_proc.terminate()
        return 1

    logger.info(f"\n✓ Diagnostic Agent started at {agent_address}")

    # Give agent time to fully initialize
    time.sleep(2)

    # Test communication
    try:
        test_passed = test_agent_communication(agent_address)
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        test_passed = False
    finally:
        # Cleanup agent process
        logger.info("\nShutting down Diagnostic Agent...")
        try:
            agent_proc.terminate()
            agent_proc.wait(timeout=5)
        except:
            agent_proc.kill()

    logger.info("\n" + "=" * 60)
    if test_passed:
        logger.info("✓ PHASE 2 TEST PASSED")
        logger.info("=" * 60)
        return 0
    else:
        logger.error("✗ PHASE 2 TEST FAILED")
        logger.info("=" * 60)
        logger.info("Troubleshooting:")
        logger.info("1. Check that uagents is installed: uv sync")
        logger.info("2. Check agent ports are not in use (8001, 8002)")
        logger.info("3. Check DIAGNOSTIC_AGENT_ADDRESS environment variable")
        return 1


if __name__ == "__main__":
    sys.exit(main())
