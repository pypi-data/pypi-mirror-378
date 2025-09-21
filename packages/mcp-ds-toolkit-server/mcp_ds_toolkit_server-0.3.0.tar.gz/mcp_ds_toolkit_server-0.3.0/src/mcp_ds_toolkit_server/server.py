"""
MCP Data Science Toolkit Server

This module implements the main server for the MCP Data Science Toolkit,
providing a comprehensive interface for data science operations through
the Model Context Protocol.

The server orchestrates various data science tools and workflows, including
data management, model training, experiment tracking, and more. It provides
a natural language interface for interacting with complex data science
pipelines.

Classes:
    MCPDataScienceServer: Main server class that handles MCP protocol integration

Functions:
    main: Entry point for starting the server

Example:
    Starting the server::

        from mcp_ds_toolkit_server.server import main

        # Start the server with default configuration
        await main()

Note:
    The server requires proper initialization of all toolkit components
    including local SQLite tracking, data management tools, and ML frameworks.
"""

from typing import Any, Callable, Coroutine, Optional
import asyncio
import os

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

from mcp_ds_toolkit_server.tools import (
    DataManagementTools,
    TrackingTools,
    TrainingTools,
)
from mcp_ds_toolkit_server.utils.config import Settings
from mcp_ds_toolkit_server.utils.logger import make_logger
from mcp_ds_toolkit_server.utils.persistence import ArtifactBridge, create_default_persistence_config

logger = make_logger(__name__)

# Initialize settings and server
settings = Settings()
server = Server(settings.app_name)


