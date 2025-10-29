"""
Writing Schedule Adapter Schema - Raw Data Structure

Written by Claude Code on 2025-10-28

PURPOSE: Define raw data structure from writing_schedule_current table

PRINCIPLES:
- Adapter layer (RHETORICA) - knows external schema
- Pure data bag - no validation, no parsing, no business logic
- Uses canonical field names from WritingScheduleSchema (shared tool)
- Domain entities (CATEGORIAE) know nothing about this structure

RESPONSIBILITY:
- Represent exactly what writing_schedule_current table provides
- Type hint all fields for downstream adapters
- Document data formats (dates as strings, amounts as numeric strings)

This is NOT a domain entity. It's infrastructure plumbing between external
data source (Writing Schedule) and domain model (Proposal, Report, etc.)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class WritingScheduleRow:
    """
    Raw row from writing_schedule_current table.

    Represents exactly what the database provides - no transformation,
    no validation, no business logic. Just a typed data bag.

    Field Names: Use canonical names from WritingScheduleSchema
    Data Types: Match database storage (mostly TEXT)
    Required Fields: Only task_id is NOT NULL in database

    Date Fields: Stored as TEXT in YYYY-MM-DD format
    Amount Fields: Stored as TEXT (numeric string like "100000.0")
    Timestamp: updated_at is ISO 8601 string
    Archive Flag: is_archive is 0 or 1
    """

    # PRIMARY KEY (NOT NULL)
    task_id: str  # Unique identifier, e.g., "DOBBFD-GA25E-NSO-LOI-240830"

    # CORE IDENTIFICATION
    funder: Optional[str] = None  # Foundation/organization name
    opportunity: Optional[str] = None  # Specific program/opportunity name
    bernie_identifier: Optional[str] = None  # Bernie Number (BN000XXX format)
    short_name: Optional[str] = None  # Person responsible / lead

    # TYPE & STATUS
    type: Optional[str] = None  # "Proposal", "LOI", "Report", "Final Report", etc.
    status: Optional[str] = None  # Workflow status (numbered: "1. Awarded", etc.)

    # FINANCIAL (stored as TEXT - numeric strings)
    amount: Optional[str] = None  # Requested amount, e.g., "100000.0"
    award: Optional[str] = None  # Awarded amount if granted

    # DATES (all stored as TEXT in YYYY-MM-DD format)
    deadline: Optional[str] = None  # Application/submission deadline
    notification_date: Optional[str] = None  # When decision received
    grant_start_date: Optional[str] = None  # Project start date
    grant_end_date: Optional[str] = None  # Project end date
    reports_due: Optional[str] = None  # Report due date
    last_modified: Optional[str] = None  # Last modification date

    # PROGRAM/INITIATIVE CLASSIFICATION
    fiscal_year: Optional[str] = None  # e.g., "FY25"
    area: Optional[str] = None  # Program area
    initiative: Optional[str] = None  # Initiative name
    state: Optional[str] = None  # Geographic state (two-letter code)
    communities: Optional[str] = None  # Communities served

    # CONTENT & NOTES
    grant_goals: Optional[str] = None  # Goals for the grant
    dev_team_notes: Optional[str] = None  # Internal development notes
    acknowledgment_needs: Optional[str] = None  # Acknowledgment requirements
    members_funded: Optional[str] = None  # Team members supported
    model_funded: Optional[str] = None  # Business model/approach funded

    # EXTERNAL SYSTEM INTEGRATION
    bloomerang_account: Optional[str] = None  # Bloomerang CRM account reference
    owner: Optional[str] = None  # Assigned owner/responsible party

    # EXCLUDED FIELDS (present in DB but typically filtered)
    month: Optional[str] = None  # Month categorization
    recent_pledge: Optional[str] = None  # Recent pledge information
    internal_status: Optional[str] = None  # Internal workflow flags
    note_stub: Optional[str] = None  # CRM note template stub

    # SYSTEM FIELDS
    updated_at: Optional[str] = None  # ISO 8601 timestamp string
    is_archive: Optional[int] = None  # 0=active, 1=archived

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (
            f"WritingScheduleRow(task_id='{self.task_id}', "
            f"type={self.type}, "
            f"funder='{self.funder}', "
            f"status={self.status})"
        )
