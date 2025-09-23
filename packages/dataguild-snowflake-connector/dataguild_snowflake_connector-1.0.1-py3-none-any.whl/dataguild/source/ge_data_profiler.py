"""
DataGuild Great Expectations Profiler

Enterprise-grade data profiler integrating Great Expectations with DataGuild's
metadata system for comprehensive data quality assessment and statistical profiling.
"""

import json
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Union
from dataclasses import dataclass
from contextlib import contextmanager

# DataGuild imports
from dataguild.api.workunit import MetadataWorkUnit
from dataguild.metadata.schemas import MetadataEvent, MetadataEventType, MetadataEventSeverity
from dataguild.utilities.perf_timer import PerfTimer

logger = logging.getLogger(__name__)

# ✅ FIXED: Corrected Great Expectations imports with proper fallback handling
try:
    import great_expectations as ge
    from great_expectations import DataContext
    from great_expectations.core.batch import RuntimeBatchRequest

    # ✅ FIX: Try multiple import paths for Validator (different GE versions)
    try:
        from great_expectations.validator.validator import Validator
    except ImportError:
        try:
            from great_expectations.validator import Validator
        except ImportError:
            from great_expectations.dataset import Dataset as Validator

    # ✅ FIX: Try multiple import paths for UserConfigurableProfiler
    try:
        from great_expectations.profile.user_configurable_profiler import UserConfigurableProfiler
    except ImportError:
        try:
            from great_expectations.profile.user_configurable import UserConfigurableProfiler
        except ImportError:
            from great_expectations.profile import UserConfigurableProfiler

    from great_expectations.exceptions import GreatExpectationsError

    GE_AVAILABLE = True
    logger.debug("Great Expectations successfully imported")

except ImportError as e:
    logger.warning(
        f"Great Expectations not available: {e}. "
        "Install with: pip install great-expectations. "
        "Profiling functionality will be limited."
    )
    GE_AVAILABLE = False

    # ✅ ADDED: Create placeholder classes when GE is not available
    class Validator:
        """Placeholder Validator class when Great Expectations is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Great Expectations not available")

    class UserConfigurableProfiler:
        """Placeholder UserConfigurableProfiler class when Great Expectations is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Great Expectations not available")


@dataclass
class ProfileResult:
    """Result of a profiling operation."""
    table_name: str
    schema_name: str
    database_name: str
    success: bool
    profile_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    expectations_count: int = 0
    columns_profiled: int = 0


