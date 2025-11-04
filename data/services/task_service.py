"""
Task Blueprints - Intermediate Representation for Task Construction

Written by Claude Code on 2025-10-29

PURPOSE: Define typed intermediate structures for building ScheduledTask entities

ARCHITECTURE:
- Blueprints contain all data needed to build a ScheduledTask
- Use NATURAL KEYS (strings) not FOREIGN KEYS (ints)
- Orchestrator layer resolves natural keys → foreign keys
- Then builds final domain entities with proper FKs

WHY BLUEPRINTS?
1. Decomposer doesn't need DB access (pure transformation)
2. Type-safe intermediate representation (not untyped dict)
3. Explicit about what needs FK resolution (status_text, funder_name, owner_name)
4. Self-documenting data flow

WORKFLOW:
1. Decomposer: WritingScheduleRow → Blueprint (natural keys)
2. Orchestrator: Blueprint + DB lookups → ScheduledTask (FKs resolved)
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class TaskCoreBlueprint:
    """
    Blueprint for TaskCore - common data for all task types.

    Contains natural keys (strings) that will be resolved to foreign keys.

    Note: bernie_number is already a natural key (external identifier), so no resolution needed.
    """
    task_id: str                    # Unique identifier from external system
    task_type: str                  # "LOI", "Proposal", "Report", "Reminder"
    bernie_number: str              # FK to Funder (natural key from external system)

    # Natural keys (will resolve to FKs)
    status_text: str                # Will resolve to → raw_statuses.id
    owner_name: Optional[str]       # Will resolve to → dev_team_members.id

    # Direct fields
    deadline: datetime
    last_modified: datetime

    # Program classification
    fiscal_year: Optional[str] = None
    program_area: Optional[str] = None
    initiative: Optional[str] = None

    opportunity_id: Optional[str] = None


@dataclass
class LOIBlueprint:
    """
    Blueprint for LOI entity.

    Contains all data needed to construct an LOI, but uses natural keys
    instead of foreign keys.

    Note: Funder and program fields are in core (normalized).
    """
    core: TaskCoreBlueprint

    # LOI-specific fields
    notification_date: Optional[datetime] = None
    amount_requested: Optional[Decimal] = None

    # Relationships (natural keys)
    related_proposal_id: Optional[str] = None  # task_id of proposal (if exists)

    # LOI-specific notes
    dev_team_notes: Optional[str] = None


@dataclass
class ProposalBlueprint:
    """
    Blueprint for Proposal entity.

    Amount requested is REQUIRED (not optional) - enforced at blueprint level.

    Note: Funder and common program fields (fiscal_year, program_area, initiative)
    are in core (normalized).
    """
    core: TaskCoreBlueprint

    # Proposal-specific fields
    amount_requested: Decimal           # REQUIRED for proposals!
    award_amount: Optional[Decimal] = None

    # Dates
    submission_date: Optional[datetime] = None
    notification_date: Optional[datetime] = None
    grant_start_date: Optional[datetime] = None
    grant_end_date: Optional[datetime] = None

    # Proposal-specific program details
    communities: Optional[str] = None
    members_funded: Optional[str] = None
    model_funded: Optional[str] = None

    # Notes
    dev_team_notes: Optional[str] = None
    grant_goals: Optional[str] = None

    def __post_init__(self):
        """Validate proposal blueprint at construction"""
        if self.amount_requested < 0:
            raise ValueError(f"Proposal amount cannot be negative: {self.amount_requested}")


@dataclass
class ReportBlueprint:
    """
    Blueprint for Report entity.

    Reports have NO amount fields (they don't request money).

    Note: Funder and program fields (fiscal_year, program_area, initiative)
    are in core (normalized).
    """
    core: TaskCoreBlueprint

    # Report-specific fields
    report_type: str                    # "Final Report", "Interim Report", "Report"

    # Relationships (natural keys)
    related_proposal_id: Optional[str] = None  # task_id of proposal being reported on

    # Dates
    submission_date: Optional[datetime] = None
    reporting_period_start: Optional[datetime] = None
    reporting_period_end: Optional[datetime] = None

    # Report-specific
    acknowledgment_needs: Optional[str] = None
    dev_team_notes: Optional[str] = None


@dataclass
class ReminderBlueprint:
    """
    Blueprint for Reminder entity.

    Lightweight scheduled task - just core scheduling + note.
    """
    core: TaskCoreBlueprint

    # Reminder-specific
    reminder_note: Optional[str] = None


# Type alias for any task blueprint
TaskBlueprint = LOIBlueprint | ProposalBlueprint | ReportBlueprint | ReminderBlueprint
