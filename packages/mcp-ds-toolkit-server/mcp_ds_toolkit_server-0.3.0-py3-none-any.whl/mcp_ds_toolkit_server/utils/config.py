"""Configuration management for the MCP DS Toolkit server."""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from mcp_ds_toolkit_server.exceptions import ConfigurationError
from mcp_ds_toolkit_server.utils.common import ensure_directory
from mcp_ds_toolkit_server.utils.logger import make_logger

logger = make_logger(__name__)


class PathManager:
    """Unified path management for all MCP DS Toolkit data."""

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize PathManager with unified directory structure.

        Args:
            base_dir: Base directory for all MCP data. Defaults to ~/.mcp-ds-toolkit
        """
        self.base_dir = base_dir or Path.home() / ".mcp-ds-toolkit"

        # Core directories
        self.data_dir = self.base_dir / "data"
        self.uploads_dir = self.base_dir / "uploads"
        self.config_dir = self.base_dir / "config"

        # ML/AI directories
        self.models_dir = self.base_dir / "models"
        self.experiments_dir = self.base_dir / "experiments"
        self.workspace_dir = self.base_dir / "workspace"
        self.artifacts_dir = self.base_dir / "artifacts"

        # Cache directories (consolidated)
        self.cache_dir = self.base_dir / "cache"
        self.huggingface_cache = self.cache_dir / "huggingface"
        self.matplotlib_cache = self.cache_dir / "matplotlib"
        self.torch_cache = self.cache_dir / "torch"
        self.jupyter_cache = self.cache_dir / "jupyter"
        self.memory_cache = self.cache_dir / "memory"

        # Database files
        self.experiments_db = self.base_dir / "experiments.db"

        logger.info(f"PathManager initialized with base directory: {self.base_dir}")

    def ensure_all_directories(self) -> None:
        """Create all necessary directories in the unified structure."""
        directories = [
            self.data_dir,
            self.uploads_dir,
            self.config_dir,
            self.models_dir,
            self.experiments_dir,
            self.workspace_dir,
            self.artifacts_dir,
            self.cache_dir,
            self.huggingface_cache,
            self.matplotlib_cache,
            self.torch_cache,
            self.jupyter_cache,
            self.memory_cache,
        ]

        created_dirs = []
        for directory in directories:
            try:
                created_dir = ensure_directory(directory)
                created_dirs.append(str(created_dir))
            except Exception as e:
                logger.warning(f"Failed to create directory {directory}: {e}")

        logger.debug(f"Ensured unified directories: {created_dirs}")

    def get_cache_env_vars(self) -> dict:
        """Get environment variables for cache redirection."""
        return {
            "HUGGINGFACE_HUB_CACHE": str(self.huggingface_cache),
            "TRANSFORMERS_CACHE": str(self.huggingface_cache),
            "HF_HOME": str(self.huggingface_cache),
            "TORCH_HOME": str(self.torch_cache),
            "MPLCONFIGDIR": str(self.matplotlib_cache),
            "JUPYTER_DATA_DIR": str(self.jupyter_cache),
        }

    def apply_cache_redirection(self) -> None:
        """Apply cache redirection environment variables."""
        env_vars = self.get_cache_env_vars()
        for key, value in env_vars.items():
            os.environ[key] = value
            logger.debug(f"Set {key}={value}")



@dataclass
class Settings:
    """Configuration settings for the MCP DS Toolkit server."""

    # Application settings
    app_name: str = field(default="mcp-ds-toolkit-server")
    app_version: str = field(default="0.3.0")
    app_description: str = field(
        default="MCP DS Toolkit Server - A comprehensive DS toolkit with natural language interface"
    )

    # Server settings
    debug: bool = field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Unified path management
    path_manager: PathManager = field(init=False)




    # Resource limits
    max_dataset_size_mb: int = field(
        default_factory=lambda: int(os.getenv("MAX_DATASET_SIZE_MB", "1000"))
    )
    max_model_size_mb: int = field(
        default_factory=lambda: int(os.getenv("MAX_MODEL_SIZE_MB", "500"))
    )
    max_concurrent_jobs: int = field(
        default_factory=lambda: int(os.getenv("MAX_CONCURRENT_JOBS", "4"))
    )

    # Training settings
    default_test_size: float = field(
        default_factory=lambda: float(os.getenv("DEFAULT_TEST_SIZE", "0.2"))
    )
    default_random_state: int = field(
        default_factory=lambda: int(os.getenv("DEFAULT_RANDOM_STATE", "42"))
    )


    def __post_init__(self):
        """Initialize unified configuration with PathManager."""
        # Initialize PathManager with optional base directory override
        base_dir = os.getenv("MCP_DS_TOOLKIT_DIR")
        self.path_manager = PathManager(Path(base_dir) if base_dir else None)

        # Apply cache redirection immediately
        self.path_manager.apply_cache_redirection()

        # Create unified directory structure
        try:
            self.path_manager.ensure_all_directories()
        except Exception as e:
            logger.warning(f"Failed to create some unified directories: {e}")

        self._validate_config()
        logger.info(f"Settings initialized with unified structure at: {self.path_manager.base_dir}")

    def _validate_config(self) -> None:
        """Validate configuration values."""
        if self.max_dataset_size_mb <= 0:
            raise ConfigurationError(
                f"max_dataset_size_mb must be positive, got {self.max_dataset_size_mb}"
            )

        if not (0 < self.default_test_size < 1):
            raise ConfigurationError(
                f"default_test_size must be between 0 and 1, got {self.default_test_size}"
            )

    def ensure_directories(self) -> None:
        """Ensure all required directories exist using PathManager."""
        try:
            self.path_manager.ensure_all_directories()
        except Exception as e:
            logger.warning(f"Failed to ensure unified directories: {e}")