class MCPDataScienceServer:
    """Main MCP Data Science Toolkit Server.

    This class implements the core server functionality for the MCP Data Science Toolkit,
    orchestrating various data science operations and tools through the Model Context Protocol.

    The server handles initialization, validation, tool registration, and provides a unified
    interface for data science workflows including data management, model training,
    experiment tracking, and workflow orchestration.

    Attributes:
        settings (Settings): Configuration settings for the server
        server (Server): MCP server instance for protocol communication
        logger (Logger): Logging instance for server operations
        tool_handlers (dict[str, Callable]): Registry of available MCP tool handlers
        startup_errors (list[str]): List of errors encountered during startup

    Example:
        Creating and starting the server::

            server = MCPDataScienceServer()
            await server.run()

    Note:
        The server performs comprehensive startup validation including directory
        structure, dependency checks, and local tracking system initialization.
    """

    def __init__(self) -> None:
        """Initialize the MCP Data Science Server.

        Performs startup validation and initializes all required components
        including settings, logging, tool handlers, and validation checks.

        Raises:
            RuntimeError: If critical startup validation fails
            ImportError: If required dependencies are missing
        """
        self.settings = settings
        self.server = server
        self.logger = logger
        self.tool_handlers: dict[str, Callable] = {}
        self.startup_errors: list[str] = []

        # Enhanced startup validation
        self._validate_startup()

    def _validate_startup(self) -> None:
        """Perform comprehensive startup validation.

        Validates all critical components required for the server to function properly,
        including directory structure, local tracking system, and dependencies.

        Raises:
            RuntimeError: If any critical validation step fails
        """
        try:
            # Validate directories
            self._validate_directories()

            # Validate local tracking system
            self._validate_local_tracking()

            # Validate dependencies
            self._validate_dependencies()

        except Exception as e:
            self.logger.error(f"Critical startup validation failed: {e}")
            raise
    
    def _validate_directories(self) -> None:
        """Validate and create required directories.

        Ensures all necessary directories for the toolkit are created and accessible,
        including workspace, model storage, experiment tracking, and temporary directories.

        Note:
            Errors in directory creation are logged as warnings and added to startup_errors
            but do not prevent server initialization.
        """
        try:
            self.settings.ensure_directories()
            self.logger.info("Directory structure validated successfully")
        except Exception as e:
            error_msg = f"Failed to create required directories: {e}"
            self.startup_errors.append(error_msg)
            self.logger.warning(error_msg)
    
    def _validate_local_tracking(self) -> None:
        """Validate local experiment tracking system.

        Initializes and tests the local SQLite-based experiment tracking system
        to ensure it can store and retrieve experiment data properly.

        The validation includes:
            - Importing the tracking module
            - Creating a tracker instance
            - Testing basic database operations
            - Listing existing experiments

        Note:
            Tracking system failures are logged as warnings and added to startup_errors
            but do not prevent server initialization.
        """
        try:
            from mcp_ds_toolkit_server.tracking import get_tracker

            # Initialize local tracker
            tracker = get_tracker()
            self.logger.info(f"Local experiment tracking initialized: {tracker.db_path}")

            # Test basic functionality
            experiments = tracker.list_experiments()
            self.logger.info(f"Found {len(experiments)} existing experiments")

        except Exception as e:
            error_msg = f"Local tracking initialization failed: {e}"
            self.startup_errors.append(error_msg)
            self.logger.warning(error_msg)
    
    def _validate_dependencies(self) -> None:
        """Validate critical dependencies are available.

        Checks that all required Python packages are installed and importable.
        This includes core data science libraries and the MCP framework.

        Critical dependencies:
            - pandas: Data manipulation and analysis
            - numpy: Numerical computing
            - scikit-learn: Machine learning algorithms
            - mcp: Model Context Protocol framework

        Note:
            Missing dependencies are logged as errors and added to startup_errors
            but do not prevent server initialization to allow for graceful degradation.
        """
        critical_deps = [
            ('pandas', 'pandas'),
            ('numpy', 'numpy'),
            ('sklearn', 'scikit-learn'),
            ('mcp', 'mcp')
        ]

        for module_name, package_name in critical_deps:
            try:
                __import__(module_name)
            except ImportError as e:
                error_msg = f"Critical dependency missing: {package_name} ({e})"
                self.startup_errors.append(error_msg)
                self.logger.error(error_msg)

        # Initialize shared artifact bridge for persistence across all tools
        default_persistence_config = create_default_persistence_config("memory_only")
        self.shared_artifact_bridge = ArtifactBridge(default_persistence_config)
        logger.info(f"Initialized shared artifact bridge with mode: {default_persistence_config.mode.value}")

        # Initialize data management tools with unified config and shared artifact bridge
        self.data_tools = DataManagementTools(
            config=settings,
            artifact_bridge=self.shared_artifact_bridge
        )
        self._register_data_tools()

        # Initialize training tools with unified config and shared dataset registry
        logger.info(f"Passing datasets to TrainingTools - Registry ID: {id(self.data_tools.datasets)}, Keys: {list(self.data_tools.datasets.keys())}")
        self.training_tools = TrainingTools(
            config=settings,
            datasets=self.data_tools.datasets,
            dataset_metadata=self.data_tools.dataset_metadata,
            artifact_bridge=self.shared_artifact_bridge
        )
        self._register_training_tools()

        # Initialize tracking tools with unified config and shared artifact bridge
        self.tracking_tools = TrackingTools(
            config=settings,
            artifact_bridge=self.shared_artifact_bridge
        )
        self._register_tracking_tools()
        
        # Final validation
        self.logger.info(f"MCP Data Science Toolkit initialized with {len(self.tool_handlers)} tools")
        if self.startup_errors:
            self.logger.info(f"Initialization completed with {len(self.startup_errors)} non-critical issues")

    def _register_data_tools(self) -> None:
        """Register data management tools with the server.

        Iterates through all available data management tools and creates
        appropriate handlers for each tool, registering them with the server
        for MCP protocol communication.
        """
        for tool in self.data_tools.get_tools():
            self.tool_handlers[tool.name] = self._create_tool_handler(self.data_tools, tool.name)

    def _register_training_tools(self) -> None:
        """Register training tools with the server.

        Iterates through all available training tools and creates
        appropriate handlers for each tool, registering them with the server
        for MCP protocol communication.
        """
        for tool in self.training_tools.get_tools():
            self.tool_handlers[tool.name] = self._create_tool_handler(self.training_tools, tool.name)


    def _register_tracking_tools(self) -> None:
        """Register tracking tools with the server.

        Iterates through all available tracking tools and creates
        appropriate handlers for each tool, registering them with the server
        for MCP protocol communication.
        """
        for tool in self.tracking_tools.get_tools():
            self.tool_handlers[tool.name] = self._create_tool_handler(self.tracking_tools, tool.name)

    def _create_tool_handler(self, tool_manager, tool_name: str) -> Callable:
        """Create a handler for a specific tool.

        Creates an async handler function that wraps tool manager calls
        for proper integration with the MCP protocol.

        Args:
            tool_manager: The tool manager instance (DataManagementTools, TrainingTools, etc.)
            tool_name (str): Name of the tool to create a handler for

        Returns:
            Callable: Async handler function for the specified tool
        """
        async def handler(args):
            return await tool_manager.handle_tool_call(tool_name, args)
        return handler

    def register_tool_handler(self, tool_name: str, handler: Callable) -> None:
        """Register a tool handler.

        Allows external registration of custom tool handlers with the server.

        Args:
            tool_name (str): Name of the tool to register
            handler (Callable): Async handler function for the tool
        """
        self.tool_handlers[tool_name] = handler

    async def run(self) -> None:
        """Run the MCP Data Science Toolkit server.

        Starts the server and handles MCP protocol communication through
        standard input/output streams. This is the main entry point for
        server execution.

        The server will run indefinitely until interrupted, handling
        all incoming MCP requests and routing them to appropriate tools.
        """
        self.logger.info("Running MCP Data Science Toolkit Server")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.settings.app_name,
                    server_version=self.settings.app_version,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(
                            resources_changed=True,
                            tools_changed=True,
                            prompts_changed=True,
                        ),
                        experimental_capabilities={},
                    ),
                ),
            )


