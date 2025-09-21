"""
MCP Data Science Toolkit - Main Entry Point

This module provides the main entry point for the MCP Data Science Toolkit server,
handling command-line interface initialization, logging setup, and server startup.

The module supports both direct execution and programmatic usage, providing
flexible deployment options for different environments and use cases.

Functions:
    run_server: Async function to run the server with optional settings
    cli_main: CLI entry point for command-line execution

Example:
    Run the server directly from command line::

        python -m mcp_ds_toolkit --mcp-dir ./my_mcp_data

    Or programmatically::

        from mcp_ds_toolkit_server.__main__ import run_server
        import asyncio

        asyncio.run(run_server())
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

from mcp_ds_toolkit_server.server import main
from mcp_ds_toolkit_server.utils.config import Settings
from mcp_ds_toolkit_server.utils.logger import setup_logging


async def run_server(settings: Optional[Settings] = None, mcp_dir: Optional[str] = None) -> None:
    """Run the MCP Data Science Toolkit server.

    Initializes and starts the server with proper logging configuration
    and error handling. This function can be used for programmatic
    server startup in custom deployment scenarios.

    Args:
        settings (Optional[Settings]): Configuration settings for the server.
            If None, creates a new Settings instance with default values.
        mcp_dir (Optional[str]): Base directory for unified MCP data storage.
            If provided, overrides default MCP base directory.

    Note:
        This function is the primary async entry point for server execution
        and should be called within an asyncio event loop.
    """
    if settings is None:
        settings = Settings()

    # Set up logging
    setup_logging(settings)

    # Run the server with unified directory structure
    await main()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for unified MCP structure.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="MCP Data Science Toolkit Server")
    parser.add_argument(
        "--mcp-dir",
        type=str,
        help="Base directory for unified MCP data storage (default: ~/.mcp-ds-toolkit)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level (default: INFO)",
    )
    return parser.parse_args()


def cli_main() -> None:
    """CLI entry point for the MCP Data Science Toolkit server.

    Handles command-line execution of the server with proper error handling
    and graceful shutdown on keyboard interrupt. This function provides
    the standard entry point for running the server from the command line.

    The function handles:
        - Command-line argument parsing
        - Unified MCP directory setup
        - Asyncio event loop management
        - Graceful shutdown on Ctrl+C
        - Error logging and appropriate exit codes

    Exit Codes:
        0: Normal shutdown (user interrupt)
        1: Error during server execution
    """
    # Parse command line arguments
    args = parse_args()

    # Set environment variables for unified structure
    if args.mcp_dir:
        import os
        os.environ["MCP_DS_TOOLKIT_DIR"] = str(Path(args.mcp_dir).resolve())
        print(f"Using MCP directory: {args.mcp_dir}")

    # Create settings with unified structure (PathManager handles directory creation)
    settings = Settings()
    settings.log_level = args.log_level

    from mcp_ds_toolkit_server.utils.logger import make_logger
    logger = make_logger(__name__)

    try:
        asyncio.run(run_server(settings=settings))
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