class DataGuildGEProfiler:
    """
    DataGuild Great Expectations Profiler with comprehensive data quality assessment.

    This profiler integrates Great Expectations with DataGuild's metadata system
    to provide enterprise-grade data profiling capabilities including:
    - Statistical profiling of tables and columns
    - Data quality expectations generation and validation
    - Comprehensive metadata work unit generation
    - Event-driven monitoring and error handling
    """

    def __init__(
        self,
        conn: Any,
        report: Optional[Any] = None,
        config: Optional[Any] = None,
        platform: str = "unknown",
        data_context: Optional[Any] = None,
    ) -> None:
        """
        Initialize DataGuild Great Expectations profiler.

        Args:
            conn: Database connection or SQLAlchemy engine
            report: DataGuild report instance for tracking
            config: Profiling configuration
            platform: Data platform identifier (e.g., 'snowflake', 'postgres')
            data_context: Optional Great Expectations DataContext
        """
        self.conn = conn
        self.report = report
        self.config = config
        self.platform = platform

        # Performance and event tracking
        self.profiling_timer = PerfTimer("ge_profiling")
        self.events: List[MetadataEvent] = []

        # Great Expectations setup
        self.ge_available = GE_AVAILABLE
        self.data_context = data_context
        # ✅ FIXED: Use Optional type annotation and handle case when GE not available
        self.validator: Optional[Any] = None  # Changed from Optional[Validator] to Optional[Any]

        # Profiling state
        self.tables_profiled = 0
        self.tables_failed = 0
        self.total_expectations_generated = 0

        if not self.ge_available:
            logger.warning("Great Expectations not available - profiling will be limited")
        else:
            self._initialize_ge_context()

        logger.info(f"Initialized DataGuildGEProfiler for platform {platform}")

    def _emit_event(self, event: MetadataEvent) -> None:
        """Emit profiling event for monitoring and debugging."""
        self.events.append(event)

        if event.severity == MetadataEventSeverity.ERROR:
            logger.error(f"GE Profiling error: {event.message}")
        elif event.severity == MetadataEventSeverity.WARNING:
            logger.warning(f"GE Profiling warning: {event.message}")
        else:
            logger.debug(f"GE Profiling event: {event.message}")

    def _initialize_ge_context(self) -> None:
        """Initialize Great Expectations context."""
        if not self.ge_available:
            logger.warning("Cannot initialize GE context - Great Expectations not available")
            return

        try:
            if not self.data_context:
                # ✅ FIXED: Added version-specific context creation
                try:
                    # Try modern GE context creation
                    self.data_context = ge.get_context(mode="ephemeral")
                except Exception:
                    # Fallback for older versions
                    self.data_context = ge.DataContext()

            logger.debug("Great Expectations context initialized successfully")

        except Exception as e:
            error_msg = f"Failed to initialize Great Expectations context: {e}"

            error_event = MetadataEvent(
                event_type=MetadataEventType.VALIDATION_ERROR,
                timestamp=datetime.now(),
                source="ge_profiler",
                severity=MetadataEventSeverity.ERROR,
                message=error_msg,
                platform=self.platform
            )
            error_event.add_tag("initialization_error")
            self._emit_event(error_event)

            logger.error(error_msg)
            self.ge_available = False

    def profile_table(
        self,
        table_name: str,
        schema_name: str,
        database_name: str,
        batch_kwargs: Optional[Dict[str, Any]] = None,
        profile_options: Optional[Dict[str, Any]] = None
    ) -> ProfileResult:
        """
        Profile a single table using Great Expectations.

        Args:
            table_name: Name of the table to profile
            schema_name: Schema containing the table
            database_name: Database containing the table
            batch_kwargs: Additional batch configuration
            profile_options: Profiling configuration options

        Returns:
            ProfileResult with profiling outcomes
        """
        start_time = datetime.now()
        fully_qualified_name = f"{database_name}.{schema_name}.{table_name}"

        # Emit profiling start event
        start_event = MetadataEvent(
            event_type=MetadataEventType.DATA_PROFILING_STARTED,
            timestamp=start_time,
            source="ge_profiler",
            message=f"Starting profiling for table {fully_qualified_name}",
            platform=self.platform,
            payload={
                "table_name": table_name,
                "schema_name": schema_name,
                "database_name": database_name
            }
        )
        start_event.add_tag("table_profiling")
        self._emit_event(start_event)

        if not self.ge_available:
            error_msg = "Great Expectations not available for profiling"

            error_event = MetadataEvent(
                event_type=MetadataEventType.DATA_PROFILING_FAILED,
                timestamp=datetime.now(),
                source="ge_profiler",
                severity=MetadataEventSeverity.ERROR,
                message=error_msg,
                platform=self.platform
            )
            error_event.add_tag("ge_unavailable")
            self._emit_event(error_event)

            return ProfileResult(
                table_name=table_name,
                schema_name=schema_name,
                database_name=database_name,
                success=False,
                error_message=error_msg
            )

        try:
            with self.profiling_timer:
                # Create batch request
                batch_request = self._create_batch_request(
                    table_name, schema_name, database_name, batch_kwargs
                )

                # Get validator
                validator = self._get_validator(batch_request)

                # Run profiling
                profile_data = self._run_profiling(
                    validator, fully_qualified_name, profile_options or {}
                )

                # Calculate metrics
                duration_ms = int(self.profiling_timer.elapsed_seconds() * 1000)
                expectations_count = len(profile_data.get("expectations", []))
                columns_profiled = len(profile_data.get("columns", {}))

                # Update counters
                self.tables_profiled += 1
                self.total_expectations_generated += expectations_count

                # Emit completion event
                completion_event = MetadataEvent(
                    event_type=MetadataEventType.DATA_PROFILING_COMPLETED,
                    timestamp=datetime.now(),
                    source="ge_profiler",
                    message=f"Completed profiling for table {fully_qualified_name}",
                    platform=self.platform,
                    duration_ms=duration_ms,
                    payload={
                        "expectations_count": expectations_count,
                        "columns_profiled": columns_profiled
                    }
                )
                completion_event.add_tag("profiling_success")
                self._emit_event(completion_event)

                logger.info(
                    f"Successfully profiled {fully_qualified_name}: "
                    f"{expectations_count} expectations, {columns_profiled} columns, "
                    f"{duration_ms}ms"
                )

                return ProfileResult(
                    table_name=table_name,
                    schema_name=schema_name,
                    database_name=database_name,
                    success=True,
                    profile_data=profile_data,
                    duration_ms=duration_ms,
                    expectations_count=expectations_count,
                    columns_profiled=columns_profiled
                )

        except Exception as e:
            error_msg = f"Error profiling table {fully_qualified_name}: {e}"

            # Emit error event
            error_event = MetadataEvent(
                event_type=MetadataEventType.DATA_PROFILING_FAILED,
                timestamp=datetime.now(),
                source="ge_profiler",
                severity=MetadataEventSeverity.ERROR,
                message=error_msg,
                platform=self.platform,
                stack_trace=traceback.format_exc()
            )
            error_event.add_tag("profiling_error")
            self._emit_event(error_event)

            # Update counters
            self.tables_failed += 1

            # Update report if available
            if self.report and hasattr(self.report, 'report_failure'):
                self.report.report_failure(schema_name, table_name, str(e))

            logger.error(error_msg, exc_info=True)

            return ProfileResult(
                table_name=table_name,
                schema_name=schema_name,
                database_name=database_name,
                success=False,
                error_message=str(e)
            )

    def _create_batch_request(
        self,
        table_name: str,
        schema_name: str,
        database_name: str,
        batch_kwargs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create batch request for Great Expectations."""
        # Build base batch request
        base_request = {
            "datasource_name": "default_datasource",
            "data_connector_name": "default_data_connector",
            "data_asset_name": f"{database_name}.{schema_name}.{table_name}",
        }

        # Add custom batch kwargs if provided
        if batch_kwargs:
            # Handle custom SQL queries
            if "custom_sql" in batch_kwargs:
                base_request["query"] = batch_kwargs["custom_sql"]

            # Handle quoted names for mixed-case tables
            if batch_kwargs.get("use_quoted_name", False):
                base_request["data_asset_name"] = f'"{database_name}"."{schema_name}"."{table_name}"'

            # Add other batch kwargs
            for key, value in batch_kwargs.items():
                if key not in ["custom_sql", "use_quoted_name"]:
                    base_request[key] = value

        return base_request

    # ✅ FIXED: Changed return type annotation from Validator to Any to avoid import issues
    def _get_validator(self, batch_request: Dict[str, Any]) -> Any:
        """Get Great Expectations validator for the batch."""
        if not self.ge_available:
            raise ImportError("Great Expectations not available")

        try:
            # Create datasource if it doesn't exist
            if not hasattr(self, '_datasource_created'):
                self._ensure_datasource()
                self._datasource_created = True

            # ✅ FIXED: Handle different GE versions for getting batch
            try:
                # Try modern batch creation
                batch = self.data_context.get_batch(batch_request)
            except Exception:
                # Fallback for older versions
                batch = self.data_context.get_batch(**batch_request)

            # ✅ FIXED: Handle different GE versions for getting validator
            try:
                # Try modern validator creation
                validator = self.data_context.get_validator(
                    batch_request=batch_request,
                    expectation_suite_name="profiling_suite"
                )
            except Exception:
                # Fallback - create validator directly from batch
                validator = batch

            return validator

        except Exception as e:
            logger.error(f"Error creating validator: {e}")
            raise

    def _ensure_datasource(self) -> None:
        """Ensure datasource exists in Great Expectations context."""
        if not self.ge_available:
            return

        try:
            # ✅ FIXED: Updated datasource configuration for different GE versions
            datasource_config = {
                "name": "default_datasource",
                "class_name": "Datasource",
                "execution_engine": {
                    "class_name": "SqlAlchemyExecutionEngine",
                    "connection_string": str(self.conn.url) if hasattr(self.conn, 'url') else None,
                    "create_temp_table": False,
                },
                "data_connectors": {
                    "default_data_connector": {
                        "class_name": "RuntimeDataConnector",
                        "batch_identifiers": ["default_identifier_name"],
                    }
                }
            }

            # Add datasource to context
            try:
                self.data_context.add_datasource(**datasource_config)
            except Exception:
                # Try alternative method for older versions
                self.data_context.add_datasource(datasource_config["name"], **datasource_config)

        except Exception as e:
            # Datasource might already exist
            logger.debug(f"Datasource creation note: {e}")

    # ✅ FIXED: Changed parameter type annotation from Validator to Any
    def _run_profiling(
        self,
        validator: Any,  # Changed from Validator to Any
        table_name: str,
        profile_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run comprehensive profiling using Great Expectations."""
        if not self.ge_available:
            raise ImportError("Great Expectations not available")

        try:
            # ✅ FIXED: Handle UserConfigurableProfiler creation with error handling
            try:
                # Create profiler with custom configuration
                profiler = UserConfigurableProfiler(
                    profile_dataset=validator,
                    excluded_expectations=profile_options.get("excluded_expectations", []),
                    ignored_columns=profile_options.get("ignored_columns", []),
                    not_null_only=profile_options.get("not_null_only", False),
                    primary_or_compound_key=profile_options.get("primary_or_compound_key", []),
                    semantic_types_dict=profile_options.get("semantic_types_dict", {}),
                    table_expectations_only=profile_options.get("table_expectations_only", False),
                    value_set_threshold=profile_options.get("value_set_threshold", "MANY")
                )
            except Exception as e:
                logger.warning(f"Could not create UserConfigurableProfiler: {e}")
                # Return basic profile data without advanced profiling
                return {
                    "table_name": table_name,
                    "expectations": [],
                    "validation_results": {},
                    "columns": self._extract_column_statistics(validator),
                    "row_count": self._get_row_count(validator),
                    "table_statistics": self._get_table_statistics(validator),
                    "profiling_timestamp": datetime.now().isoformat(),
                    "profiler_version": ge.__version__ if GE_AVAILABLE else "unknown",
                    "error": f"Basic profiling only: {e}"
                }

            # Build expectation suite
            suite = profiler.build_suite()

            # Run validation to get results
            results = validator.validate(expectation_suite=suite)

            # Extract column-level statistics
            column_stats = self._extract_column_statistics(validator)

            # Build comprehensive profile data
            profile_data = {
                "table_name": table_name,
                "expectations": [exp.to_json_dict() for exp in suite.expectations],
                "validation_results": results.to_json_dict(),
                "columns": column_stats,
                "row_count": self._get_row_count(validator),
                "table_statistics": self._get_table_statistics(validator),
                "profiling_timestamp": datetime.now().isoformat(),
                "profiler_version": ge.__version__ if GE_AVAILABLE else "unknown"
            }

            return profile_data

        except Exception as e:
            logger.error(f"Error running profiling for {table_name}: {e}")
            raise

    # ✅ FIXED: Changed parameter type annotation from Validator to Any
    def _extract_column_statistics(self, validator: Any) -> Dict[str, Dict[str, Any]]:
        """Extract detailed column statistics."""
        column_stats = {}

        try:
            # Get basic column info
            columns = validator.get_metric(
                metric_name="table.columns",
                metric_domain_kwargs={}
            )

            for column in columns:
                try:
                    stats = {
                        "column_name": column,
                        "data_type": None,
                        "null_count": None,
                        "null_percentage": None,
                        "distinct_count": None,
                        "min_value": None,
                        "max_value": None,
                        "mean_value": None,
                        "median_value": None,
                        "std_dev": None,
                    }

                    # Get column type
                    try:
                        column_type = validator.get_metric(
                            metric_name="column.type_list",
                            metric_domain_kwargs={"column": column}
                        )
                        stats["data_type"] = str(column_type[0]) if column_type else "unknown"
                    except:
                        pass

                    # Get null count and percentage
                    try:
                        null_count = validator.get_metric(
                            metric_name="column_values.null.count",
                            metric_domain_kwargs={"column": column}
                        )
                        stats["null_count"] = null_count

                        total_count = validator.get_metric(
                            metric_name="column.count",
                            metric_domain_kwargs={"column": column}
                        )
                        if total_count and total_count > 0:
                            stats["null_percentage"] = (null_count / total_count) * 100
                    except:
                        pass

                    # Get distinct count
                    try:
                        distinct_count = validator.get_metric(
                            metric_name="column.distinct_values.count",
                            metric_domain_kwargs={"column": column}
                        )
                        stats["distinct_count"] = distinct_count
                    except:
                        pass

                    # Get min/max for applicable types
                    try:
                        min_value = validator.get_metric(
                            metric_name="column.min",
                            metric_domain_kwargs={"column": column}
                        )
                        stats["min_value"] = min_value

                        max_value = validator.get_metric(
                            metric_name="column.max",
                            metric_domain_kwargs={"column": column}
                        )
                        stats["max_value"] = max_value
                    except:
                        pass

                    # Get mean for numeric columns
                    try:
                        mean_value = validator.get_metric(
                            metric_name="column.mean",
                            metric_domain_kwargs={"column": column}
                        )
                        stats["mean_value"] = mean_value
                    except:
                        pass

                    # Get median for numeric columns
                    try:
                        median_value = validator.get_metric(
                            metric_name="column.median",
                            metric_domain_kwargs={"column": column}
                        )
                        stats["median_value"] = median_value
                    except:
                        pass

                    # Get standard deviation for numeric columns
                    try:
                        std_dev = validator.get_metric(
                            metric_name="column.standard_deviation",
                            metric_domain_kwargs={"column": column}
                        )
                        stats["std_dev"] = std_dev
                    except:
                        pass

                    column_stats[column] = stats

                except Exception as e:
                    logger.debug(f"Error getting statistics for column {column}: {e}")
                    column_stats[column] = {"column_name": column, "error": str(e)}

        except Exception as e:
            logger.error(f"Error extracting column statistics: {e}")

        return column_stats

    # ✅ FIXED: Changed parameter type annotation from Validator to Any
    def _get_row_count(self, validator: Any) -> Optional[int]:
        """Get table row count."""
        try:
            return validator.get_metric(
                metric_name="table.row_count",
                metric_domain_kwargs={}
            )
        except Exception as e:
            logger.debug(f"Error getting row count: {e}")
            return None

    # ✅ FIXED: Changed parameter type annotation from Validator to Any
    def _get_table_statistics(self, validator: Any) -> Dict[str, Any]:
        """Get table-level statistics."""
        stats = {}

        try:
            # Get column count
            columns = validator.get_metric(
                metric_name="table.columns",
                metric_domain_kwargs={}
            )
            stats["column_count"] = len(columns) if columns else 0

            # Get table head for sample data
            try:
                head = validator.get_metric(
                    metric_name="table.head",
                    metric_domain_kwargs={},
                    metric_value_kwargs={"n_rows": 5}
                )
                stats["sample_rows"] = head.to_dict("records") if head is not None else []
            except:
                stats["sample_rows"] = []

        except Exception as e:
            logger.debug(f"Error getting table statistics: {e}")

        return stats

    def generate_work_units(
        self,
        profile_results: List[ProfileResult]
    ) -> Iterable[MetadataWorkUnit]:
        """
        Generate DataGuild metadata work units from profiling results.

        Args:
            profile_results: List of profiling results

        Yields:
            MetadataWorkUnit instances for each profiling result
        """
        for result in profile_results:
            try:
                if result.success and result.profile_data:
                    # Create work unit for successful profiling
                    work_unit = self._create_profiling_work_unit(result)
                    if work_unit:
                        yield work_unit

                        logger.debug(
                            f"Generated work unit for {result.database_name}."
                            f"{result.schema_name}.{result.table_name}"
                        )
                else:
                    # Log failed profiling
                    logger.warning(
                        f"Skipping work unit generation for failed profiling: "
                        f"{result.database_name}.{result.schema_name}.{result.table_name} - "
                        f"{result.error_message}"
                    )

            except Exception as e:
                error_msg = (
                    f"Error generating work unit for "
                    f"{result.database_name}.{result.schema_name}.{result.table_name}: {e}"
                )

                error_event = MetadataEvent(
                    event_type=MetadataEventType.VALIDATION_ERROR,
                    timestamp=datetime.now(),
                    source="ge_profiler",
                    severity=MetadataEventSeverity.ERROR,
                    message=error_msg,
                    platform=self.platform
                )
                error_event.add_tag("work_unit_error")
                self._emit_event(error_event)

                logger.error(error_msg, exc_info=True)

    def _create_profiling_work_unit(self, result: ProfileResult) -> Optional[MetadataWorkUnit]:
        """Create MetadataWorkUnit from profiling result."""
        try:
            # Build work unit metadata
            work_unit_metadata = {
                "table_name": result.table_name,
                "schema_name": result.schema_name,
                "database_name": result.database_name,
                "platform": self.platform,
                "profiling_timestamp": datetime.now().isoformat(),
                "duration_ms": result.duration_ms,
                "expectations_count": result.expectations_count,
                "columns_profiled": result.columns_profiled,
                "profile_data": result.profile_data
            }

            # Create work unit (this would integrate with DataGuild's actual MetadataWorkUnit)
            work_unit = MetadataWorkUnit(
                id=f"profile_{result.database_name}_{result.schema_name}_{result.table_name}",
                metadata=work_unit_metadata
            )

            return work_unit

        except Exception as e:
            logger.error(f"Error creating profiling work unit: {e}")
            return None

    def get_profiling_summary(self) -> Dict[str, Any]:
        """Get comprehensive profiling summary."""
        return {
            "platform": self.platform,
            "ge_available": self.ge_available,
            "tables_profiled": self.tables_profiled,
            "tables_failed": self.tables_failed,
            "total_expectations_generated": self.total_expectations_generated,
            "success_rate": (
                (self.tables_profiled / (self.tables_profiled + self.tables_failed)) * 100
                if (self.tables_profiled + self.tables_failed) > 0 else 0
            ),
            "total_processing_time_seconds": self.profiling_timer.elapsed_seconds(),
            "events_generated": len(self.events),
            "error_events": len([e for e in self.events if e.severity == MetadataEventSeverity.ERROR]),
            "warning_events": len([e for e in self.events if e.severity == MetadataEventSeverity.WARNING]),
        }

    def get_events(self) -> List[MetadataEvent]:
        """Get all profiling events."""
        return self.events.copy()

    def clear_events(self) -> None:
        """Clear profiling events to free memory."""
        self.events.clear()

    @contextmanager
    def profiling_context(self, operation_name: str):
        """Context manager for profiling operations with event tracking."""
        start_time = datetime.now()

        start_event = MetadataEvent(
            event_type=MetadataEventType.DATA_PROFILING_STARTED,
            timestamp=start_time,
            source="ge_profiler",
            message=f"Starting {operation_name}",
            platform=self.platform
        )
        start_event.add_tag("profiling_context")
        self._emit_event(start_event)

        try:
            yield

            # Success event
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            success_event = MetadataEvent(
                event_type=MetadataEventType.DATA_PROFILING_COMPLETED,
                timestamp=datetime.now(),
                source="ge_profiler",
                message=f"Completed {operation_name}",
                platform=self.platform,
                duration_ms=duration_ms
            )
            success_event.add_tag("profiling_context")
            self._emit_event(success_event)

        except Exception as e:
            # Error event
            error_event = MetadataEvent(
                event_type=MetadataEventType.DATA_PROFILING_FAILED,
                timestamp=datetime.now(),
                source="ge_profiler",
                severity=MetadataEventSeverity.ERROR,
                message=f"Failed {operation_name}: {e}",
                platform=self.platform,
                stack_trace=traceback.format_exc()
            )
            error_event.add_tag("profiling_context")
            self._emit_event(error_event)
            raise


# Export main class
__all__ = [
    'DataGuildGEProfiler',
    'ProfileResult'
]