# Global server instance - will be initialized in main()
mcp_server: MCPDataScienceServer = None


@server.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    """List available prompts for the MCP Data Science Toolkit server.

    Provides a list of predefined prompts that can be used to guide
    common data science and machine learning workflows.

    Returns:
        list[types.Prompt]: List of available prompts for data science workflows
    """
    return [
        types.Prompt(
            name="analyze_dataset",
            description="Analyze an uploaded dataset using the MCP Data Science Toolkit",
            arguments=[
                types.PromptArgument(
                    name="dataset_path",
                    description="Path to the dataset file (CSV, JSON, Parquet, etc.)",
                    required=True,
                ),
                types.PromptArgument(
                    name="analysis_focus",
                    description="What to focus on in the analysis (e.g., 'data quality', 'correlations', 'outliers')",
                    required=False,
                ),
            ],
        ),
        types.Prompt(
            name="ml_workflow_guide",
            description="Guide for end-to-end ML workflow using the MCP Data Science Toolkit",
            arguments=[
                types.PromptArgument(
                    name="task_type",
                    description="Type of ML task (classification, regression, clustering, etc.)",
                    required=False,
                ),
                types.PromptArgument(
                    name="dataset_type",
                    description="Type of dataset (tabular, text, image, etc.)",
                    required=False,
                ),
            ],
        ),
        types.Prompt(
            name="model_comparison",
            description="Compare different models for a specific task",
            arguments=[
                types.PromptArgument(
                    name="models",
                    description="List of model names to compare",
                    required=True,
                ),
                types.PromptArgument(
                    name="metrics",
                    description="Evaluation metrics to use for comparison",
                    required=False,
                ),
            ],
        ),
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
    """Get a specific prompt with the provided arguments.

    Handles dynamic prompt generation based on user-provided arguments.
    Currently supports the 'analyze_dataset' prompt for uploaded files.

    Args:
        name (str): Name of the prompt to retrieve
        arguments (dict[str, str] | None): Arguments to customize the prompt

    Returns:
        types.GetPromptResult: The generated prompt with instructions

    Raises:
        ValueError: If the prompt name is unknown or required arguments are missing
    """
    if name == "analyze_dataset":
        if not arguments or "dataset_path" not in arguments:
            raise ValueError("Missing required argument: dataset_path")

        dataset_path = arguments["dataset_path"]
        analysis_focus = arguments.get("analysis_focus", "comprehensive data analysis")

        # Generate comprehensive analysis prompt
        prompt_text = f"""I'll help you analyze the dataset at: {dataset_path}

Focus area: {analysis_focus}

Let me start by loading and exploring this dataset. I'll use the MCP Data Science Toolkit to:

1. Load the dataset using the load_dataset tool
2. Examine its structure, size, and basic statistics
3. Check for data quality issues (missing values, outliers, etc.)
4. Perform exploratory data analysis based on your focus area
5. Provide insights and recommendations

Let me begin by loading the dataset:"""

        return types.GetPromptResult(
            description=f"Dataset analysis for {dataset_path}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text),
                )
            ],
        )

    elif name == "ml_workflow_guide":
        task_type = arguments.get("task_type", "general") if arguments else "general"
        dataset_type = arguments.get("dataset_type", "tabular") if arguments else "tabular"

        prompt_text = f"""I'll guide you through an end-to-end machine learning workflow for a {task_type} task with {dataset_type} data.

Here's the recommended workflow using the MCP Data Science Toolkit:

1. **Data Loading & Exploration**
   - Load your dataset using the load_dataset tool
   - Examine data structure, quality, and distributions

2. **Data Preprocessing**
   - Handle missing values and outliers
   - Feature engineering and selection

3. **Model Selection & Training**
   - Choose appropriate algorithms for {task_type} tasks
   - Train models with proper validation

4. **Evaluation & Optimization**
   - Assess model performance with relevant metrics
   - Hyperparameter tuning and optimization

5. **Model Deployment**
   - Save and version your trained models
   - Track experiments and results

Let's start with your dataset. Do you have data ready to load?"""

        return types.GetPromptResult(
            description=f"ML workflow guide for {task_type} with {dataset_type} data",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text),
                )
            ],
        )

    elif name == "model_comparison":
        if not arguments or "models" not in arguments:
            raise ValueError("Missing required argument: models")

        models = arguments["models"]
        metrics = arguments.get("metrics", "accuracy, precision, recall, f1-score")

        prompt_text = f"""I'll help you compare these models: {models}

Evaluation metrics to use: {metrics}

Here's my systematic approach:

1. **Training Multiple Models**
   - Train each model: {models}
   - Use consistent data splits and preprocessing

2. **Performance Evaluation**
   - Calculate metrics: {metrics}
   - Cross-validation for robust estimates

3. **Comparative Analysis**
   - Performance comparison across metrics
   - Statistical significance testing
   - Training time and resource usage

4. **Model Selection Recommendation**
   - Best performing model for your use case
   - Trade-offs analysis (performance vs. complexity)

Let's start by loading your dataset and training these models."""

        return types.GetPromptResult(
            description=f"Model comparison: {models}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text),
                )
            ],
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools for the MCP Data Science Toolkit.

    Aggregates and returns all available tools from data management,
    training, and tracking modules.

    Returns:
        list[types.Tool]: List of available tools for data science operations
    """
    if mcp_server is None:
        return []

    # Return all available tools
    all_tools = []
    all_tools.extend(mcp_server.data_tools.get_tools())
    all_tools.extend(mcp_server.training_tools.get_tools())
    all_tools.extend(mcp_server.tracking_tools.get_tools())
    return all_tools


@server.call_tool()
async def call_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Call a specific tool with the given arguments.

    Routes tool calls to the appropriate tool handler based on the tool name.
    This is the main entry point for all MCP tool interactions.

    Args:
        tool_name (str): Name of the tool to call
        arguments (dict[str, Any]): Arguments to pass to the tool

    Returns:
        list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            List of content items returned by the tool execution

    Raises:
        ValueError: If the server is not initialized or tool name is not recognized
    """
    if mcp_server is None:
        raise ValueError("Server not initialized")

    if tool_name not in mcp_server.tool_handlers:
        raise ValueError(f"Tool {tool_name} not found")

    return await mcp_server.tool_handlers[tool_name](arguments)


