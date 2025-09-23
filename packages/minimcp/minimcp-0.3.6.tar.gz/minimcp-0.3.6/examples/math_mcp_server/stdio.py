import logging
import os

import anyio

from minimcp import stdio

from .math_mcp import math_mcp

# Configure logging globally for the demo server
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.environ.get("MCP_SERVER_LOG_FILE", "mcp_server.log")),
        logging.StreamHandler(),  # Also log to stderr
    ],
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("MiniMCP: Started stdio server with concurrent transport, listening for messages...")
    anyio.run(stdio.concurrent_transport, math_mcp.handle)
