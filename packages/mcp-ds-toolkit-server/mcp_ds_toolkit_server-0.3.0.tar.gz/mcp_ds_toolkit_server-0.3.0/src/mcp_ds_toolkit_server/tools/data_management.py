"""Data Management Tools Module

This module provides MCP tools for comprehensive data management operations
including dataset loading, validation, profiling, and preprocessing.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np
import pandas as pd
from mcp.types import (
    EmbeddedResource,
    ImageContent,
    LoggingLevel,
    TextContent,
    Tool,
)

from mcp_ds_toolkit_server.tools.base import BaseMCPTools
from mcp_ds_toolkit_server.data import (
    CleaningConfig,
    CrossValidationMethod,
    DataCleaner,
    DataProfiler,
    DatasetLoader,
    DataSplitter,
    DataValidator,
    EncodingMethod,
    ImputationMethod,
    MissingDataConfig,
    MissingDataHandler,
    MissingDataMethod,
    OutlierAction,
    OutlierConfig,
    OutlierDetector,
    OutlierMethod,
    PreprocessingConfig,
    PreprocessingPipeline,
    ScalingMethod,
    SelectionMethod,
    SplittingConfig,
    SplittingMethod,
)
from mcp_ds_toolkit_server.data.model_evaluation import (
    CrossValidationConfig,
    HyperparameterTuningConfig,
    HyperparameterTuningMethod,
    ModelEvaluator,
    TaskType,
    get_default_param_grids,
)
from mcp_ds_toolkit_server.exceptions import DataError
from mcp_ds_toolkit_server.utils import (
    UnifiedDataResolver,
    ArtifactBridge,
    PersistenceConfig,
    create_default_persistence_config,
    Settings,
)


class DataManagementTools(BaseMCPTools):
    """MCP tools for data management operations."""

    def __init__(self, config, artifact_bridge=None):
        """Initialize data management tools.

        Args:
            config: Settings object with unified path management
            artifact_bridge: Artifact bridge for persistence operations
        """
        # Use base class initialization to eliminate redundancy
        super().__init__(
            workspace_path=config.path_manager.workspace_dir,
            persistence_mode="memory_only",
            artifact_bridge=artifact_bridge
        )

        # Store config for unified path access
        self.config = config

        # Initialize components with unified cache structure
        cache_dir = str(self.config.path_manager.cache_dir)
        self.loader = DatasetLoader(cache_dir=cache_dir)
        self.validator = DataValidator()
        self.profiler = DataProfiler()
        self.preprocessing_pipeline = PreprocessingPipeline()
        self.cleaning_pipeline = DataCleaner()
        self.splitter = DataSplitter()

        # Store loaded datasets - initialize first
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.dataset_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Initialize unified data resolver for intelligent dataset discovery
        self.data_resolver = UnifiedDataResolver(
            memory_registry=self.datasets,
            artifact_bridge=self.artifact_bridge,
            data_loader=self.loader  # Use our workspace-specific loader
        )
        
        self.logger.info(f"DataManagementTools initialized - Registry ID: {id(self.datasets)}, Keys: {list(self.datasets.keys())}")

    def _get_mime_type_for_format(self, format: str) -> str:
        """Get MIME type for dataset format.

        Args:
            format: Dataset format (csv, json, etc.)

        Returns:
            MIME type string
        """
        mime_types = {
            "csv": "text/csv",
            "json": "application/json",
            "parquet": "application/octet-stream",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "sql": "text/plain",
            "hdf5": "application/octet-stream",
            "feather": "application/octet-stream"
        }
        return mime_types.get(format, "text/plain")


    def _resolve_dataset(self, dataset_name: str, dataset_path: str = None, artifact_key: str = None):
        """Resolve dataset using unified data resolver.

        This method provides intelligent dataset discovery across multiple sources:
        1. Unified data resolver (artifact bridge, memory, filesystem)

        Args:
            dataset_name: Name of the dataset
            dataset_path: Optional filesystem path
            artifact_key: Optional artifact bridge key

        Returns:
            tuple: (DataFrame, data_reference) or raises DataError if not found
        """
        try:
            # Use unified data resolver
            df, data_reference = self.data_resolver.resolve_data(
                dataset_name=dataset_name,
                dataset_path=dataset_path,
                artifact_key=artifact_key,
                auto_fallback=True
            )
            self.logger.info(f"✅ Resolved dataset '{dataset_name}' via unified resolver from {data_reference.location_type}")
            return df, data_reference

        except Exception as resolver_error:
            # Check what datasets are available
            available_datasets = []

            try:
                available_datasets.extend([ref.name for ref in self.data_resolver.list_available_data()])
            except Exception:
                pass

            error_msg = f"Dataset '{dataset_name}' not found."
            if available_datasets:
                error_msg += f" Available datasets: {sorted(set(available_datasets))}"
            else:
                error_msg += " No datasets available. Load a dataset first."

            self.logger.error(f"❌ {error_msg}")
            raise DataError(error_msg)

    def get_tools(self) -> List[Tool]:
        """Get all available MCP tools for data management.

        Returns:
            List of MCP tools
        """
        return [
            # Dataset Loading Tools
            Tool(
                name="load_dataset",
                description="Load a dataset from various sources: uploaded files (full path), data directory (filename), URLs, or sklearn datasets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Path to dataset file (full path for uploaded files, filename for data directory), URL for remote datasets, or sklearn dataset name",
                        },
                        "format": {
                            "type": "string",
                            "enum": [
                                "csv",
                                "json",
                                "parquet",
                                "excel",
                                "sql",
                                "hdf5",
                                "feather",
                            ],
                            "description": "Dataset format",
                        },
                        "name": {
                            "type": "string",
                            "description": "Name to assign to the loaded dataset",
                        },
                        "options": {
                            "type": "object",
                            "description": "Additional loading options",
                            "properties": {
                                "encoding": {
                                    "type": "string",
                                    "description": "File encoding (utf-8, latin-1, cp1252, etc.)",
                                    "default": "utf-8",
                                },
                                "dataset_name": {
                                    "type": "string",
                                    "description": "For sklearn datasets: specify dataset name (wine, iris, etc.)",
                                },
                                "sep": {
                                    "type": "string",
                                    "description": "CSV separator character",
                                    "default": ",",
                                },
                            },
                            "additionalProperties": True,
                        },
                    },
                    "required": ["source", "format", "name"],
                },
            ),
            # Dataset Validation Tools
            Tool(
                name="validate_dataset",
                description="Validate dataset quality and check for issues",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to validate",
                        },
                        "validation_rules": {
                            "type": "object",
                            "description": "Custom validation rules",
                            "properties": {
                                "required_columns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Required column names",
                                },
                                "min_rows": {
                                    "type": "integer",
                                    "description": "Minimum number of rows required",
                                },
                                "max_missing_ratio": {
                                    "type": "number",
                                    "description": "Maximum allowed missing data ratio",
                                },
                                "allowed_dtypes": {
                                    "type": "object",
                                    "description": "Expected data types for columns",
                                    "additionalProperties": {"type": "string"},
                                },
                            },
                        },
                    },
                    "required": ["dataset_name"],
                },
            ),
            # Dataset Profiling Tools
            Tool(
                name="profile_dataset",
                description="Generate comprehensive data profile and statistics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to profile",
                        },
                        "include_correlations": {
                            "type": "boolean",
                            "description": "Include correlation analysis",
                            "default": True,
                        },
                        "include_distributions": {
                            "type": "boolean",
                            "description": "Include distribution analysis",
                            "default": True,
                        },
                        "correlation_threshold": {
                            "type": "number",
                            "description": "Correlation threshold for reporting",
                            "default": 0.5,
                        },
                    },
                    "required": ["dataset_name"],
                },
            ),
            # Data Preprocessing Tools
            Tool(
                name="preprocess_dataset",
                description="Apply preprocessing transformations to dataset",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to preprocess",
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Target column name for supervised learning",
                        },
                        "preprocessing_config": {
                            "type": "object",
                            "description": "Preprocessing configuration",
                            "properties": {
                                "scaling_method": {
                                    "type": "string",
                                    "enum": [
                                        "standard",
                                        "minmax",
                                        "robust",
                                        "maxabs",
                                        "quantile_uniform",
                                        "quantile_normal",
                                        "power_yeojonson",
                                        "power_boxcox",
                                        "none",
                                        "standardize",
                                        "normalize",
                                    ],
                                    "description": "Scaling method to apply (supports both full names and common aliases)",
                                },
                                "encoding_method": {
                                    "type": "string",
                                    "enum": ["onehot", "label", "target", "ordinal"],
                                    "description": "Categorical encoding method",
                                },
                                "feature_selection": {
                                    "type": "object",
                                    "properties": {
                                        "method": {
                                            "type": "string",
                                            "enum": [
                                                "variance",
                                                "correlation",
                                                "univariate",
                                                "rfe",
                                                "lasso",
                                            ],
                                            "description": "Feature selection method",
                                        },
                                        "params": {
                                            "type": "object",
                                            "description": "Feature selection parameters",
                                            "additionalProperties": True,
                                        },
                                    },
                                },
                                "handle_missing": {
                                    "type": "boolean",
                                    "description": "Handle missing values",
                                    "default": True,
                                },
                            },
                        },
                        "output_name": {
                            "type": "string",
                            "description": "Name for the preprocessed dataset",
                        },
                    },
                    "required": ["dataset_name", "output_name"],
                },
            ),
            # Data Cleaning Tools
            Tool(
                name="clean_dataset",
                description="Clean dataset by handling missing values and outliers",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to clean",
                        },
                        "missing_strategy": {
                            "type": "string",
                            "enum": [
                                "drop_rows",
                                "drop_columns",
                                "fill_median",
                                "fill_mean",
                                "fill_mode",
                                "fill_constant",
                                "fill_forward",
                                "fill_backward",
                                "fill_interpolate",
                                "fill_knn",
                                "fill_iterative",
                                "median",
                                "mean",
                                "mode",
                            ],
                            "description": "Strategy for handling missing values (supports both full names and short aliases)",
                        },
                        "outlier_strategy": {
                            "type": "string",
                            "enum": ["remove", "cap", "transform", "flag", "leave_as_is"],
                            "description": "Strategy for handling outliers",
                            "default": "cap",
                        },
                        "outlier_method": {
                            "type": "string",
                            "enum": [
                                "z_score",
                                "modified_z_score",
                                "iqr",
                                "isolation_forest",
                                "local_outlier_factor",
                                "dbscan",
                                "percentile",
                                "statistical_distance",
                                "zscore",
                                "lof",
                            ],
                            "description": "Method for outlier detection (supports both full names and short aliases)",
                            "default": "iqr",
                        },
                        "missing_constant_value": {
                            "type": ["string", "number"],
                            "description": "Value to use when missing_strategy is fill_constant",
                            "default": 0,
                        },
                        "missing_drop_threshold": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Proportion of missing values above which to drop columns/rows",
                            "default": 0.5,
                        },
                        "missing_knn_neighbors": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "description": "Number of neighbors for KNN imputation",
                            "default": 5,
                        },
                        "missing_max_iter": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum iterations for iterative imputation",
                            "default": 10,
                        },
                        "missing_random_state": {
                            "type": "integer",
                            "description": "Random seed for reproducible imputation",
                            "default": 42,
                        },
                        "outlier_z_threshold": {
                            "type": "number",
                            "minimum": 1.0,
                            "maximum": 5.0,
                            "description": "Z-score threshold for outlier detection",
                            "default": 3.0,
                        },
                        "outlier_iqr_multiplier": {
                            "type": "number",
                            "minimum": 0.5,
                            "maximum": 3.0,
                            "description": "IQR multiplier for outlier detection",
                            "default": 1.5,
                        },
                        "outlier_contamination": {
                            "type": "number",
                            "minimum": 0.01,
                            "maximum": 0.5,
                            "description": "Expected contamination ratio for isolation forest and LOF",
                            "default": 0.1,
                        },
                        "outlier_percentile_lower": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 50.0,
                            "description": "Lower percentile bound for percentile-based outlier detection",
                            "default": 5.0,
                        },
                        "outlier_percentile_upper": {
                            "type": "number",
                            "minimum": 50.0,
                            "maximum": 100.0,
                            "description": "Upper percentile bound for percentile-based outlier detection",
                            "default": 95.0,
                        },
                        "outlier_dbscan_eps": {
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 2.0,
                            "description": "DBSCAN epsilon parameter",
                            "default": 0.5,
                        },
                        "outlier_dbscan_min_samples": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "description": "DBSCAN minimum samples parameter",
                            "default": 5,
                        },
                        "handle_missing_first": {
                            "type": "boolean",
                            "description": "Handle missing values before outlier detection",
                            "default": True,
                        },
                        "preserve_original": {
                            "type": "boolean",
                            "description": "Preserve original dataset alongside cleaned version",
                            "default": True,
                        },
                        "output_name": {
                            "type": "string",
                            "description": "Name for the cleaned dataset",
                        },
                    },
                    "required": ["dataset_name", "output_name"],
                },
            ),
            # Data Splitting Tools
            Tool(
                name="split_dataset",
                description="Split dataset into train/validation/test sets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to split",
                        },
                        "split_method": {
                            "type": "string",
                            "enum": [
                                "random",
                                "stratified",
                                "time_series",
                                "group_based",
                            ],
                            "description": "Method for splitting the dataset",
                        },
                        "test_size": {
                            "type": "number",
                            "description": "Proportion of data for test set",
                            "default": 0.2,
                        },
                        "val_size": {
                            "type": "number",
                            "description": "Proportion of data for validation set (creates 70/20/10 split by default)",
                            "default": 0.1,
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Target column for stratified splitting",
                        },
                        "time_column": {
                            "type": "string",
                            "description": "Time column for time-series splitting",
                        },
                        "group_column": {
                            "type": "string",
                            "description": "Group column for group-based splitting",
                        },
                        "random_state": {
                            "type": "integer",
                            "description": "Random seed for reproducibility",
                            "default": 42,
                        },
                    },
                    "required": ["dataset_name", "split_method"],
                },
            ),
            # Dataset Information Tools
            Tool(
                name="list_datasets",
                description="List all loaded datasets with their metadata",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_details": {
                            "type": "boolean",
                            "description": "Include detailed information about each dataset",
                            "default": False,
                        }
                    },
                },
            ),
            Tool(
                name="get_dataset_info",
                description="Get detailed information about a specific dataset",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset",
                        },
                        "include_sample": {
                            "type": "boolean",
                            "description": "Include sample data",
                            "default": True,
                        },
                        "sample_size": {
                            "type": "integer",
                            "description": "Number of sample rows to include",
                            "default": 5,
                        },
                    },
                    "required": ["dataset_name"],
                },
            ),
            # Data Comparison Tools
            Tool(
                name="compare_datasets",
                description="Compare structure and statistics of two datasets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset1_name": {
                            "type": "string",
                            "description": "Name of the first dataset",
                        },
                        "dataset2_name": {
                            "type": "string",
                            "description": "Name of the second dataset",
                        },
                        "comparison_type": {
                            "type": "string",
                            "enum": ["structure", "statistics", "full"],
                            "description": "Type of comparison to perform",
                            "default": "full",
                        },
                        "include_samples": {
                            "type": "boolean",
                            "description": "Include sample data in comparison",
                            "default": False,
                        },
                    },
                    "required": ["dataset1_name", "dataset2_name"],
                },
            ),
            # Batch Processing Tools
            Tool(
                name="batch_process_datasets",
                description="Apply the same operation to multiple datasets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of dataset names to process",
                        },
                        "operation": {
                            "type": "string",
                            "enum": ["validate", "profile", "clean", "preprocess"],
                            "description": "Operation to apply to all datasets",
                        },
                        "operation_config": {
                            "type": "object",
                            "description": "Configuration for the operation",
                            "additionalProperties": True,
                        },
                        "output_prefix": {
                            "type": "string",
                            "description": "Prefix for output dataset names",
                            "default": "batch_",
                        },
                    },
                    "required": ["dataset_names", "operation"],
                },
            ),
            # Data Sampling Tools
            Tool(
                name="sample_dataset",
                description="Create a sample from a dataset",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to sample",
                        },
                        "sample_method": {
                            "type": "string",
                            "enum": [
                                "random",
                                "stratified",
                                "systematic",
                                "first_n",
                                "last_n",
                            ],
                            "description": "Sampling method",
                            "default": "random",
                        },
                        "sample_size": {
                            "type": "number",
                            "description": "Sample size (as fraction if <1, as count if >=1)",
                            "default": 0.1,
                        },
                        "target_column": {
                            "type": "string",
                            "description": "Target column for stratified sampling",
                        },
                        "output_name": {
                            "type": "string",
                            "description": "Name for the sampled dataset",
                        },
                        "random_state": {
                            "type": "integer",
                            "description": "Random seed for reproducibility",
                            "default": 42,
                        },
                    },
                    "required": ["dataset_name", "output_name"],
                },
            ),
            Tool(
                name="export_dataset",
                description="Export dataset to file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to export",
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Output file path",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["csv", "json", "parquet", "excel"],
                            "description": "Export format",
                        },
                        "options": {
                            "type": "object",
                            "description": "Export options",
                            "additionalProperties": True,
                        },
                        "persistence_mode": {
                            "type": "string",
                            "enum": ["memory_only", "filesystem", "hybrid"],
                            "description": "How to store exported data: memory_only (in-memory), filesystem (traditional files), hybrid (both)",
                            "default": "filesystem",
                        },
                    },
                    "required": ["dataset_name", "output_path", "format"],
                },
            ),
            Tool(
                name="remove_dataset",
                description="Remove a dataset from memory and optionally delete files",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to remove",
                        },
                        "delete_files": {
                            "type": "boolean",
                            "description": "Also delete the original data files",
                            "default": False,
                        }
                    },
                    "required": ["dataset_name"],
                },
            ),
            Tool(
                name="clear_all_data",
                description="Clear all datasets and cached data from current session",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "confirm": {
                            "type": "boolean",
                            "description": "Confirm you want to clear all data",
                            "default": False,
                        }
                    },
                    "required": ["confirm"],
                },
            ),
        ]

    async def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Handle MCP tool calls for data management operations.

        Args:
            tool_name: Tool name
            arguments: Tool arguments

        Returns:
            List of text content responses
        """
        try:
            if tool_name == "load_dataset":
                return await self._handle_load_dataset(arguments)
            elif tool_name == "validate_dataset":
                return await self._handle_validate_dataset(arguments)
            elif tool_name == "profile_dataset":
                return await self._handle_profile_dataset(arguments)
            elif tool_name == "preprocess_dataset":
                return await self._handle_preprocess_dataset(arguments)
            elif tool_name == "clean_dataset":
                return await self._handle_clean_dataset(arguments)
            elif tool_name == "split_dataset":
                return await self._handle_split_dataset(arguments)
            elif tool_name == "list_datasets":
                return await self._handle_list_datasets(arguments)
            elif tool_name == "get_dataset_info":
                return await self._handle_get_dataset_info(arguments)
            elif tool_name == "export_dataset":
                return await self._handle_export_dataset(arguments)
            elif tool_name == "sample_dataset":
                return await self._handle_sample_dataset(arguments)
            elif tool_name == "compare_datasets":
                return await self._handle_compare_datasets(arguments)
            elif tool_name == "batch_process_datasets":
                return await self._handle_batch_process_datasets(arguments)
            elif tool_name == "remove_dataset":
                return await self._handle_remove_dataset(arguments)
            elif tool_name == "clear_all_data":
                return await self._handle_clear_all_data(arguments)
            else:
                unknown_tool_result = {
                    "status": "error",
                    "message": f"Unknown tool: {tool_name}",
                    "available_tools": [tool.name for tool in self.get_tools()]
                }
                return self._create_json_response(unknown_tool_result)

        except Exception as e:
            return self._handle_tool_error(tool_name, e)

    async def _handle_load_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle load_dataset tool call using clean filesystem approach."""
        source = arguments["source"]
        format_type = arguments["format"]
        name = arguments["name"]
        options = arguments.get("options", {})

        # Handle sklearn dataset sources
        sklearn_datasets = ["iris", "wine", "breast_cancer", "diabetes", "digits"]

        if source and source.startswith("sklearn.datasets."):
            sklearn_name = source.split(".")[-1]
            source = sklearn_name
        elif source == "sklearn" and "dataset_name" in options:
            source = options["dataset_name"]
            options = {k: v for k, v in options.items() if k != "dataset_name"}

        try:
            # Handle URLs and sklearn datasets normally
            if (source.startswith(("http://", "https://")) or
                source in sklearn_datasets or
                source == "sklearn"):
                # Use DatasetLoader directly for URLs and sklearn datasets
                dataset, dataset_info = self.loader.load_dataset(source, **options)
            else:
                # Detect if this is an absolute path (uploaded file) or relative filename (data directory)
                from pathlib import Path
                from mcp_ds_toolkit_server.utils.config import Settings

                settings = Settings()
                source_path = Path(source)

                if source_path.is_absolute():
                    # Absolute path - likely an uploaded file from Claude Desktop
                    self.logger.info(f"Attempting to load from absolute path: {source}")
                    self.logger.info(f"Path exists: {source_path.exists()}")
                    if not source_path.exists():
                        # Try alternative common upload paths
                        alt_paths = [
                            Path("/tmp") / source_path.name,
                            Path("/var/tmp") / source_path.name,
                            Path.home() / "Downloads" / source_path.name
                        ]
                        for alt_path in alt_paths:
                            self.logger.info(f"Trying alternative path: {alt_path}")
                            if alt_path.exists():
                                source_path = alt_path
                                self.logger.info(f"Found file at alternative path: {alt_path}")
                                break
                        else:
                            raise ValueError(f"Uploaded file not found: {source}")

                    # Load directly from uploaded file path
                    dataset, dataset_info = self.loader.load_dataset(str(source_path), **options)
                    self.logger.info(f"Loaded dataset from uploaded file: {source_path}")

                else:
                    # Relative path - look in unified data directory
                    data_file_path = self.config.path_manager.data_dir / source

                    # Security validation: ensure path stays within data directory
                    resolved_path = data_file_path.resolve()
                    data_dir_resolved = self.config.path_manager.data_dir.resolve()

                    if not str(resolved_path).startswith(str(data_dir_resolved)):
                        raise ValueError(f"Access denied: path traversal not allowed")

                    if not data_file_path.exists():
                        self.config.path_manager.data_dir.mkdir(parents=True, exist_ok=True)
                        raise ValueError(
                            f"File '{source}' not found.\n"
                            f"Please save your file to the data directory: {self.config.path_manager.data_dir}\n"
                            f"Data directory contents: {list(self.config.path_manager.data_dir.glob('*')) if self.config.path_manager.data_dir.exists() else 'empty'}"
                        )

                    # Load dataset from data directory
                    dataset, dataset_info = self.loader.load_dataset(str(data_file_path), **options)
                    self.logger.info(f"Loaded dataset from data directory: {source}")

            # Store dataset in memory registry and artifact bridge
            self.datasets[name] = dataset
            self.dataset_metadata[name] = {
                "source": source,
                "format": format_type,
                "loaded_at": datetime.now().isoformat(),
                "shape": dataset.shape,
                "columns": list(dataset.columns),
                "dtypes": dataset.dtypes.to_dict(),
                "memory_usage": dataset.memory_usage(deep=True).sum(),
                "dataset_info": dataset_info,
            }

            # Store in artifact bridge for cross-tool sharing
            self.artifact_bridge.store_artifact(
                name,
                dataset,
                {
                    "type": "dataset",
                    "source": source,
                    "format": format_type,
                    "shape": dataset.shape,
                    "columns": list(dataset.columns)
                }
            )

            # Register dataset as MCP Resource
            try:
                resource_uri = self.artifact_bridge.register_resource(
                    artifact_key=f"dataset_{name}",
                    name=f"Dataset: {name}",
                    mime_type=self._get_mime_type_for_format(format_type),
                    description=f"Loaded dataset: {len(dataset)} rows, {len(dataset.columns)} columns"
                )
                self.logger.info(f"Registered dataset '{name}' as MCP Resource: {resource_uri}")
            except Exception as e:
                self.logger.warning(f"Failed to register dataset '{name}' as MCP Resource: {e}")

            return [
                TextContent(
                    type="text",
                    text=f"Successfully loaded dataset '{name}' from {source}\n"
                    f"Shape: {dataset.shape}\n"
                    f"Columns: {list(dataset.columns)}\n"
                    f"Memory usage: {dataset.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
                )
            ]

        except Exception as e:
            error_msg = f"Error loading dataset '{name}' from {source}: {str(e)}"
            self.logger.error(error_msg)

            error_result = {
                "status": "error",
                "message": error_msg,
                "dataset_name": name,
                "source": source
            }
            return self._create_json_response(error_result)

    async def _handle_validate_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle validate_dataset tool call."""
        dataset_name = arguments["dataset_name"]
        validation_rules = arguments.get("validation_rules", {})

        try:
            dataset, data_reference = self._resolve_dataset(
                dataset_name=dataset_name,
                dataset_path=arguments.get("dataset_path"),
                artifact_key=arguments.get("artifact_key")
            )
        except DataError as e:
            return [
                TextContent(
                    type="text",
                    text=str(e)
                )
            ]

        # Validate dataset - DataValidator doesn't need config
        report = self.validator.validate_dataset(dataset)

        # Create structured JSON response
        issues_data = []
        for issue in report.issues:
            issue_data = {
                "severity": issue.severity.value.upper(),
                "message": issue.message
            }
            if issue.column:
                issue_data["column"] = issue.column
            issues_data.append(issue_data)

        validation_result = {
            "status": "success",
            "dataset_name": dataset_name,
            "validation": {
                "overall_status": "PASSED" if not report.has_critical_issues() else "FAILED",
                "issues_count": len(report.issues),
                "quality_score": round(report.quality_score, 2),
                "completeness_score": round(report.completeness_score, 2),
                "issues": issues_data,
                "summary": {str(k): v for k, v in report.summary.items()}
            }
        }

        return self._create_json_response(validation_result)

    async def _handle_profile_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle profile_dataset tool call."""
        dataset_name = arguments["dataset_name"]
        include_correlations = arguments.get("include_correlations", True)
        include_distributions = arguments.get("include_distributions", True)
        correlation_threshold = arguments.get("correlation_threshold", 0.5)

        try:
            dataset, data_reference = self._resolve_dataset(
                dataset_name=dataset_name,
                dataset_path=arguments.get("dataset_path"),
                artifact_key=arguments.get("artifact_key")
            )
        except DataError as e:
            error_result = {
                "status": "error",
                "message": str(e),
                "dataset_name": dataset_name
            }
            return self._create_json_response(error_result)

        # Profile dataset - DataProfiler doesn't need config
        report = self.profiler.profile_dataset(dataset)

        # Create structured JSON response
        column_profiles = {}
        for col_name, col_profile in report.column_profiles.items():
            profile_data = {
                "type": str(col_profile.dtype),
                "non_null_count": report.row_count - col_profile.null_count,
                "unique_count": col_profile.unique_count,
            }
            if col_profile.mean is not None:
                profile_data["mean"] = round(col_profile.mean, 2)
            if col_profile.std is not None:
                profile_data["std"] = round(col_profile.std, 2)
            column_profiles[col_name] = profile_data

        correlations = []
        if include_correlations and report.correlation_analysis:
            for col1, col2, corr in report.correlation_analysis.strong_correlations:
                correlations.append({
                    "column1": col1,
                    "column2": col2,
                    "correlation": round(corr, 3)
                })

        profiling_result = {
            "status": "success",
            "dataset_name": dataset_name,
            "profiling": {
                "shape": list(dataset.shape),
                "memory_usage_mb": round(report.memory_usage / 1024 / 1024, 2),
                "quality_score": round(report.quality_score, 2),
                "row_count": report.row_count,
                "column_profiles": column_profiles,
                "missing_data": {
                    "overall_completeness": round(report.overall_completeness, 2) if hasattr(report, 'overall_completeness') else None,
                    "columns_with_missing": list(report.columns_with_missing) if hasattr(report, 'columns_with_missing') else []
                },
                "correlations": correlations,
                "correlation_threshold": correlation_threshold
            }
        }

        return self._create_json_response(profiling_result)

    async def _handle_preprocess_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle preprocess_dataset tool call."""
        dataset_name = arguments["dataset_name"]
        target_column = arguments.get("target_column")
        preprocessing_config = arguments.get("preprocessing_config", {})
        output_name = arguments["output_name"]

        if dataset_name not in self.datasets:
            return [
                TextContent(
                    type="text",
                    text=f"Dataset '{dataset_name}' not found. Please load it first.",
                )
            ]

        dataset = self.datasets[dataset_name]

        # Map user-friendly aliases to actual enum values
        def map_scaling_method(method):
            mapping = {"standardize": "standard", "normalize": "minmax"}
            return mapping.get(method, method)

        # Create preprocessing config
        config = PreprocessingConfig(
            numeric_scaling=ScalingMethod(
                map_scaling_method(
                    preprocessing_config.get("scaling_method", "standard")
                )
            ),
            categorical_encoding=EncodingMethod(
                preprocessing_config.get("encoding_method", "onehot")
            ),
            feature_selection=SelectionMethod(
                preprocessing_config.get("feature_selection_method", "none")
            ),
            numeric_imputation=ImputationMethod(
                preprocessing_config.get("imputation_strategy", "median")
            ),
            categorical_imputation=ImputationMethod(
                preprocessing_config.get("categorical_imputation_strategy", "mode")
            ),
            random_state=preprocessing_config.get("random_state", 42),
        )

        # Create preprocessor and preprocess dataset
        preprocessor = PreprocessingPipeline(config)

        # Fit and transform dataset
        if target_column and target_column in dataset.columns:
            X = dataset.drop(columns=[target_column])
            y = dataset[target_column]
            X_processed = preprocessor.fit_transform(X, y)

            # Combine processed features with target
            processed_data = X_processed.copy()
            processed_data[target_column] = y
        else:
            processed_data = preprocessor.fit_transform(dataset)

        # Store preprocessed dataset
        self.datasets[output_name] = processed_data
        self.dataset_metadata[output_name] = {
            "source": f"Preprocessed from {dataset_name}",
            "format": "dataframe",
            "loaded_at": datetime.now().isoformat(),
            "shape": processed_data.shape,
            "columns": list(processed_data.columns),
            "dtypes": processed_data.dtypes.to_dict(),
            "memory_usage": processed_data.memory_usage(deep=True).sum(),
            "preprocessing_config": preprocessing_config,
        }

        # Create structured JSON response
        preprocessing_result = {
            "status": "success",
            "operation": "preprocess_dataset",
            "input_dataset": dataset_name,
            "output_dataset": output_name,
            "shape_change": {
                "original": list(dataset.shape),
                "processed": list(processed_data.shape)
            },
            "preprocessing_config": {
                "numeric_scaling": config.numeric_scaling.value,
                "categorical_encoding": config.categorical_encoding.value,
                "feature_selection": config.feature_selection.value,
                "numeric_imputation": config.numeric_imputation.value,
                "categorical_imputation": config.categorical_imputation.value
            },
            "metadata": {
                "columns": list(processed_data.columns),
                "dtypes": {k: str(v) for k, v in processed_data.dtypes.to_dict().items()},
                "memory_usage_bytes": int(processed_data.memory_usage(deep=True).sum())
            }
        }

        return self._create_json_response(preprocessing_result)

    async def _handle_clean_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle clean_dataset tool call."""
        dataset_name = arguments["dataset_name"]
        missing_strategy = arguments.get("missing_strategy", "fill_median")
        outlier_strategy = arguments.get("outlier_strategy", "cap")
        outlier_method = arguments.get("outlier_method", "iqr")
        output_name = arguments["output_name"]

        if dataset_name not in self.datasets:
            return [
                TextContent(
                    type="text",
                    text=f"Dataset '{dataset_name}' not found. Please load it first.",
                )
            ]

        dataset = self.datasets[dataset_name]

        # Map user-friendly aliases to actual enum values
        def map_missing_strategy(strategy):
            mapping = {
                "median": "fill_median",
                "mean": "fill_mean",
                "mode": "fill_mode",
                "drop": "drop_rows",
            }
            return mapping.get(strategy, strategy)

        def map_outlier_method(method):
            mapping = {"zscore": "z_score", "lof": "local_outlier_factor"}
            return mapping.get(method, method)

        # Create comprehensive cleaning config with all parameters
        missing_config = MissingDataConfig(
            method=MissingDataMethod(map_missing_strategy(missing_strategy)),
            constant_value=arguments.get("missing_constant_value", 0),
            drop_threshold=arguments.get("missing_drop_threshold", 0.5),
            knn_neighbors=arguments.get("missing_knn_neighbors", 5),
            max_iter=arguments.get("missing_max_iter", 10),
            random_state=arguments.get("missing_random_state", 42),
        )
        outlier_config = OutlierConfig(
            method=OutlierMethod(map_outlier_method(outlier_method)),
            action=OutlierAction(outlier_strategy),
            z_threshold=arguments.get("outlier_z_threshold", 3.0),
            iqr_multiplier=arguments.get("outlier_iqr_multiplier", 1.5),
            contamination=arguments.get("outlier_contamination", 0.1),
            percentile_bounds=(
                arguments.get("outlier_percentile_lower", 5.0),
                arguments.get("outlier_percentile_upper", 95.0)
            ),
            dbscan_eps=arguments.get("outlier_dbscan_eps", 0.5),
            dbscan_min_samples=arguments.get("outlier_dbscan_min_samples", 5),
        )
        config = CleaningConfig(
            missing_data=missing_config,
            outlier_detection=outlier_config,
            handle_missing_first=arguments.get("handle_missing_first", True),
            preserve_original=arguments.get("preserve_original", True),
        )

        # Create cleaner and clean dataset
        cleaner = DataCleaner(config)
        cleaned_data, report = cleaner.clean_data(dataset)

        # Store cleaned dataset
        self.datasets[output_name] = cleaned_data
        self.dataset_metadata[output_name] = {
            "source": f"Cleaned from {dataset_name}",
            "format": "dataframe",
            "loaded_at": datetime.now().isoformat(),
            "shape": cleaned_data.shape,
            "columns": list(cleaned_data.columns),
            "dtypes": cleaned_data.dtypes.to_dict(),
            "memory_usage": cleaned_data.memory_usage(deep=True).sum(),
            "cleaning_config": {
                "missing_strategy": missing_strategy,
                "outlier_strategy": outlier_strategy,
                "outlier_method": outlier_method,
            },
        }

        # Format cleaning report
        result = f"Successfully cleaned dataset '{dataset_name}' -> '{output_name}'\n"
        result += f"Original shape: {dataset.shape}\n"
        result += f"Cleaned shape: {cleaned_data.shape}\n\n"
        result += "Cleaning Summary:\n"
        result += (
            f"  Missing data - Total: {report.missing_data_report.total_missing}\n"
        )
        result += f"  Missing data - Percentage: {report.missing_data_report.missing_percentage:.2f}%\n"
        result += f"  Outliers detected: {report.outlier_report.total_outliers}\n"
        result += f"  Outliers - Percentage: {report.outlier_report.outlier_percentage:.2f}%\n"
        result += f"  Actions taken: {', '.join(report.actions_taken)}\n"

        return [TextContent(type="text", text=result)]

    async def _handle_split_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle split_dataset tool call."""
        dataset_name = arguments["dataset_name"]
        split_method = arguments["split_method"]
        test_size = arguments.get("test_size", 0.2)
        val_size = arguments.get("val_size", 0.1)  # Better default: 70/20/10 split
        target_column = arguments.get("target_column")
        time_column = arguments.get("time_column")
        group_column = arguments.get("group_column")
        random_state = arguments.get("random_state", 42)

        if dataset_name not in self.datasets:
            return [
                TextContent(
                    type="text",
                    text=f"Dataset '{dataset_name}' not found. Please load it first.",
                )
            ]

        dataset = self.datasets[dataset_name]

        # Create splitting config
        config = SplittingConfig(
            method=(
                SplittingMethod(split_method)
                if isinstance(split_method, str)
                else split_method
            ),
            test_size=test_size,
            validation_size=val_size,
            train_size=1.0 - test_size - val_size,
            stratify_column=target_column,
            time_column=time_column,
            group_column=group_column,
            random_state=random_state,
        )

        # Create splitter and split dataset
        splitter = DataSplitter(config)
        train_df, val_df, test_df, split_report = splitter.split_data(
            dataset, target_column
        )

        # Store splits with proper naming
        splits = {"train": train_df, "validation": val_df, "test": test_df}

        for split_name, split_data in splits.items():
            full_name = f"{dataset_name}_{split_name}"
            self.datasets[full_name] = split_data
            self.dataset_metadata[full_name] = {
                "source": f"Split from {dataset_name}",
                "format": "dataframe",
                "loaded_at": datetime.now().isoformat(),
                "shape": split_data.shape,
                "columns": list(split_data.columns),
                "dtypes": split_data.dtypes.to_dict(),
                "memory_usage": split_data.memory_usage(deep=True).sum(),
                "split_info": {
                    "method": split_method,
                    "original_dataset": dataset_name,
                    "split_type": split_name,
                },
            }

        # Format split report
        result = (
            f"Successfully split dataset '{dataset_name}' using {split_method} method\n"
        )
        result += f"Original shape: {dataset.shape}\n\n"
        result += "Split Results:\n"
        for split_name, split_data in splits.items():
            result += f"  {split_name}: {split_data.shape} ({len(split_data)/len(dataset)*100:.1f}%)\n"

        return [TextContent(type="text", text=result)]


    async def _handle_list_datasets(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle list_datasets tool call."""
        include_details = arguments.get("include_details", False)

        if not self.datasets:
            return [
                TextContent(
                    type="text",
                    text="No datasets loaded. Use load_dataset to load a dataset first.",
                )
            ]

        result = f"Loaded Datasets (Registry ID: {id(self.datasets)}):\n"
        result += "=" * 30 + "\n\n"

        for name, dataset in self.datasets.items():
            metadata = self.dataset_metadata.get(name, {})
            result += f"📊 {name}\n"
            result += f"  Shape: {dataset.shape}\n"
            result += f"  Source: {metadata.get('source', 'Unknown')}\n"
            result += f"  Loaded: {metadata.get('loaded_at', 'Unknown')}\n"

            if include_details:
                result += f"  Columns: {list(dataset.columns)}\n"
                result += f"  Memory: {metadata.get('memory_usage', 0) / 1024 / 1024:.2f} MB\n"
                result += f"  Data Types: {len(set(dataset.dtypes))}\n"

            result += "\n"

        return [TextContent(type="text", text=result)]

    async def _handle_get_dataset_info(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_dataset_info tool call."""
        dataset_name = arguments["dataset_name"]
        include_sample = arguments.get("include_sample", True)
        sample_size = arguments.get("sample_size", 5)

        if dataset_name not in self.datasets:
            return [
                TextContent(
                    type="text",
                    text=f"Dataset '{dataset_name}' not found. Please load it first.",
                )
            ]

        dataset = self.datasets[dataset_name]
        metadata = self.dataset_metadata.get(dataset_name, {})

        # Format dataset information
        result = f"Dataset Information: {dataset_name}\n"
        result += "=" * 40 + "\n\n"
        result += f"Shape: {dataset.shape}\n"
        result += f"Columns: {len(dataset.columns)}\n"
        result += (
            f"Memory Usage: {metadata.get('memory_usage', 0) / 1024 / 1024:.2f} MB\n"
        )
        result += f"Source: {metadata.get('source', 'Unknown')}\n"
        result += f"Loaded At: {metadata.get('loaded_at', 'Unknown')}\n\n"

        # Column information
        result += "Column Information:\n"
        result += "-" * 20 + "\n"
        for col in dataset.columns:
            dtype = dataset[col].dtype
            non_null = dataset[col].notna().sum()
            unique = dataset[col].nunique()
            result += f"  {col}: {dtype} (non-null: {non_null}, unique: {unique})\n"

        # Sample data
        if include_sample:
            result += f"\nSample Data (first {sample_size} rows):\n"
            result += "-" * 30 + "\n"
            sample_data = dataset.head(sample_size).to_string()
            result += sample_data + "\n"

        return [TextContent(type="text", text=result)]

    async def _handle_export_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle export_dataset tool call with persistence system support."""
        dataset_name = arguments["dataset_name"]
        output_path = arguments["output_path"]
        format_type = arguments["format"]
        options = arguments.get("options", {})
        persistence_mode = arguments.get("persistence_mode", "filesystem")

        if dataset_name not in self.datasets:
            return [
                TextContent(
                    type="text",
                    text=f"Dataset '{dataset_name}' not found. Please load it first.",
                )
            ]

        dataset = self.datasets[dataset_name]

        try:
            # Create persistence configuration
            persistence_config = create_default_persistence_config(persistence_mode)
            
            # Update artifact bridge if needed
            if self.artifact_bridge.config.mode.value != persistence_mode:
                self.artifact_bridge = ArtifactBridge(persistence_config)
            
            # Generate artifact key for the exported dataset
            export_key = f"{dataset_name}_export_{format_type}"
            
            # Store in artifact bridge
            artifact_storage = self.artifact_bridge.store_artifact(
                key=export_key,
                artifact=dataset,
                artifact_type="dataset",
                filesystem_path=Path(output_path) if persistence_config.should_save_to_filesystem() else None
            )

            # Register as MCP Resource for Claude Desktop access
            mime_type_map = {
                "csv": "text/csv",
                "json": "application/json",
                "parquet": "application/parquet",
                "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
            resource_uri = self.artifact_bridge.register_resource(
                artifact_key=export_key,
                name=f"Exported {dataset_name} ({format_type})",
                mime_type=mime_type_map.get(format_type, "application/octet-stream"),
                description=f"Dataset '{dataset_name}' exported in {format_type} format"
            )

            # Format result text based on persistence mode
            result_text = f"Successfully exported dataset '{dataset_name}'\n"
            result_text += f"Format: {format_type}\n"
            result_text += f"Shape: {dataset.shape}\n"
            result_text += f"Persistence Mode: {persistence_mode}\n"
            result_text += f"Resource URI: {resource_uri}\n"
            result_text += "📥 Dataset available for download in Claude Desktop Resources\n"
            
            # Show artifact storage information
            if "memory_reference" in artifact_storage:
                result_text += f"Stored in memory (key: {export_key})\n"
            
            if "filesystem_reference" in artifact_storage:
                file_path = artifact_storage["filesystem_reference"].replace("file://", "")
                file_size = Path(file_path).stat().st_size / 1024 / 1024
                result_text += f"Saved to file: {file_path}\n"
                result_text += f"File size: {file_size:.2f} MB\n"
            
            if "fallback_to_memory" in artifact_storage:
                result_text += "⚠️ Filesystem write failed, using memory storage as fallback\n"

            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            return [
                TextContent(type="text", text=f"Failed to export dataset: {str(e)}")
            ]

    async def _handle_sample_dataset(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle dataset sampling."""
        try:
            dataset_name = arguments.get("dataset_name")

            if dataset_name not in self.datasets:
                return [
                    TextContent(
                        type="text", text=f"Dataset '{dataset_name}' not found."
                    )
                ]

            df = self.datasets[dataset_name].copy()

            # Get sampling parameters
            n_samples = arguments.get("n_samples", 100)
            method = arguments.get("method", "random")
            random_state = arguments.get("random_state", 42)
            stratify = arguments.get("stratify")

            # Perform sampling
            if method == "random":
                if len(df) <= n_samples:
                    sampled_df = df.copy()
                else:
                    sampled_df = df.sample(n=n_samples, random_state=random_state)
            elif method == "stratified" and stratify:
                if stratify in df.columns:
                    sampled_df = (
                        df.groupby(stratify, group_keys=False)
                        .apply(
                            lambda x: x.sample(
                                min(len(x), n_samples // df[stratify].nunique() + 1),
                                random_state=random_state,
                            )
                        )
                        .reset_index(drop=True)
                    )
                    if len(sampled_df) > n_samples:
                        sampled_df = sampled_df.sample(
                            n=n_samples, random_state=random_state
                        )
                else:
                    return [
                        TextContent(
                            type="text",
                            text=f"Stratification column '{stratify}' not found in dataset.",
                        )
                    ]
            elif method == "systematic":
                step = max(1, len(df) // n_samples)
                sampled_df = df.iloc[::step].head(n_samples).copy()
            else:
                return [
                    TextContent(type="text", text=f"Unknown sampling method: {method}")
                ]

            # Store the sampled dataset
            output_name = arguments.get("output_name", f"{dataset_name}_sample")
            self.datasets[output_name] = sampled_df

            # Update metadata
            metadata = self.dataset_metadata.get(dataset_name, {}).copy()
            metadata.update(
                {
                    "sampled_from": dataset_name,
                    "sampling_method": method,
                    "sample_size": len(sampled_df),
                    "sampling_ratio": len(sampled_df) / len(df),
                }
            )
            self.dataset_metadata[output_name] = metadata

            return [
                TextContent(
                    type="text",
                    text=f"Successfully sampled dataset '{dataset_name}' → '{output_name}'\n"
                    f"Original size: {len(df):,} rows\n"
                    f"Sample size: {len(sampled_df):,} rows ({len(sampled_df)/len(df)*100:.1f}%)\n"
                    f"Sampling method: {method}\n"
                    f"Columns: {len(sampled_df.columns)}",
                )
            ]

        except Exception as e:
            self.logger.error(f"Error sampling dataset: {str(e)}")
            error_result = {
                "status": "error",
                "operation": "sample_dataset",
                "message": f"Error sampling dataset: {str(e)}"
            }
            return self._create_json_response(error_result)

    async def _handle_compare_datasets(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle dataset comparison."""
        try:
            dataset1_name = arguments.get("dataset1_name")
            dataset2_name = arguments.get("dataset2_name")

            if dataset1_name not in self.datasets:
                return [
                    TextContent(
                        type="text", text=f"Dataset '{dataset1_name}' not found."
                    )
                ]
            if dataset2_name not in self.datasets:
                return [
                    TextContent(
                        type="text", text=f"Dataset '{dataset2_name}' not found."
                    )
                ]

            df1 = self.datasets[dataset1_name]
            df2 = self.datasets[dataset2_name]

            comparison_type = arguments.get("comparison_type", "structure")

            if comparison_type == "structure":
                # Compare structure and basic statistics
                comparison = {
                    "shape_comparison": {
                        dataset1_name: df1.shape,
                        dataset2_name: df2.shape,
                    },
                    "columns_comparison": {
                        "common_columns": list(set(df1.columns) & set(df2.columns)),
                        "only_in_dataset1": list(set(df1.columns) - set(df2.columns)),
                        "only_in_dataset2": list(set(df2.columns) - set(df1.columns)),
                    },
                }

                # Check for data type mismatches in common columns
                dtype_mismatches = []
                for col in comparison["columns_comparison"]["common_columns"]:
                    if str(df1[col].dtype) != str(df2[col].dtype):
                        dtype_mismatches.append(
                            {
                                "column": col,
                                dataset1_name: str(df1[col].dtype),
                                dataset2_name: str(df2[col].dtype),
                            }
                        )
                comparison["dtype_mismatches"] = dtype_mismatches

                result_text = (
                    f"Dataset Comparison Report: {dataset1_name} vs {dataset2_name}\n\n"
                )
                result_text += f"Shape Comparison:\n"
                result_text += f"  {dataset1_name}: {df1.shape}\n"
                result_text += f"  {dataset2_name}: {df2.shape}\n\n"
                result_text += f"Column Comparison:\n"
                result_text += f"  Common columns ({len(comparison['columns_comparison']['common_columns'])}): {comparison['columns_comparison']['common_columns']}\n"
                result_text += f"  Only in {dataset1_name} ({len(comparison['columns_comparison']['only_in_dataset1'])}): {comparison['columns_comparison']['only_in_dataset1']}\n"
                result_text += f"  Only in {dataset2_name} ({len(comparison['columns_comparison']['only_in_dataset2'])}): {comparison['columns_comparison']['only_in_dataset2']}\n\n"

                if dtype_mismatches:
                    result_text += f"Data Type Mismatches:\n"
                    for mismatch in dtype_mismatches:
                        result_text += f"  {mismatch['column']}: {mismatch[dataset1_name]} vs {mismatch[dataset2_name]}\n"
                else:
                    result_text += "No data type mismatches found in common columns.\n"

            elif comparison_type == "statistics":
                # Compare statistical properties for common numeric columns
                common_cols = list(set(df1.columns) & set(df2.columns))
                numeric_cols = [
                    col
                    for col in common_cols
                    if pd.api.types.is_numeric_dtype(df1[col])
                    and pd.api.types.is_numeric_dtype(df2[col])
                ]

                if not numeric_cols:
                    return [
                        TextContent(
                            type="text",
                            text="No common numeric columns found for statistical comparison.",
                        )
                    ]

                stats_comparison = {}
                for col in numeric_cols:
                    stats_comparison[col] = {
                        dataset1_name: {
                            "mean": df1[col].mean(),
                            "std": df1[col].std(),
                            "min": df1[col].min(),
                            "max": df1[col].max(),
                            "median": df1[col].median(),
                        },
                        dataset2_name: {
                            "mean": df2[col].mean(),
                            "std": df2[col].std(),
                            "min": df2[col].min(),
                            "max": df2[col].max(),
                            "median": df2[col].median(),
                        },
                    }

                result_text = f"Statistical Comparison Report: {dataset1_name} vs {dataset2_name}\n\n"
                for col in numeric_cols:
                    result_text += f"Column: {col}\n"
                    result_text += f"  {dataset1_name} - Mean: {stats_comparison[col][dataset1_name]['mean']:.3f}, Std: {stats_comparison[col][dataset1_name]['std']:.3f}\n"
                    result_text += f"  {dataset2_name} - Mean: {stats_comparison[col][dataset2_name]['mean']:.3f}, Std: {stats_comparison[col][dataset2_name]['std']:.3f}\n"
                    result_text += f"  Mean Difference: {abs(stats_comparison[col][dataset1_name]['mean'] - stats_comparison[col][dataset2_name]['mean']):.3f}\n\n"

            else:
                return [
                    TextContent(
                        type="text", text=f"Unknown comparison type: {comparison_type}"
                    )
                ]

            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            self.logger.error(f"Error comparing datasets: {str(e)}")
            return [
                TextContent(type="text", text=f"Error comparing datasets: {str(e)}")
            ]

    async def _handle_batch_process_datasets(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle batch processing of multiple datasets."""
        try:
            dataset_names = arguments.get("dataset_names", [])
            operation = arguments.get("operation")
            operation_config = arguments.get("operation_config", {})

            if not dataset_names:
                return [
                    TextContent(
                        type="text", text="No datasets specified for batch processing."
                    )
                ]

            # Validate all datasets exist
            missing_datasets = [
                name for name in dataset_names if name not in self.datasets
            ]
            if missing_datasets:
                return [
                    TextContent(
                        type="text", text=f"Datasets not found: {missing_datasets}"
                    )
                ]

            results = []
            successful = 0
            failed = 0

            for dataset_name in dataset_names:
                try:
                    if operation == "validate":
                        # Batch validation
                        validation_args = {"dataset_name": dataset_name}
                        validation_args.update(operation_config)
                        result = await self._handle_validate_dataset(validation_args)
                        results.append(f"✅ {dataset_name}: Validation completed")
                        successful += 1

                    elif operation == "profile":
                        # Batch profiling
                        profile_args = {"dataset_name": dataset_name}
                        profile_args.update(operation_config)
                        result = await self._handle_profile_dataset(profile_args)
                        results.append(f"✅ {dataset_name}: Profiling completed")
                        successful += 1

                    elif operation == "clean":
                        # Batch cleaning
                        clean_args = {
                            "dataset_name": dataset_name,
                            "output_name": f"{dataset_name}_clean",
                        }
                        clean_args.update(operation_config)
                        result = await self._handle_clean_dataset(clean_args)
                        results.append(
                            f"✅ {dataset_name}: Cleaning completed → {dataset_name}_clean"
                        )
                        successful += 1

                    elif operation == "sample":
                        # Batch sampling
                        sample_args = {
                            "dataset_name": dataset_name,
                            "output_name": f"{dataset_name}_sample",
                        }
                        sample_args.update(operation_config)
                        result = await self._handle_sample_dataset(sample_args)
                        results.append(
                            f"✅ {dataset_name}: Sampling completed → {dataset_name}_sample"
                        )
                        successful += 1

                    else:
                        results.append(
                            f"❌ {dataset_name}: Unknown operation '{operation}'"
                        )
                        failed += 1

                except Exception as e:
                    results.append(f"❌ {dataset_name}: Error - {str(e)}")
                    failed += 1

            summary = f"Batch Processing Results\n"
            summary += f"Operation: {operation}\n"
            summary += f"Datasets processed: {len(dataset_names)}\n"
            summary += f"Successful: {successful}\n"
            summary += f"Failed: {failed}\n\n"
            summary += "Details:\n" + "\n".join(results)

            return [TextContent(type="text", text=summary)]

        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            return [
                TextContent(type="text", text=f"Error in batch processing: {str(e)}")
            ]


    async def _handle_remove_dataset(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Remove a dataset from memory and optionally delete files."""
        dataset_name = arguments["dataset_name"]
        delete_files = arguments.get("delete_files", False)
        
        try:
            removed_from_memory = False
            removed_files = []
            
            # Remove from memory registry
            if dataset_name in self.datasets:
                del self.datasets[dataset_name]
                removed_from_memory = True
                
            if dataset_name in self.dataset_metadata:
                del self.dataset_metadata[dataset_name]
                
            # Remove from artifact bridge if exists
            try:
                self.artifact_bridge.remove_artifact(dataset_name)
            except Exception:
                pass  # Continue even if artifact removal fails
                
            # Optionally delete files
            if delete_files:
                # Try to find and delete associated files
                import glob
                
                potential_files = [
                    f"{dataset_name}.*",
                    f"*{dataset_name}*",
                ]
                
                for pattern in potential_files:
                    matches = glob.glob(str(self.config.path_manager.workspace_dir / pattern))
                    for match in matches:
                        try:
                            Path(match).unlink()
                            removed_files.append(match)
                        except Exception:
                            continue
            
            removal_result = {
                "status": "success",
                "operation": "remove_dataset",
                "dataset_name": dataset_name,
                "removed_from_memory": removed_from_memory,
                "files_deleted": len(removed_files),
                "deleted_files": removed_files if delete_files else []
            }
            
            return self._create_json_response(removal_result)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "operation": "remove_dataset", 
                "message": f"Error removing dataset: {str(e)}"
            }
            return self._create_json_response(error_result)

    async def _handle_clear_all_data(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Clear all datasets and cached data from current session."""
        confirm = arguments.get("confirm", False)
        
        if not confirm:
            warning_result = {
                "status": "warning",
                "operation": "clear_all_data",
                "message": "This will remove ALL datasets from memory. Set confirm=true to proceed.",
                "datasets_count": len(self.datasets),
                "datasets": list(self.datasets.keys())
            }
            return self._create_json_response(warning_result)
        
        try:
            # Clear all datasets and metadata
            dataset_count = len(self.datasets)
            dataset_names = list(self.datasets.keys())
            
            self.datasets.clear()
            self.dataset_metadata.clear()
            
            # Clear artifact bridge (only datasets, not models)
            try:
                for key in list(self.artifact_bridge.list_artifacts().keys()):
                    if not key.endswith("_model"):  # Keep models, only clear datasets
                        self.artifact_bridge.remove_artifact(key)
            except Exception:
                pass  # Continue even if artifact clearing fails
            
            # Clear cache directories if they exist
            cache_dirs_cleared = 0
            cache_dir = self.config.path_manager.cache_dir
            if cache_dir.exists():
                import shutil
                try:
                    shutil.rmtree(cache_dir)
                    cache_dirs_cleared += 1
                except Exception:
                    pass
            
            clear_result = {
                "status": "success",
                "operation": "clear_all_data",
                "datasets_removed": dataset_count,
                "dataset_names": dataset_names,
                "cache_dirs_cleared": cache_dirs_cleared,
                "message": f"Successfully cleared {dataset_count} datasets from memory"
            }
            
            return self._create_json_response(clear_result)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "operation": "clear_all_data",
                "message": f"Error clearing data: {str(e)}"
            }
            return self._create_json_response(error_result)



