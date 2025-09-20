"""Standalone History server for DataBeak using FastMCP server composition.

This module provides a complete History management server implementation following DataBeak's
modular server architecture pattern. It focuses on operation history tracking, undo/redo
functionality, and auto-save management with robust session lifecycle integration.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Import session management from the main package
from ..exceptions import SessionNotFoundError
from ..models import get_session_manager


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert object to int."""
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """Safely convert object to str."""
    try:
        return str(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def safe_bool(value: Any, *, default: bool = False) -> bool:
    """Safely convert object to bool."""
    try:
        return bool(value) if value is not None else default
    except (TypeError, ValueError):
        return default


logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class HistoryOperation(BaseModel):
    """Individual history operation details."""

    model_config = ConfigDict(extra="forbid")

    operation_id: str = Field(description="Unique identifier for this operation")
    operation_type: str = Field(
        description="Type of operation performed (load, filter, sort, etc.)",
    )
    timestamp: str = Field(description="When the operation was performed (ISO format)")
    description: str = Field(description="Human-readable description of the operation")
    can_undo: bool = Field(description="Whether this operation can be undone")
    can_redo: bool = Field(description="Whether this operation can be redone")


class HistorySummary(BaseModel):
    """Summary of operation history."""

    model_config = ConfigDict(extra="forbid")

    total_operations: int = Field(ge=0, description="Total number of operations in history")
    can_undo: bool = Field(description="Whether any operations can be undone")
    can_redo: bool = Field(description="Whether any operations can be redone")
    current_position: int = Field(ge=0, description="Current position in the operation history")
    history_enabled: bool = Field(description="Whether history tracking is enabled")


class AutoSaveConfig(BaseModel):
    """Auto-save configuration details."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(description="Whether auto-save is enabled")
    mode: Literal["disabled", "after_operation", "periodic", "hybrid"] = Field(
        description="Auto-save trigger mode",
    )
    strategy: Literal["overwrite", "backup", "versioned", "custom"] = Field(
        description="File saving strategy",
    )
    interval_seconds: int | None = Field(
        None,
        description="Interval between periodic saves (seconds)",
    )
    max_backups: int | None = Field(
        default=None,
        description="Maximum number of backup files to keep",
    )
    backup_dir: str | None = Field(default=None, description="Directory for backup files")
    custom_path: str | None = Field(default=None, description="Custom file path for saves")
    format: Literal["csv", "tsv", "json", "excel", "parquet"] = Field(
        "csv",
        description="Export format for saved files",
    )
    encoding: str = Field(default="utf-8", description="Text encoding for saved files")

    @field_validator("interval_seconds")
    @classmethod
    def validate_interval(cls, v: int | None) -> int | None:
        """Validate interval is reasonable for periodic saves."""
        if v is not None and v < 30:
            msg = "Interval must be at least 30 seconds for stability"
            raise ValueError(msg)
        return v

    @field_validator("max_backups")
    @classmethod
    def validate_max_backups(cls, v: int | None) -> int | None:
        """Validate max_backups is reasonable."""
        if v is not None and v < 1:
            msg = "Maximum backups must be at least 1"
            raise ValueError(msg)
        return v


class AutoSaveStatus(BaseModel):
    """Auto-save status information."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(description="Whether auto-save is currently enabled")
    config: AutoSaveConfig | None = Field(
        default=None,
        description="Current auto-save configuration",
    )
    last_save_time: str | None = Field(
        default=None,
        description="Timestamp of last save (ISO format)",
    )
    save_count: int = Field(default=0, description="Total number of saves performed")
    last_save_path: str | None = Field(
        default=None,
        description="Path of the most recent save file",
    )
    next_scheduled_save: str | None = Field(
        None,
        description="Timestamp of next scheduled save (ISO format)",
    )


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class UndoResult(BaseModel):
    """Response model for undo operations."""

    success: bool = Field(default=True, description="Whether the undo operation was successful")
    operation_undone: str | None = Field(
        default=None,
        description="Type of operation that was undone",
    )
    previous_operation: str | None = Field(
        default=None,
        description="Previous operation in history",
    )
    can_undo_more: bool = Field(default=False, description="Whether more operations can be undone")
    can_redo: bool = Field(default=False, description="Whether any operations can be redone")
    history_position: int = Field(default=0, description="Current position in operation history")


class RedoResult(BaseModel):
    """Response model for redo operations."""

    success: bool = Field(default=True, description="Whether the redo operation was successful")
    operation_redone: str | None = Field(
        default=None,
        description="Type of operation that was redone",
    )
    next_operation: str | None = Field(default=None, description="Next operation in history")
    can_undo: bool = Field(default=False, description="Whether any operations can be undone")
    can_redo_more: bool = Field(default=False, description="Whether more operations can be redone")
    history_position: int = Field(default=0, description="Current position in operation history")


class HistoryResult(BaseModel):
    """Response model for history retrieval operations."""

    success: bool = Field(default=True, description="Whether the history retrieval was successful")
    operations: list[HistoryOperation] = Field(
        default_factory=list,
        description="List of history operations",
    )
    summary: HistorySummary = Field(description="Summary of operation history")
    total_found: int = Field(default=0, description="Total number of operations found")
    limit_applied: int | None = Field(
        default=None,
        description="Maximum number of operations returned",
    )


class RestoreResult(BaseModel):
    """Response model for restore operations."""

    success: bool = Field(default=True, description="Whether the restore operation was successful")
    restored_to_operation: str | None = Field(
        default=None,
        description="Operation ID that was restored to",
    )
    operations_undone: int = Field(default=0, description="Number of operations that were undone")
    operations_redone: int = Field(default=0, description="Number of operations that were redone")
    final_position: int = Field(default=0, description="Final position in operation history")


class ClearHistoryResult(BaseModel):
    """Response model for clear history operations."""

    success: bool = Field(default=True, description="Whether the clear operation was successful")
    operations_cleared: int = Field(default=0, description="Number of operations that were cleared")
    history_was_enabled: bool = Field(
        default=True,
        description="Whether history was enabled before clearing",
    )


class ExportHistoryResult(BaseModel):
    """Response model for history export operations."""

    success: bool = Field(default=True, description="Whether the export was successful")
    file_path: str = Field(description="Path to the exported history file")
    format: Literal["json", "csv"] = Field(default="json", description="Format used for export")
    operations_exported: int = Field(default=0, description="Number of operations exported")
    file_size_bytes: int | None = Field(default=None, description="Size of exported file in bytes")


class AutoSaveConfigResult(BaseModel):
    """Response model for auto-save configuration operations."""

    success: bool = Field(
        default=True,
        description="Whether the configuration update was successful",
    )
    config: AutoSaveConfig = Field(description="New auto-save configuration")
    previous_config: AutoSaveConfig | None = Field(
        None,
        description="Previous auto-save configuration",
    )
    config_changed: bool = Field(
        default=True,
        description="Whether the configuration actually changed",
    )


class AutoSaveStatusResult(BaseModel):
    """Response model for auto-save status operations."""

    success: bool = Field(default=True, description="Whether the status retrieval was successful")
    status: AutoSaveStatus = Field(description="Current auto-save status information")


class AutoSaveDisableResult(BaseModel):
    """Response model for auto-save disable operations."""

    success: bool = Field(default=True, description="Whether the disable operation was successful")
    was_enabled: bool = Field(
        default=False,
        description="Whether auto-save was enabled before disabling",
    )
    final_save_performed: bool = Field(
        default=False,
        description="Whether a final save was performed before disabling",
    )
    final_save_path: str | None = Field(
        default=None,
        description="Path of final save file if performed",
    )


class ManualSaveResult(BaseModel):
    """Response model for manual save operations."""

    success: bool = Field(default=True, description="Whether the manual save was successful")
    save_path: str = Field(description="Path where the data was saved")
    format: str = Field(default="csv", description="Format used for saving")
    rows_saved: int = Field(default=0, description="Number of rows saved")
    columns_saved: int = Field(default=0, description="Number of columns saved")
    file_size_bytes: int | None = Field(default=None, description="Size of saved file in bytes")
    save_time: str | None = Field(
        None,
        description="Timestamp when save was completed (ISO format)",
    )


# ============================================================================
# HISTORY OPERATIONS LOGIC
# ============================================================================


async def undo_operation(
    ctx: Annotated[Context, Field(description="FastMCP context for session access")],
) -> UndoResult:
    """Undo the last operation in a session.

    Reverts the most recent data manipulation operation and restores the DataFrame
    to its previous state. Essential for data exploration workflows where users
    need to experiment with transformations safely.

    Args:
        ctx: FastMCP context for session access

    Returns:
        Detailed result of the undo operation including new history state

    Undo Process:
        🔄 State Restoration: Reverts DataFrame to previous snapshot
        📝 History Update: Updates current position in operation history
        🔍 Validation: Ensures data integrity after restoration
        ⚡ Performance: Optimized for quick state switching

    Examples:
        # Undo the last transformation
        result = await undo_operation("session_123")

        # Check what can be undone next
        if result.can_undo_more:
            next_undo = await undo_operation("session_123")

    AI Workflow Integration:
        1. Safe data exploration with immediate rollback capability
        2. Iterative analysis with confidence to experiment
        3. Error recovery when transformations produce unexpected results
        4. Comparison workflows (apply → analyze → undo → try alternative)
    """
    try:
        # Get session_id from FastMCP context
        session_id = ctx.session_id

        manager = get_session_manager()
        session = manager.get_or_create_session(session_id)

        if not session:
            raise SessionNotFoundError(session_id)

        await ctx.info(f"Performing undo operation for session {session_id}")

        result = await session.undo()

        if not result["success"]:
            msg = f"Undo operation failed: {result.get('error', 'Unknown error')}"
            raise ToolError(msg)

        # Extract history information
        history_info = session.get_history()
        can_undo = history_info.get("can_undo", False)
        can_redo = history_info.get("can_redo", False)
        position = history_info.get("current_position", 0)

        await ctx.info(f"Successfully undid operation: {result.get('message', 'Operation undone')}")

        return UndoResult(
            operation_undone=result.get("operation_type"),
            previous_operation=safe_str(result.get("previous_operation"))
            if result.get("previous_operation")
            else None,
            can_undo_more=safe_bool(can_undo),
            can_redo=safe_bool(can_redo),
            history_position=safe_int(position),
        )

    except SessionNotFoundError as e:
        logger.error("Undo operation failed: %s", e.message)
        raise ToolError(e.message) from e
    except ToolError:
        raise
    except Exception as e:
        logger.error("Error in undo operation: %s", str(e))
        await ctx.error(f"Failed to undo operation: {e!s}")
        msg = f"Error performing undo operation: {e}"
        raise ToolError(msg) from e


async def redo_operation(
    ctx: Annotated[Context, Field(description="FastMCP context for session access")],
) -> RedoResult:
    """Redo a previously undone operation.

    Reapplies an operation that was previously undone, moving forward in the
    operation history. Enables flexible navigation through the data transformation
    timeline for optimal workflow experimentation.

    Args:
        ctx: FastMCP context for session access

    Returns:
        Detailed result of the redo operation including new history state

    Redo Process:
        🔄 State Reapplication: Reapplies the next operation in history
        📝 History Navigation: Moves forward in operation timeline
        🔍 Consistency: Maintains data integrity through state transitions
        ⚡ Efficiency: Quick restoration of previously computed states

    Examples:
        # Redo the last undone operation
        result = await redo_operation("session_123")

        # Navigate through multiple redos
        if result.can_redo_more:
            next_redo = await redo_operation("session_123")

    AI Workflow Integration:
        1. Timeline navigation for data transformation workflows
        2. A/B testing scenarios (apply → undo → try alternative → redo original)
        3. Step-by-step analysis building (undo to checkpoint → redo with confidence)
        4. Collaborative workflows where multiple paths are explored
    """
    try:
        # Get session_id from FastMCP context
        session_id = ctx.session_id

        manager = get_session_manager()
        session = manager.get_or_create_session(session_id)

        if not session:
            raise SessionNotFoundError(session_id)

        await ctx.info(f"Performing redo operation for session {session_id}")

        result = await session.redo()

        if not result["success"]:
            msg = f"Redo operation failed: {result.get('error', 'Unknown error')}"
            raise ToolError(msg)

        # Extract history information
        history_info = session.get_history()
        can_undo = history_info.get("can_undo", False)
        can_redo = history_info.get("can_redo", False)
        position = history_info.get("current_position", 0)

        await ctx.info(f"Successfully redid operation: {result.get('message', 'Operation redone')}")

        return RedoResult(
            operation_redone=result.get("operation_type"),
            next_operation=safe_str(result.get("next_operation"))
            if result.get("next_operation")
            else None,
            can_undo=safe_bool(can_undo),
            can_redo_more=safe_bool(can_redo),
            history_position=safe_int(position),
        )

    except SessionNotFoundError as e:
        logger.error("Redo operation failed: %s", e.message)
        raise ToolError(e.message) from e
    except ToolError:
        raise
    except Exception as e:
        logger.error("Error in redo operation: %s", str(e))
        await ctx.error(f"Failed to redo operation: {e!s}")
        msg = f"Error performing redo operation: {e}"
        raise ToolError(msg) from e


async def get_history(
    ctx: Annotated[Context, Field(description="FastMCP context for session access")],
    limit: Annotated[
        int | None,
        Field(description="Maximum number of operations to return (None = all)"),
    ] = None,
) -> HistoryResult:
    """Get comprehensive operation history for a session.

    Retrieves the complete timeline of data operations performed in the session,
    including metadata about each operation and current position in history.
    Essential for understanding data provenance and workflow documentation.

    Args:
        ctx: FastMCP context for session access
        limit: Maximum number of operations to return (default: all)

    Returns:
        Complete operation history with summary statistics and navigation info

    History Information:
        📋 Operation Log: Complete list of data transformations performed
        🕐 Timestamps: When each operation was executed
        🔍 Descriptions: Human-readable operation summaries
        📊 Summary Stats: Current position, undo/redo capabilities

    Examples:
        # Get complete history
        history = await get_history("session_123")

        # Get recent operations only
        recent = await get_history("session_123", limit=10)

        # Check current state
        if history.summary.can_undo:
            # Safe to undo operations

    AI Workflow Integration:
        1. Data provenance tracking for reproducible analysis
        2. Workflow documentation and audit trails
        3. Understanding transformation chains for optimization
        4. Debugging complex multi-step data processing pipelines
    """
    try:
        # Get session_id from FastMCP context
        session_id = ctx.session_id

        manager = get_session_manager()
        session = manager.get_or_create_session(session_id)

        if not session:
            raise SessionNotFoundError(session_id)

        await ctx.info(f"Retrieving operation history for session {session_id}")

        result = session.get_history(limit)

        if not result["success"]:
            msg = f"Failed to retrieve history: {result.get('error', 'Unknown error')}"
            raise ToolError(msg)

        # Convert operations to structured format
        operations = []
        if "history" in result:
            for op in result["history"]:
                operations.append(
                    HistoryOperation(
                        operation_id=safe_str(op.get("operation_id")),
                        operation_type=safe_str(op.get("operation_type", "unknown")),
                        timestamp=safe_str(op.get("timestamp")),
                        description=safe_str(op.get("description")),
                        can_undo=safe_bool(op.get("can_undo", False)),
                        can_redo=safe_bool(op.get("can_redo", False)),
                    ),
                )

        # Build summary
        summary = HistorySummary(
            total_operations=safe_int(result.get("total_operations", 0)),
            can_undo=safe_bool(result.get("can_undo", False)),
            can_redo=safe_bool(result.get("can_redo", False)),
            current_position=safe_int(result.get("current_position", 0)),
            history_enabled=safe_bool(result.get("history_enabled", True)),
        )

        await ctx.info(f"Retrieved {len(operations)} operations from history")

        return HistoryResult(
            operations=operations,
            summary=summary,
            total_found=len(operations),
            limit_applied=limit,
        )

    except SessionNotFoundError as e:
        logger.error("History retrieval failed: %s", e.message)
        raise ToolError(e.message) from e
    except ToolError:
        raise
    except Exception as e:
        logger.error("Error retrieving history: %s", str(e))
        await ctx.error(f"Failed to retrieve history: {e!s}")
        msg = f"Error retrieving operation history: {e}"
        raise ToolError(msg) from e


async def restore_to_operation(
    ctx: Annotated[Context, Field(description="FastMCP context for session access")],
    operation_id: Annotated[str, Field(description="ID of the operation to restore to")],
) -> RestoreResult:
    """Restore session data to a specific operation point.

    Navigates directly to a specific point in the operation history, potentially
    undoing or redoing multiple operations to reach the target state. Powerful
    for jumping to known good states or comparing results at different stages.

    Args:
        ctx: FastMCP context for session access
        operation_id: Target operation ID to restore to

    Returns:
        Detailed result of the restore operation including steps taken

    Restore Process:
        🎯 Target Navigation: Direct jump to specified operation state
        🔄 Multi-Step Processing: Handles multiple undo/redo operations as needed
        📝 Path Tracking: Records all intermediate steps taken
        ✅ State Validation: Ensures target state is correctly reached

    Examples:
        # Restore to a specific operation
        result = await restore_to_operation("session_123", "op_456")

        # Check how many steps were taken
        total_steps = result.operations_undone + result.operations_redone

    AI Workflow Integration:
        1. Checkpoint restoration for complex analysis workflows
        2. A/B testing by jumping between different analysis branches
        3. Error recovery to last known good state
        4. Comparative analysis at different transformation stages
    """
    try:
        # Get session_id from FastMCP context
        session_id = ctx.session_id

        manager = get_session_manager()
        session = manager.get_or_create_session(session_id)

        if not session:
            raise SessionNotFoundError(session_id)

        await ctx.info(f"Restoring session {session_id} to operation {operation_id}")

        result = await session.restore_to_operation(operation_id)

        if not result["success"]:
            msg = f"Restore operation failed: {result.get('error', 'Unknown error')}"
            raise ToolError(msg)

        await ctx.info(f"Successfully restored to operation {operation_id}")

        return RestoreResult(
            restored_to_operation=operation_id,
            operations_undone=safe_int(result.get("operations_undone", 0)),
            operations_redone=safe_int(result.get("operations_redone", 0)),
            final_position=safe_int(result.get("final_position", 0)),
        )

    except SessionNotFoundError as e:
        logger.error("Restore operation failed: %s", e.message)
        raise ToolError(e.message) from e
    except ToolError:
        raise
    except Exception as e:
        logger.error("Error in restore operation: %s", str(e))
        await ctx.error(f"Failed to restore to operation: {e!s}")
        msg = f"Error restoring to operation: {e}"
        raise ToolError(msg) from e


async def clear_history(
    ctx: Annotated[Context, Field(description="FastMCP context for session access")],
) -> ClearHistoryResult:
    """Clear all operation history for a session.

    Removes all stored operation history while preserving the current data state.
    Useful for starting fresh after completing a major workflow phase or when
    history storage becomes large. Current data remains unchanged.

    Args:
        ctx: FastMCP context for session access

    Returns:
        Result of the clear operation including count of operations removed

    Clear Process:
        🗑️ History Removal: Deletes all stored operation snapshots
        💾 Data Preservation: Current DataFrame state remains intact
        🔄 Fresh Start: Resets history tracking for new operations
        ⚡ Memory Recovery: Frees memory used by historical snapshots

    Examples:
        # Clear all history
        result = await clear_history("session_123")
        print(f"Cleared {result.operations_cleared} operations")

        # After clearing, no undo/redo is possible
        # But current data is preserved

    AI Workflow Integration:
        1. Workflow phase transitions (exploration → production)
        2. Memory management for long-running analysis sessions
        3. Clean slate for new team members joining analysis
        4. Performance optimization when history is no longer needed

    Warning:
        This operation cannot be undone. All ability to undo previous operations
        will be lost, though current data remains unchanged.
    """
    try:
        # Get session_id from FastMCP context
        session_id = ctx.session_id

        manager = get_session_manager()
        session = manager.get_or_create_session(session_id)

        if not session:
            raise SessionNotFoundError(session_id)

        # Check if history is enabled
        if not session.history_manager:
            msg = "History is not enabled for this session"
            raise ToolError(msg)

        await ctx.info(f"Clearing operation history for session {session_id}")

        # Get current operation count before clearing
        history_info = session.get_history()
        operations_count = history_info.get("total_operations", 0)

        # Clear the history
        session.history_manager.clear_history()

        await ctx.info(f"Cleared {operations_count} operations from history")

        return ClearHistoryResult(
            operations_cleared=operations_count,
            history_was_enabled=True,
        )

    except SessionNotFoundError as e:
        logger.error("Clear history failed: %s", e.message)
        raise ToolError(e.message) from e
    except ToolError:
        raise
    except Exception as e:
        logger.error("Error clearing history: %s", str(e))
        await ctx.error(f"Failed to clear history: {e!s}")
        msg = f"Error clearing operation history: {e}"
        raise ToolError(msg) from e


async def export_history(
    ctx: Annotated[Context, Field(description="FastMCP context for session access")],
    file_path: Annotated[str, Field(description="Output file path for history export")],
    export_format: Annotated[
        Literal["json", "csv"],
        Field(description="Export format: json or csv"),
    ] = "json",
) -> ExportHistoryResult:
    """Export operation history to a file for audit trails.

    Creates a permanent record of all operations performed in the session,
    including timestamps, descriptions, and metadata. Essential for data
    governance, reproducibility, and workflow documentation.

    Args:
        ctx: FastMCP context for session access
        file_path: Path where history file will be saved
        format: Export format - 'json' (detailed) or 'csv' (tabular)

    Returns:
        Result of export operation including file details and operation count

    Export Formats:
        📋 JSON: Complete structured export with all metadata
        📊 CSV: Tabular format optimized for analysis and reporting
        🕐 Timestamps: Precise timing information for each operation
        📝 Descriptions: Human-readable operation summaries

    Examples:
        # Export complete history as JSON
        result = await export_history("session_123", "/path/to/audit.json")

        # Export as CSV for analysis
        result = await export_history("session_123", "/path/to/log.csv", export_format="csv")

    AI Workflow Integration:
        1. Compliance and audit trail generation
        2. Workflow documentation for team knowledge sharing
        3. Process optimization through operation analysis
        4. Reproducibility records for scientific workflows
        5. Performance analysis of transformation sequences

    File Contents:
        - Operation IDs and types
        - Execution timestamps
        - Operation descriptions
        - Success/failure status
        - Parameters and configuration used
    """
    try:
        # Get session_id from FastMCP context
        session_id = ctx.session_id

        manager = get_session_manager()
        session = manager.get_or_create_session(session_id)

        if not session:
            raise SessionNotFoundError(session_id)

        if not session.history_manager:
            msg = "History is not enabled for this session"
            raise ToolError(msg)

        await ctx.info(f"Exporting history for session {session_id} to {file_path}")

        # Export the history
        success = session.history_manager.export_history(file_path, export_format)

        if not success:
            msg = "History export operation failed"
            raise ToolError(msg)

        # Get operation count for response
        history_info = session.get_history()
        operations_count = history_info.get("total_operations", 0)

        # Try to get file size
        file_size = None
        try:
            from pathlib import Path

            file_size = Path(file_path).stat().st_size
        except Exception as e:
            # File size is optional, continue without it
            logger.debug("Could not get file size for %s: %s", file_path, e)

        await ctx.info(f"Successfully exported {operations_count} operations to {file_path}")

        return ExportHistoryResult(
            file_path=file_path,
            format=export_format,
            operations_exported=operations_count,
            file_size_bytes=file_size,
        )

    except SessionNotFoundError as e:
        logger.error("History export failed: %s", e.message)
        raise ToolError(e.message) from e
    except ToolError:
        raise
    except Exception as e:
        logger.error("Error exporting history: %s", str(e))
        await ctx.error(f"Failed to export history: {e!s}")
        msg = f"Error exporting operation history: {e}"
        raise ToolError(msg) from e


# ============================================================================
# AUTO-SAVE OPERATIONS LOGIC
# ============================================================================


async def configure_auto_save(
    ctx: Annotated[Context, Field(description="FastMCP context for session access")],
    *,
    enabled: Annotated[bool, Field(description="Whether to enable auto-save functionality")] = True,
    mode: Annotated[
        Literal["disabled", "after_operation", "periodic", "hybrid"],
        Field(description="Auto-save trigger mode"),
    ] = "after_operation",
    strategy: Annotated[
        Literal["overwrite", "backup", "versioned", "custom"],
        Field(description="File saving strategy"),
    ] = "backup",
    interval_seconds: Annotated[
        int | None,
        Field(description="Interval between periodic saves in seconds"),
    ] = None,
    max_backups: Annotated[
        int | None,
        Field(description="Maximum number of backup files to keep"),
    ] = None,
    backup_dir: Annotated[str | None, Field(description="Directory for backup files")] = None,
    custom_path: Annotated[str | None, Field(description="Custom file path for saves")] = None,
    export_format: Annotated[
        Literal["csv", "tsv", "json", "excel", "parquet"],
        Field(description="Export format for saved files"),
    ] = "csv",
    encoding: Annotated[str, Field(description="Text encoding for saved files")] = "utf-8",
) -> AutoSaveConfigResult:
    """Configure auto-save settings for a session.

    Establishes automated data preservation policies to protect against data loss
    and enable workflow continuity. Supports multiple save strategies and timing
    modes to balance data safety with performance requirements.

    Args:
        ctx: FastMCP context for session access
        enabled: Whether auto-save functionality is active
        mode: When to trigger saves (after_operation, periodic, hybrid, disabled)
        strategy: How to handle save files (overwrite, backup, versioned, custom)
        interval_seconds: Interval for periodic saves (minimum 30 seconds)
        max_backups: Maximum backup files to retain (for backup/versioned strategies)
        backup_dir: Directory for backup files (default: session temp directory)
        custom_path: Fixed path for saves (when strategy='custom')
        format: File format for saves (csv, tsv, json, excel, parquet)
        encoding: Text encoding for output files

    Returns:
        Configuration result with current and previous settings

    Auto-Save Modes:
        🎯 after_operation: Save after each data transformation (safest)
        ⏰ periodic: Save at regular intervals (performance-optimized)
        🔄 hybrid: Combine both modes for maximum protection
        ⏹️ disabled: Turn off auto-save completely

    Save Strategies:
        📝 overwrite: Replace existing file each time
        📦 backup: Keep multiple numbered backup files
        🔄 versioned: Timestamp-based file versioning
        🎯 custom: Save to specific fixed location

    Examples:
        # Basic setup - save after each operation
        config = await configure_auto_save("session_123", enabled=True)

        # Advanced setup - hybrid mode with backups
        config = await configure_auto_save(
            "session_123",
            mode="hybrid",
            strategy="backup",
            interval_seconds=300,  # 5 minutes
            max_backups=10
        )

        # Performance mode - periodic saves only
        config = await configure_auto_save(
            "session_123",
            mode="periodic",
            strategy="versioned",
            interval_seconds=600  # 10 minutes
        )

    AI Workflow Integration:
        1. Experiment protection during iterative analysis
        2. Long-running analysis workflow checkpointing
        3. Collaborative work session continuity
        4. Automated backup for critical business analysis
    """
    try:
        # Get session_id from FastMCP context
        session_id = ctx.session_id

        manager = get_session_manager()
        session = manager.get_or_create_session(session_id)

        if not session:
            raise SessionNotFoundError(session_id)

        await ctx.info(f"Configuring auto-save for session {session_id}")

        # Get previous configuration
        previous_status = session.get_auto_save_status()
        previous_config = None
        if previous_status.get("enabled", False) and "config" in previous_status:
            try:
                config_data = previous_status["config"]
                if isinstance(config_data, dict):
                    from ..models.auto_save import AutoSaveConfig

                    previous_config = AutoSaveConfig.from_dict(dict(config_data))
                else:
                    previous_config = None
            except Exception:
                # Previous config format might be incompatible, continue without it
                previous_config = None

        # Build new configuration
        config_dict: dict[str, Any] = {
            "enabled": enabled,
            "mode": mode,
            "strategy": strategy,
            "format": export_format,
            "encoding": encoding,
        }

        if interval_seconds is not None:
            config_dict["interval_seconds"] = interval_seconds
        if max_backups is not None:
            config_dict["max_backups"] = max_backups
        if backup_dir is not None:
            config_dict["backup_dir"] = backup_dir
        if custom_path is not None:
            config_dict["custom_path"] = custom_path

        # Validate configuration using Pydantic
        new_config = AutoSaveConfig(**config_dict)

        # Apply configuration to session
        result = await session.enable_auto_save(config_dict)

        if not result["success"]:
            msg = f"Failed to configure auto-save: {result.get('error', 'Unknown error')}"
            raise ToolError(
                msg,
            )

        await ctx.info(f"Auto-save configured: {mode} mode, {strategy} strategy")

        # Check if configuration actually changed
        config_changed = previous_config != new_config

        # Convert model instance to Pydantic AutoSaveConfig for response
        # Use local AutoSaveConfig class (Pydantic model)
        local_autosave_config = AutoSaveConfig  # Local reference to avoid confusion
        pydantic_config = local_autosave_config(
            enabled=new_config.enabled,
            mode=new_config.mode.value,  # type: ignore  # String literal matches Pydantic Literal type
            strategy=new_config.strategy.value,  # type: ignore  # String literal matches Pydantic Literal type
            interval_seconds=new_config.interval_seconds,
            max_backups=new_config.max_backups,
            backup_dir=new_config.backup_dir,
            custom_path=new_config.custom_path,
            export_format=new_config.export_format.value,  # type: ignore  # String literal matches Pydantic Literal type
            encoding=new_config.encoding,
        )

        pydantic_previous = None
        if previous_config:
            pydantic_previous = local_autosave_config(
                enabled=previous_config.enabled,
                mode=previous_config.mode.value,  # type: ignore  # String literal matches Pydantic Literal type
                strategy=previous_config.strategy.value,  # type: ignore  # String literal matches Pydantic Literal type
                interval_seconds=previous_config.interval_seconds,
                max_backups=previous_config.max_backups,
                backup_dir=previous_config.backup_dir,
                custom_path=previous_config.custom_path,
                export_format=previous_config.export_format.value,  # type: ignore  # String literal matches Pydantic Literal type
                encoding=previous_config.encoding,
            )

        return AutoSaveConfigResult(
            config=pydantic_config,  # type: ignore  # Pydantic models are compatible
            previous_config=pydantic_previous,  # type: ignore  # Pydantic models are compatible
            config_changed=config_changed,
        )

    except SessionNotFoundError as e:
        logger.error("Auto-save configuration failed: %s", e.message)
        raise ToolError(e.message) from e
    except ToolError:
        raise
    except Exception as e:
        logger.error("Error configuring auto-save: %s", str(e))
        await ctx.error(f"Failed to configure auto-save: {e!s}")
        msg = f"Error configuring auto-save: {e}"
        raise ToolError(msg) from e


async def disable_auto_save(
    ctx: Annotated[Context, Field(description="FastMCP context for session access")],
) -> AutoSaveDisableResult:
    """Disable auto-save for a session.

    Turns off all automated saving functionality for the session. Optionally
    performs a final save to preserve current state before disabling. Useful
    when transitioning to manual save control or when auto-save is impacting
    performance.

    Args:
        ctx: FastMCP context for session access

    Returns:
        Result of disable operation including whether final save was performed

    Disable Process:
        ⏹️ Mode Deactivation: Stops all automatic save triggers
        💾 Optional Final Save: Preserves current state before disable
        🧹 Cleanup: Cancels any scheduled periodic saves
        📝 State Recording: Tracks previous configuration for potential re-enable

    Examples:
        # Simply disable auto-save
        result = await disable_auto_save("session_123")

        # Check if final save was performed
        if result.final_save_performed:
            print(f"Final save at: {result.final_save_path}")

    AI Workflow Integration:
        1. Manual control during critical analysis phases
        2. Performance optimization for compute-intensive operations
        3. Transition to different save strategies mid-workflow
        4. Preparing for session export or transfer

    Note:
        Disabling auto-save increases risk of data loss. Consider triggering
        a manual save before performing risky operations.
    """
    try:
        # Get session_id from FastMCP context
        session_id = ctx.session_id

        manager = get_session_manager()
        session = manager.get_or_create_session(session_id)

        if not session:
            raise SessionNotFoundError(session_id)

        # Check current auto-save status
        current_status = session.get_auto_save_status()
        was_enabled = current_status.get("enabled", False)

        await ctx.info(f"Disabling auto-save for session {session_id}")

        # Disable auto-save
        result = await session.disable_auto_save()

        if not result["success"]:
            msg = f"Failed to disable auto-save: {result.get('error', 'Unknown error')}"
            raise ToolError(msg)

        # Check if a final save was performed
        final_save_performed = result.get("final_save_performed", False)
        final_save_path = result.get("final_save_path")

        if was_enabled:
            await ctx.info("Auto-save disabled successfully")
            if final_save_performed:
                await ctx.info(f"Final save completed: {final_save_path}")
        else:
            await ctx.info("Auto-save was already disabled")

        return AutoSaveDisableResult(
            was_enabled=bool(was_enabled),
            final_save_performed=bool(final_save_performed),
            final_save_path=str(final_save_path) if final_save_path is not None else None,
        )

    except SessionNotFoundError as e:
        logger.error("Auto-save disable failed: %s", e.message)
        raise ToolError(e.message) from e
    except ToolError:
        raise
    except Exception as e:
        logger.error("Error disabling auto-save: %s", str(e))
        await ctx.error(f"Failed to disable auto-save: {e!s}")
        msg = f"Error disabling auto-save: {e}"
        raise ToolError(msg) from e


async def get_auto_save_status(
    ctx: Annotated[Context, Field(description="FastMCP context for session access")],
) -> AutoSaveStatusResult:
    """Get current auto-save configuration and status.

    Retrieves comprehensive information about the session's auto-save configuration,
    including current settings, last save information, and upcoming scheduled saves.
    Essential for understanding current data protection policies.

    Args:
        ctx: FastMCP context for session access

    Returns:
        Complete auto-save status including configuration and timing information

    Status Information:
        ⚙️ Configuration: Current mode, strategy, and all settings
        🕐 Timing Info: Last save time and next scheduled save
        📊 Statistics: Total saves performed, success rates
        💾 File Info: Current save paths and backup locations

    Examples:
        # Check current auto-save status
        status = await get_auto_save_status("session_123")

        if status.status.enabled:
            print(f"Mode: {status.status.config.mode}")
            print(f"Last saved: {status.status.last_save_time}")

        # Monitor save frequency
        if status.status.next_scheduled_save:
            print(f"Next save: {status.status.next_scheduled_save}")

    AI Workflow Integration:
        1. Workflow status monitoring and validation
        2. Performance analysis of save frequency vs. operation speed
        3. Backup verification and audit trail maintenance
        4. Troubleshooting auto-save configuration issues
        5. Optimizing save policies based on usage patterns
    """
    try:
        # Get session_id from FastMCP context
        session_id = ctx.session_id

        manager = get_session_manager()
        session = manager.get_or_create_session(session_id)

        if not session:
            raise SessionNotFoundError(session_id)

        await ctx.info(f"Retrieving auto-save status for session {session_id}")

        # Get current status from session
        status_dict = session.get_auto_save_status()

        # Build status object
        pydantic_config_obj = None
        if status_dict.get("enabled", False) and "config" in status_dict:
            try:
                config_data = status_dict["config"]
                if isinstance(config_data, dict):
                    from ..models.auto_save import AutoSaveConfig as ModelConfig

                    model_config = ModelConfig.from_dict(dict(config_data))
                    # Convert to Pydantic AutoSaveConfig
                    local_autosave_config = AutoSaveConfig  # Local reference to avoid confusion
                    pydantic_config_obj = local_autosave_config(
                        enabled=model_config.enabled,
                        mode=model_config.mode.value,
                        strategy=model_config.strategy.value,
                        interval_seconds=model_config.interval_seconds,
                        max_backups=model_config.max_backups,
                        backup_dir=model_config.backup_dir,
                        custom_path=model_config.custom_path,
                        export_format=model_config.export_format.value,  # type: ignore  # String literal matches Pydantic Literal type
                        encoding=model_config.encoding,
                    )
            except Exception as e:
                logger.warning("Could not parse auto-save config: %s", e)

        status = AutoSaveStatus(
            enabled=bool(status_dict.get("enabled", False)),
            config=pydantic_config_obj,
            last_save_time=str(status_dict.get("last_save_time"))
            if status_dict.get("last_save_time") is not None
            else None,
            save_count=int(status_dict.get("save_count", 0)),
            last_save_path=str(status_dict.get("last_save_path"))
            if status_dict.get("last_save_path") is not None
            else None,
            next_scheduled_save=str(status_dict.get("next_scheduled_save"))
            if status_dict.get("next_scheduled_save") is not None
            else None,
        )

        if status.enabled:
            await ctx.info(
                f"Auto-save is enabled with {status.config.mode if status.config else 'unknown'} mode",
            )
        else:
            await ctx.info("Auto-save is currently disabled")

        return AutoSaveStatusResult(
            status=status,
        )

    except SessionNotFoundError as e:
        logger.error("Auto-save status check failed: %s", e.message)
        raise ToolError(e.message) from e
    except ToolError:
        raise
    except Exception as e:
        logger.error("Error getting auto-save status: %s", str(e))
        await ctx.error(f"Failed to get auto-save status: {e!s}")
        msg = f"Error retrieving auto-save status: {e}"
        raise ToolError(msg) from e


async def trigger_manual_save(
    ctx: Annotated[Context, Field(description="FastMCP context for session access")],
) -> ManualSaveResult:
    """Manually trigger a save operation for the session.

    Forces an immediate save of the current session state, bypassing auto-save
    scheduling and triggers. Uses the current auto-save configuration for file
    format and location, or defaults if auto-save is disabled.

    Args:
        ctx: FastMCP context for session access

    Returns:
        Result of save operation including file details and data statistics

    Save Process:
        💾 Immediate Save: Bypasses all scheduling and triggers immediate save
        ⚙️ Config Respect: Uses current auto-save settings for format and location
        📊 Data Capture: Saves complete current DataFrame state
        📝 Metadata: Records timing, file size, and data dimensions

    Examples:
        # Force immediate save
        result = await trigger_manual_save("session_123")
        print(f"Saved {result.rows_saved} rows to {result.save_path}")

        # Use before risky operations
        await trigger_manual_save("session_123")  # Checkpoint
        # ... perform experimental transformations ...

    AI Workflow Integration:
        1. Checkpoint creation before experimental operations
        2. Forced backups at critical workflow milestones
        3. Manual intervention when auto-save timing is insufficient
        4. Immediate data preservation before system maintenance
        5. Backup verification by triggering save and checking results

    Performance Notes:
        Manual saves respect current auto-save configuration but execute
        immediately. Large datasets may require time to complete the save
        operation.
    """
    try:
        # Get session_id from FastMCP context
        session_id = ctx.session_id

        manager = get_session_manager()
        session = manager.get_or_create_session(session_id)

        if not session:
            raise SessionNotFoundError(session_id)

        await ctx.info(f"Triggering manual save for session {session_id}")

        # Trigger manual save
        result = await session.manual_save()

        if not result["success"]:
            msg = f"Manual save failed: {result.get('error', 'Unknown error')}"
            raise ToolError(msg)

        # Extract result information
        save_path = result.get("save_path", "")
        save_format = result.get("format", "csv")
        file_size = result.get("file_size_bytes")
        save_time = result.get("save_time")

        # Get current data dimensions
        rows_saved = 0
        columns_saved = 0
        if session.has_data() and session.df is not None:
            rows_saved = len(session.df)
            columns_saved = len(session.df.columns)

        await ctx.info(f"Manual save completed: {save_path}")

        return ManualSaveResult(
            save_path=str(save_path),
            format=str(save_format),
            rows_saved=rows_saved,
            columns_saved=columns_saved,
            file_size_bytes=safe_int(file_size) if file_size is not None else None,
            save_time=str(save_time) if save_time is not None else None,
        )

    except SessionNotFoundError as e:
        logger.error("Manual save failed: %s", e.message)
        raise ToolError(e.message) from e
    except ToolError:
        raise
    except Exception as e:
        logger.error("Error in manual save: %s", str(e))
        await ctx.error(f"Failed to trigger manual save: {e!s}")
        msg = f"Error triggering manual save: {e}"
        raise ToolError(msg) from e


# ============================================================================
# FASTMCP SERVER SETUP
# ============================================================================

# Create History server
history_server = FastMCP(
    "DataBeak-History",
    instructions="History and auto-save management server for DataBeak with comprehensive operation tracking and data preservation capabilities",
)

# Register history operation functions directly as MCP tools
history_server.tool(name="undo")(undo_operation)
history_server.tool(name="redo")(redo_operation)
history_server.tool(name="get_history")(get_history)
history_server.tool(name="restore_to_operation")(restore_to_operation)
history_server.tool(name="clear_history")(clear_history)
history_server.tool(name="export_history")(export_history)

# Register auto-save operation functions directly as MCP tools
history_server.tool(name="configure_auto_save")(configure_auto_save)
history_server.tool(name="disable_auto_save")(disable_auto_save)
history_server.tool(name="get_auto_save_status")(get_auto_save_status)
history_server.tool(name="trigger_manual_save")(trigger_manual_save)
