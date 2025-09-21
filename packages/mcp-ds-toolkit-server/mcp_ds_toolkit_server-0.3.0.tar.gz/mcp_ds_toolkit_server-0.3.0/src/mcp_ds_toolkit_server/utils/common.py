"""
Common utilities and shared functionality for the MCP Data Science Toolkit server.

This module provides reusable utilities for directory management, error handling,
and configuration validation used across the codebase.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Union

from mcp_ds_toolkit_server.utils.logger import make_logger

logger = make_logger(__name__)


def ensure_directory(
    path: Union[str, Path], create_parents: bool = True, fallback_to_temp: bool = True
) -> Path:
    """
    Ensure a directory exists with consistent error handling.

    Args:
        path: Directory path to ensure
        create_parents: Whether to create parent directories
        fallback_to_temp: Whether to fallback to temp directory on failure

    Returns:
        Path object pointing to the ensured directory

    Raises:
        OSError: If directory creation fails and fallback is disabled
    """
    path = Path(path)

    try:
        path.mkdir(parents=create_parents, exist_ok=True)

        # Verify writability
        test_file = path / ".test_write"
        test_file.touch()
        test_file.unlink()

        return path

    except (OSError, PermissionError) as e:
        if fallback_to_temp:
            temp_base = Path(tempfile.gettempdir()) / "mcp-ds-toolkit-server"
            temp_base.mkdir(parents=True, exist_ok=True)

            # Create relative path structure in temp
            relative_path = path.name if path.is_absolute() else path
            temp_path = temp_base / relative_path
            temp_path.mkdir(parents=True, exist_ok=True)

            logger.warning(
                f"Cannot create directory {path}: {e}. "
                f"Using temporary directory: {temp_path}"
            )
            return temp_path
        else:
            raise OSError(f"Cannot create directory {path}: {e}")




def validate_path(path: Union[str, Path], must_exist: bool = False) -> Path:
    """
    Validate and normalize a path.

    Args:
        path: Path to validate
        must_exist: Whether the path must exist

    Returns:
        Normalized Path object

    Raises:
        FileNotFoundError: If path must exist and doesn't
        ValueError: If path is invalid
    """
    try:
        path = Path(path).resolve()
        if must_exist and not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        return path
    except FileNotFoundError:
        # Re-raise FileNotFoundError as-is
        raise
    except Exception as e:
        raise ValueError(f"Invalid path: {e}")


