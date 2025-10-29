"""
Writing Schedule Parser - Adapter Layer Translation

Written by Claude Code on 2025-10-28

PURPOSE: Translate WritingScheduleRow → Domain Entities

PRINCIPLES:
- Pure functions (stateless transformations)
- This is the ONLY place that knows both WS schema AND domain entities
- No business logic (urgency, workflows) - just field mapping
- Returns domain entities ready for validation and persistence

RESPONSIBILITIES:
- Type dispatch (classify what entities to create)
- Field mapping (WS field names → domain field names)
- Data parsing (string dates → datetime, string amounts → float)
- Status mapping (WS numbered statuses → domain statuses)

This is adapter/translation layer (RHETORICA → CATEGORIAE boundary)
"""

from typing import List, Union, Optional
from datetime import datetime
from .schema import WritingScheduleRow
from data.entities import Proposal, Report, LOI, Prospect


def parse_writing_schedule_row(
    row: WritingScheduleRow,
    opportunity_id: int
) -> List[Union[Proposal, Report, LOI, Prospect]]:
    """
    Parse WritingScheduleRow into domain entities.

    Returns list because some WS types create multiple entities:
    - "Proposal & Report" → [Proposal(), Report()]
    - Most types → [single entity]
    - Unknown types → []

    Args:
        row: Raw data from writing_schedule_current table
        opportunity_id: Domain opportunity this belongs to

    Returns:
        List of domain entities (0-2 items)

    Usage:
        ws_row = WritingScheduleRow(task_id="ABC", type="Proposal", ...)
        entities = parse_writing_schedule_row(ws_row, opportunity_id=42)
        for entity in entities:
            repository.save(entity)
    """
    if not row.type:
        return []

    # Dispatch based on Writing Schedule type field
    if row.type == "Proposal":
        return [_to_proposal(row, opportunity_id)]

    elif row.type == "LOI":
        return [_to_loi(row, opportunity_id)]

    elif row.type in ("Report", "Final Report", "Interim Report"):
        return [_to_report(row, opportunity_id)]

    elif row.type == "Proposal & Report":
        # Special case: creates BOTH entities
        return [
            _to_proposal(row, opportunity_id),
            _to_report(row, opportunity_id)
        ]

    elif row.type == "Reminder":
        # TODO: How to handle reminders? Ignore for now
        return []

    else:
        # Unknown type - could log warning
        return []


def _to_proposal(row: WritingScheduleRow, opportunity_id: int) -> Proposal:
    """
    Map WritingScheduleRow → Proposal entity.

    Field mappings:
    - deadline (str) → deadline (datetime)
    - amount (str) → amount_requested (float)
    - award (str) → amount_awarded (float)
    - status (numbered WS status) → status (domain enum)
    """
    return Proposal(
        opportunity_id=opportunity_id,
        task_id=row.task_id,
        deadline=_parse_date(row.deadline),
        submission_date=None,  # Not tracked in WS
        notification_date=_parse_date(row.notification_date),
        grant_start_date=_parse_date(row.grant_start_date),
        grant_end_date=_parse_date(row.grant_end_date),
        amount_requested=_parse_amount(row.amount),
        amount_awarded=_parse_amount(row.award),
        status=_map_status_to_proposal(row.status),
        fiscal_year=row.fiscal_year,
        program_area=row.area,
        initiative=row.initiative,
        communities=row.communities,
        dev_team_notes=row.dev_team_notes,
        # dev_lead_id would need lookup from row.owner or row.short_name
    )


def _to_report(row: WritingScheduleRow, opportunity_id: int) -> Report:
    """
    Map WritingScheduleRow → Report entity.

    Field mappings:
    - reports_due (str) → deadline (datetime)
    - type field → report_type ('final', 'interim', etc.)
    - status (numbered WS status) → status (domain enum)
    """
    return Report(
        opportunity_id=opportunity_id,
        task_id=row.task_id,
        deadline=_parse_date(row.reports_due),  # Note: different field!
        submission_date=None,  # Not tracked in WS
        status=_map_status_to_report(row.status),
        report_type=_infer_report_type(row.type),
        fiscal_year=row.fiscal_year,
        dev_team_notes=row.dev_team_notes,
        # dev_lead_id would need lookup from row.owner or row.short_name
    )


def _to_loi(row: WritingScheduleRow, opportunity_id: int) -> LOI:
    """
    Map WritingScheduleRow → LOI entity.

    Field mappings:
    - deadline (str) → deadline (datetime)
    - amount (str) → amount_requested (float)
    - status (numbered WS status) → status (domain enum)
    """
    return LOI(
        opportunity_id=opportunity_id,
        task_id=row.task_id,
        deadline=_parse_date(row.deadline),
        submission_date=None,  # Not tracked in WS
        notification_date=_parse_date(row.notification_date),
        amount_requested=_parse_amount(row.amount),
        status=_map_status_to_loi(row.status),
        fiscal_year=row.fiscal_year,
        program_area=row.area,
        dev_team_notes=row.dev_team_notes,
        # dev_lead_id would need lookup
    )