@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources.

    Lists all available resources in the data science toolkit including
    datasets, trained models, experiment results, and other artifacts.

    Returns:
        list[types.Resource]: List of available resources (datasets, models, experiments, etc.)

    Raises:
        ValueError: If the server is not initialized
    """
    if mcp_server is None:
        raise ValueError("Server not initialized")

    # Get all resources from the artifact bridge
    resources = mcp_server.shared_artifact_bridge.get_all_resources()

    # Convert to MCP Resource types
    mcp_resources = []
    for resource in resources:
        mcp_resources.append(types.Resource(
            uri=resource["uri"],
            name=resource["name"],
            description=resource.get("description", ""),
            mimeType=resource.get("mimeType", "application/octet-stream")
        ))

    return mcp_resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource.

    Retrieves the content of a specific resource identified by its URI.
    Resources can include datasets, model files, experiment logs, etc.
    Supports both ds-toolkit:// URIs (artifacts) and file:// URIs (uploaded files).

    Args:
        uri (str): URI of the resource to read

    Returns:
        str: Content of the resource

    Raises:
        ValueError: If the server is not initialized or resource URI is not recognized
    """
    if mcp_server is None:
        raise ValueError("Server not initialized")

    # Handle simple filenames for data files
    if not uri.startswith("ds-toolkit://"):
        # Treat as simple filename in data directory
        return _read_data_file(uri)

    # Handle ds-toolkit:// URIs through artifact bridge
    try:
        # Get resource content from artifact bridge
        content_bytes = mcp_server.shared_artifact_bridge.get_resource_content(uri)

        # Convert bytes to string for MCP protocol
        return content_bytes.decode('utf-8')

    except KeyError:
        raise ValueError(f"Resource {uri} not found")
    except UnicodeDecodeError:
        # If content is binary, return base64 encoded
        import base64
        content_bytes = mcp_server.shared_artifact_bridge.get_resource_content(uri)
        return base64.b64encode(content_bytes).decode('ascii')
    except Exception as e:
        raise ValueError(f"Error reading resource {uri}: {str(e)}")


