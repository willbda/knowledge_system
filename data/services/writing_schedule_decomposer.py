"""
Writing Schedule Decomposer V2 - Returns Blueprints with Natural Keys

Written by Claude Code on 2025-10-30

PURPOSE: Decompose WritingScheduleRow into blueprints (not entities).
Blueprints use natural keys that will be resolved to FKs by the orchestrator.

KEY CHANGE: This version returns blueprints, not domain entities.
The orchestrator will handle FK resolution and entity construction.
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, Tuple

from data.adapters.writing_schedule.schema import WritingScheduleRow
from data.services.task_service import (
    TaskCoreBlueprint,
    LOIBlueprint,
    ProposalBlueprint,
    ReportBlueprint,
    ReminderBlueprint,
    TaskBlueprint
)
from data.services.data_parsing import parse_date, parse_decimal


def decompose_row(
    row: WritingScheduleRow
) -> Tuple[str, str, Optional[str], str, TaskBlueprint]:
    """
    Decompose WritingScheduleRow into blueprints with natural keys.

    Returns:
        (bernie_number, canonical_name, owner_name, raw_status, task_blueprint)

    This is pure transformation - no DB access, no FK resolution.
    The orchestrator will handle turning these into entities.
    """
    # Extract natural keys
    bernie_number = row.bernie_identifier or "UNKNOWN"
    canonical_name = row.funder or "Unknown Funder"
    owner_name = row.owner if row.owner else None
    raw_status = row.status or "Unknown"

    # Build task blueprint based on type
    task_blueprint = _extract_task_blueprint(row, raw_status, bernie_number, canonical_name, owner_name)

    return bernie_number, canonical_name, owner_name, raw_status, task_blueprint


def _extract_task_blueprint(
    row: WritingScheduleRow,
    raw_status: str,
    bernie_number: str,
    funder_name: str,
    owner_name: Optional[str]
) -> TaskBlueprint:
    """
    Build appropriate task blueprint based on row.type.

    All blueprints use natural keys (strings) not foreign keys (ints).
    """
    # Build common core
    core = TaskCoreBlueprint(
        task_id=row.task_id,
        task_type=row.type or "Unknown",
        bernie_number=bernie_number,  # FK to Funder (natural key from external system)
        status_text=raw_status,  # Natural key - will be resolved to status_id
        owner_name=owner_name,    # Natural key - will be resolved to owner_id
        deadline=parse_date(row.deadline) or datetime.now(),
        last_modified=parse_date(row.last_modified) or datetime.now(),
        fiscal_year=row.fiscal_year,  # Program fields (normalized to core)
        program_area=row.area,
        initiative=row.initiative,
        opportunity_id=None  # Could parse from task_id pattern in future
    )

    # Dispatch to type-specific builder
    if row.type == "LOI":
        return _build_loi_blueprint(row, core)

    elif row.type == "Proposal":
        return _build_proposal_blueprint(row, core)

    elif row.type in ("Report", "Final Report", "Interim Report"):
        return _build_report_blueprint(row, core)

    else:
        # Unknown type or "Reminder"
        return _build_reminder_blueprint(row, core)


def _build_loi_blueprint(row: WritingScheduleRow, core: TaskCoreBlueprint) -> LOIBlueprint:
    """Build LOI blueprint from row data."""
    return LOIBlueprint(
        core=core,
        notification_date=parse_date(row.notification_date),
        amount_requested=parse_decimal(row.amount),
        related_proposal_id=None,  # Would need separate process to link
        dev_team_notes=row.dev_team_notes
    )


def _build_proposal_blueprint(row: WritingScheduleRow, core: TaskCoreBlueprint) -> ProposalBlueprint:
    """Build Proposal blueprint from row data."""
    # Amount is required for proposals - default to 0 if missing
    amount_requested = parse_decimal(row.amount)
    if amount_requested is None:
        amount_requested = Decimal(0)

    return ProposalBlueprint(
        core=core,
        amount_requested=amount_requested,
        award_amount=parse_decimal(row.award),
        submission_date=None,  # Not in WritingSchedule
        notification_date=parse_date(row.notification_date),
        grant_start_date=parse_date(row.grant_start_date),
        grant_end_date=parse_date(row.grant_end_date),
        communities=row.communities,
        members_funded=row.members_funded,
        model_funded=row.model_funded,
        dev_team_notes=row.dev_team_notes,
        grant_goals=row.grant_goals
    )


def _build_report_blueprint(row: WritingScheduleRow, core: TaskCoreBlueprint) -> ReportBlueprint:
    """Build Report blueprint from row data."""
    return ReportBlueprint(
        core=core,
        report_type=row.type or "Report",
        related_proposal_id=None,  # Would need separate process to link
        submission_date=None,  # Not in WritingSchedule
        reporting_period_start=None,  # Not in WritingSchedule
        reporting_period_end=None,    # Not in WritingSchedule
        acknowledgment_needs=row.acknowledgment_needs,
        dev_team_notes=row.dev_team_notes
    )


def _build_reminder_blueprint(row: WritingScheduleRow, core: TaskCoreBlueprint) -> ReminderBlueprint:
    """Build Reminder blueprint for unknown/reminder tasks."""
    return ReminderBlueprint(
        core=core,
        reminder_note=row.dev_team_notes
    )
