import argparse
import asyncio
import logging
import os
import pathlib
import signal
import sys
import time
import uuid

from langgraph.pregel import Pregel
from langgraph_distributed_utils.constants import DEFAULT_EXECUTOR_ADDRESS

from langgraph_executor.executor import create_server
from langgraph_executor.info_logger import ExecutorInfo, ExecutorInfoLogger

EXECUTOR_INFO_FILE_NAME = "info.json"

YELLOW = "\033[93m"
RESET = "\033[0m"


class ColoredFormatter(logging.Formatter):
    def __init__(self, color=YELLOW, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color

    def format(self, record):
        formatted_message = super().format(record)
        return f"{self.color}{formatted_message}{RESET}"


def setup_server_logging(component_id: str, debug=False, color=YELLOW):
    """Setup logging for server with executor ID label"""
    level = logging.DEBUG if debug else logging.INFO

    # Clear any existing handlers to prevent duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    # Configure logging
    logging.basicConfig(
        level=level,
        format=f"[{component_id}] %(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )

    # Apply colored formatter to all handlers
    for handler in logging.root.handlers:
        handler.setFormatter(
            ColoredFormatter(
                color=color,
                fmt=f"[{component_id}] %(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            ),
        )


def create_executor_info(address: str, id: str):
    return ExecutorInfo(
        id=id,
        pid=os.getpid(),
        address=address,
        start_time=time.time(),
        status="starting",
        error_message=None,
        end_time=None,
    )


def signum_to_name(signum):
    try:
        return signal.Signals(signum).name
    except ValueError:
        return f"UNKNOWN_SIGNAL_{signum}"


async def serve(
    graphs: dict[str, Pregel],
    *,
    address: str = DEFAULT_EXECUTOR_ADDRESS,
    debug: bool = False,
    id: str | None = None,
    log_dir: pathlib.Path | None = None,
):
    """Start the gRPC server.

    Args:
        graphs: Dictionary mapping graph names to compiled graphs
        port: Port to listen on

    """
    id_ = id
    if id_ is None:
        id_ = str(uuid.uuid4())

    setup_server_logging(f"EXECUTOR {id_}", debug=debug)
    logger = logging.getLogger(__name__)

    info_logger = ExecutorInfoLogger(
        log_dir or pathlib.Path(__file__).resolve().parent.parent / "logs",
    )

    server = create_server(graphs, address)

    await server.start()
    loop = asyncio.get_event_loop()

    # Signal handler for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum_to_name(signum)}. Shutting down...")
        asyncio.run_coroutine_threadsafe(
            server.stop(5), loop
        )  # Give 5 seconds for graceful shutdown
        info_logger.update_executor_info(
            executor_info.id,
            status="stopped",
            error_message=f"Shutdown via signal {signum_to_name(signum)}",
            end_time=time.time(),
        )
        logger.info("Shutdown complete")
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    executor_info = create_executor_info(address, id_)
    info_logger.write_executor_info(executor_info)

    try:
        info_logger.update_executor_info(executor_info.id, status="running")
        logger.info(f"Listening at address {address}...")
        await server.wait_for_termination()
    except Exception as e:
        logger.exception("Unexpected error in executor")
        await server.stop(0)
        info_logger.update_executor_info(
            executor_info.id,
            status="error",
            error_message=str(e),
            end_time=time.time(),
        )
        raise


def main():
    """Start a LangGraph executor server."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", type=str, default=DEFAULT_EXECUTOR_ADDRESS)
    parser.add_argument("--debug", action="store_false")
    parser.add_argument(
        "--log-dir",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[2] / "logs",
    )

    args = parser.parse_args()

    id_ = str(uuid.uuid4())

    setup_server_logging(f"EXECUTOR {id_}", debug=args.debug)
    logging.getLogger(__name__)

    # load sample graphs for demo purposes
    try:
        from langgraph_distributed_utils.sample_graphs import (  # type: ignore[import-not-found]
            GRAPHS,  # type: ignore[import-untyped]
        )

    except ImportError:
        GRAPHS = {}

    graphs = GRAPHS

    # serve
    asyncio.run(
        serve(graphs, address=args.address, debug=args.debug, log_dir=args.log_dir)
    )


if __name__ == "__main__":
    main()
