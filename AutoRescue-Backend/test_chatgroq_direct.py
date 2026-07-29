"""Direct test of ChatGroq LLM without FastAPI."""

import os
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

logger.info("=" * 70)
logger.info("DIRECT CHATGROQ SMOKE TEST")
logger.info("=" * 70)

# Check GROQ_API_KEY
groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    logger.info("✓ GROQ_API_KEY configured (present)")
    logger.info(f"  Key preview: {groq_api_key[:10]}...{groq_api_key[-10:]}")
else:
    logger.error("✗ GROQ_API_KEY not found in environment")
    exit(1)

# Get model from env or use default
model_name = os.getenv("CHATBOT_MODEL", "mixtral-8x7b-32768")
logger.info(f"✓ Model: {model_name}")

try:
    logger.info("\nInitializing ChatGroq...")

    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name=model_name,
        temperature=0.7,
        max_tokens=500,
    )

    logger.info("✓ ChatGroq initialized successfully")

    logger.info("\nSending test message to Groq API...")

    messages = [
        SystemMessage(content="You are a helpful assistant. Reply only with: 'ChatGroq working'"),
        HumanMessage(content="Test message"),
    ]

    response = llm.invoke(messages)
    reply = response.content

    logger.info(f"✓ Response received:")
    logger.info(f"  Content: {reply}")

    if "ChatGroq working" in reply or "working" in reply.lower():
        logger.info("\n✓✓✓ CHATGROQ IS WORKING ✓✓✓")
    else:
        logger.warning(f"\n⚠ Unexpected response (but LLM is working): {reply}")

except Exception as e:
    logger.error(f"\n✗✗✗ CHATGROQ FAILED ✗✗✗")
    logger.error(f"Error type: {type(e).__name__}")
    logger.error(f"Error message: {str(e)}")
    logger.exception("Full traceback:")
    exit(1)

logger.info("\n" + "=" * 70)
logger.info("SMOKE TEST COMPLETE")
logger.info("=" * 70)
