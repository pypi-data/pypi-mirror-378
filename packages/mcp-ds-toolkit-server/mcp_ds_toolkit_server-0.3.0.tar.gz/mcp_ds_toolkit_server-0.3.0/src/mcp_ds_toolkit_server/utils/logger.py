"""Logging utilities for the MCP Data Science Toolkit server."""

import logging
import os
import sys
from typing import Optional, Union


def make_logger(name: str, settings: Optional[Union[object, dict]] = None) -> logging.Logger:
    """Create a logger with the specified name and configuration.

    Args:
        name: Name of the logger.
        settings: Optional settings object or dict. If None, uses environment variables.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Don't add handlers if they already exist
    if logger.handlers:
        return logger

    # Get log level from settings or environment
    if settings is not None:
        if hasattr(settings, 'log_level'):
            log_level_str = settings.log_level
        elif isinstance(settings, dict):
            log_level_str = settings.get('log_level', 'INFO')
        else:
            log_level_str = 'INFO'
    else:
        log_level_str = os.getenv("LOG_LEVEL", "INFO")

    # Set log level
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create console handler - use stderr for MCP protocol compliance
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger


def setup_logging(settings: Optional[Union[object, dict]] = None) -> None:
    """Set up logging configuration for the entire application.

    Args:
        settings: Optional settings object or dict. If None, uses environment variables.
    """
    # Get log level and debug from settings or environment
    if settings is not None:
        if hasattr(settings, 'log_level'):
            log_level_str = settings.log_level
            debug = getattr(settings, 'debug', False)
        elif isinstance(settings, dict):
            log_level_str = settings.get('log_level', 'INFO')
            debug = settings.get('debug', False)
        else:
            log_level_str = 'INFO'
            debug = False
    else:
        log_level_str = os.getenv("LOG_LEVEL", "INFO")
        debug = os.getenv("DEBUG", "false").lower() == "true"

    # Configure root logger - use stderr for MCP protocol compliance
    logging.basicConfig(
        level=getattr(logging, log_level_str.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    # Set specific log levels for third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("sklearn").setLevel(logging.WARNING)

    if debug:
        logging.getLogger("mcp_ds_toolkit_server").setLevel(logging.DEBUG)
    else:
        logging.getLogger("mcp_ds_toolkit_server").setLevel(logging.INFO)
