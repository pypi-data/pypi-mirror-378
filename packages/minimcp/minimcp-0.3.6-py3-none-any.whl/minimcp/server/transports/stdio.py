import logging
import sys
from collections.abc import Awaitable, Callable
from io import TextIOWrapper

import anyio

from minimcp.server.types import Message, NoMessage, Send

logger = logging.getLogger(__name__)

StdioRequestHandler = Callable[[Message, Send], Awaitable[Message | NoMessage]]

stdin = anyio.wrap_file(TextIOWrapper(sys.stdin.buffer, encoding="utf-8"))
stdout = anyio.wrap_file(TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True))


async def write_msg(response: Message | NoMessage):
    if not isinstance(response, NoMessage):
        logger.info("Writing response message to stdio: %s", response)
        await stdout.write(response + "\n")
        await stdout.flush()


async def handle_message(handler: StdioRequestHandler, line: str):
    line = line.rstrip("\n").strip()

    if line:
        logger.info("Handling incoming message: %s", line)

        response = await handler(line, write_msg)

        await write_msg(response)


async def concurrent_transport(handler: StdioRequestHandler):
    """
    Makes it easy to use MiniMCP over stdio with concurrent handling of messages.
    - The anyio.wrap_file implementation naturally apply backpressure.
    - Concurrency management is expected to be enforced by MiniMCP.

    Args:
        handler: A function that will be called for each incoming message. It will be called
            with the message and a send function to write responses. Message returned by the function
            will be send back to the client.

    Returns:
        None
    """

    async with anyio.create_task_group() as tg:
        async for line in stdin:
            tg.start_soon(handle_message, handler, line)


async def sequential_transport(handler: StdioRequestHandler):
    """
    Makes it easy to use MiniMCP over stdio with sequential handling of messages. Its useful when all the handlers
    are synchronous. By being sequential, the transport avoid the need for a task management and instead
    handle messages one at a time.
    - The anyio.wrap_file implementation naturally apply backpressure.
    - Concurrency management is expected to be enforced by MiniMCP.

    Args:
        handler: A function that will be called for each incoming message. It will be called
            with the message and a send function to write responses. Message returned by the function
            will be send back to the client.

    Returns:
        None
    """

    async for line in stdin:
        await handle_message(handler, line)