def _to_prospect(row: WritingScheduleRow, opportunity_id: int) -> Prospect:
    """
    Map WritingScheduleRow → Prospect entity.

    Note: Prospects may not be explicitly typed in WS.
    This function is here for completeness but may not be used.
    """
    return Prospect(
        opportunity_id=opportunity_id,
        task_id=row.task_id,
        target_deadline=_parse_date(row.deadline),
        estimated_amount=_parse_amount(row.amount),
        status=_map_status_to_prospect(row.status),
        program_area=row.area,
        dev_team_notes=row.dev_team_notes,
        # dev_lead_id would need lookup
    )


# ============================================================================
# PARSING HELPERS (string → typed values)
# ============================================================================

def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse YYYY-MM-DD string to datetime.

    Args:
        date_str: Date string from WS (format: "2024-12-31")

    Returns:
        datetime object or None if invalid/missing
    """
    if not date_str:
        return None

    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        # Invalid format - return None rather than crash
        return None


def _parse_amount(amount_str: Optional[str]) -> Optional[float]:
    """
    Parse numeric string to float.

    Args:
        amount_str: Amount from WS (format: "100000.0" or "")

    Returns:
        Float value or None if invalid/missing
    """
    if not amount_str or amount_str.strip() == "":
        return None

    try:
        return float(amount_str)
    except ValueError:
        return None


# ============================================================================
# STATUS MAPPING (WS numbered statuses → domain statuses)
# ============================================================================

def _map_status_to_proposal(ws_status: Optional[str]) -> str:
    """
    Map Writing Schedule status → Proposal.status.

    WS statuses are numbered (e.g., "1. Awarded", "2. Application Submitted")
    Domain statuses are simple: active, submitted, awarded, denied, withdrawn

    Args:
        ws_status: Status from WS (e.g., "1. Awarded")

    Returns:
        Domain status string
    """
    if not ws_status:
        return 'active'

    # Check for keywords in status string
    if "Awarded" in ws_status:
        return 'awarded'
    elif "Application Submitted" in ws_status:
        return 'submitted'
    elif "Denied" in ws_status:
        return 'denied'
    elif "Withdrawn" in ws_status or "Forgone" in ws_status:
        return 'withdrawn'
    else:
        # Default: Draft, Planned, Research, etc. → active
        return 'active'


def _map_status_to_report(ws_status: Optional[str]) -> str:
    """
    Map Writing Schedule status → Report.status.

    Domain statuses: active, submitted, completed, overdue
    """
    if not ws_status:
        return 'active'

    if "Report Submitted" in ws_status or "Follow-Up Complete" in ws_status:
        return 'submitted'
    elif "Denied" in ws_status or "Withdrawn" in ws_status:
        return 'completed'
    else:
        return 'active'


def _map_status_to_loi(ws_status: Optional[str]) -> str:
    """
    Map Writing Schedule status → LOI.status.

    Domain statuses: active, submitted, invited, declined
    """
    if not ws_status:
        return 'active'

    if "LOI Submitted" in ws_status:
        return 'submitted'
    elif "Awarded" in ws_status:
        return 'invited'  # Awarded after LOI → invited to submit full proposal
    elif "Denied" in ws_status or "Withdrawn" in ws_status:
        return 'declined'
    else:
        return 'active'


def _map_status_to_prospect(ws_status: Optional[str]) -> str:
    """
    Map Writing Schedule status → Prospect.status.

    Domain statuses: active, researching, pursuing, declined
    """
    if not ws_status:
        return 'active'

    if "Research" in ws_status:
        return 'researching'
    elif "Planned" in ws_status or "Draft" in ws_status:
        return 'pursuing'
    elif "Withdrawn" in ws_status or "Forgone" in ws_status or "Ineligible" in ws_status:
        return 'declined'
    else:
        return 'active'


# ============================================================================
# TYPE INFERENCE HELPERS
# ============================================================================

def _infer_report_type(ws_type: Optional[str]) -> Optional[str]:
    """
    Infer Report.report_type from Writing Schedule type field.

    WS type field may be: "Report", "Final Report", "Interim Report"
    Domain report_type: 'interim', 'final', 'annual', 'financial'

    Args:
        ws_type: Type field from WS

    Returns:
        Domain report_type or None (generic report)
    """
    if not ws_type:
        return None

    if "Final" in ws_type:
        return 'final'
    elif "Interim" in ws_type:
        return 'interim'
    else:
        return None  # Generic report