def _read_data_file(filename: str) -> str:
    """Read a file from the data directory.

    Args:
        filename: Name of file in data directory

    Returns:
        str: File content

    Raises:
        ValueError: If file not found or access denied
    """
    from pathlib import Path
    import base64

    # Resolve file path within data directory
    file_path = settings.path_manager.data_dir / filename

    # Security validation: ensure path stays within data directory
    try:
        resolved_path = file_path.resolve()
        data_dir_resolved = settings.path_manager.data_dir.resolve()

        # Check if resolved path is within data directory
        if not str(resolved_path).startswith(str(data_dir_resolved)):
            raise ValueError(f"Access denied: path traversal not allowed")

    except Exception as e:
        raise ValueError(f"Invalid file path: {filename}")

    # Check if file exists
    if not file_path.exists():
        # Ensure data directory exists for clear error message
        settings.path_manager.data_dir.mkdir(parents=True, exist_ok=True)
        raise ValueError(
            f"File '{filename}' not found.\n"
            f"Please save your file to the data directory: {settings.path_manager.data_dir}"
        )

    if not file_path.is_file():
        raise ValueError(f"'{filename}' is not a file")

    # Read file content
    try:
        # Try reading as text first
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Read data file: {filename}")
        return content
    except UnicodeDecodeError:
        # Handle binary files with base64 encoding
        try:
            with open(file_path, 'rb') as f:
                binary_content = f.read()
            logger.info(f"Read binary data file: {filename}")
            return base64.b64encode(binary_content).decode('ascii')
        except Exception as e:
            raise ValueError(f"Failed to read file '{filename}': {str(e)}")


async def perform_startup_checks() -> None:
    """Perform comprehensive startup checks before server initialization.

    Validates the system environment, Python version, and other prerequisites
    to ensure the server can start successfully. This includes checking for
    required Python version, available disk space, and system compatibility.

    Note:
        This function logs warnings for non-critical issues but does not
        prevent server startup.
    """
    logger.info("Performing pre-startup system checks...")
    
    # Check Python version
    import sys
    if sys.version_info < (3, 12):
        logger.warning(f"Python {sys.version_info} detected, Python 3.12+ recommended for optimal performance")
    
    # Check disk space
    import shutil
    try:
        workspace_path = settings.path_manager.workspace_dir
        total, used, free = shutil.disk_usage(workspace_path.parent)
        free_gb = free // (1024**3)
        if free_gb < 1:
            logger.warning(f"Low disk space: {free_gb}GB available")
        else:
            logger.info(f"Disk space check: {free_gb}GB available")
    except Exception as e:
        logger.warning(f"Could not check disk space: {e}")
    
    # Check optional environment variables
    optional_env_vars = [
        'WORKSPACE_PATH',
    ]
    
    missing_vars = []
    for var in optional_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.info(f"Using default values for: {', '.join(missing_vars)}")
    
    logger.info("Pre-startup checks completed")


async def main() -> None:
    """Main entry point for the MCP Data Science Toolkit server.

    Orchestrates the complete server startup sequence including:
        - Pre-startup system validation checks
        - Server instance initialization and configuration
        - Startup error handling and reporting
        - Main server execution loop

    The function handles all initialization errors gracefully and provides
    detailed logging for troubleshooting startup issues.

    Raises:
        Exception: If critical startup failures occur that prevent server operation
    """
    global mcp_server, settings

    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    try:
        # Pre-flight checks
        await perform_startup_checks()

        # Initialize the server instance
        mcp_server = MCPDataScienceServer()

        # Check for startup errors
        if mcp_server.startup_errors:
            logger.warning(f"Server started with {len(mcp_server.startup_errors)} warnings:")
            for error in mcp_server.startup_errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("Server startup validation completed successfully")

        await mcp_server.run()

    except Exception as e:
        logger.error(f"Failed to start MCP Data Science Toolkit server: {e}")
        logger.error("Server startup failed - check configuration and dependencies")
        raise


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
