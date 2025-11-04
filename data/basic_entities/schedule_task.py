
"""
Task Entities - Composition-Based Architecture

Written by Claude Code on 2025-10-29

PURPOSE: Define scheduled task entities using composition rather than inheritance.

DESIGN DECISIONS:
1. Composition over Inheritance: Each entity (LOI, Proposal, Report) contains a
   TaskCore rather than inheriting from a base class.

2. Protocol for Duck Typing: ScheduledTask Protocol defines the contract that
   all task entities must fulfill without requiring inheritance.

3. Type Safety Through Structure: Each entity exposes required properties via
   composition, enabling type checkers to validate usage.

4. Separation of Concerns: TaskCore handles scheduling logistics; specific
   entities handle domain logic for their type.

OMISSIONS:
- Opportunity is NOT included (it's a composite entity to be designed separately)
- No inheritance hierarchy (composition provides flexibility)
- No abstract base class enforcement (Protocol enables structural typing)
"""

from dataclasses import dataclass
from typing import Optional, Protocol
from datetime import datetime
from decimal import Decimal


# --- Protocol Definition ---

class ScheduledTask(Protocol):
    """
    Protocol defining the contract for all scheduled tasks.

    Any entity that implements these properties can be treated as a ScheduledTask
    without requiring inheritance. This enables duck typing with type safety.

    Note: status_id is FK to Status entity (normalized design)
    """
    @property
    def task_id(self) -> str: ...

    @property
    def deadline(self) -> datetime: ...

    @property
    def task_type(self) -> str: ...

    @property
    def status_id(self) -> int: ...


# --- Composition Core ---

@dataclass
class TaskCore:
    """
    Core scheduling data shared by all task types.

    This is the composition component that every entity contains.
    Handles common fields: identification, timing, ownership, status, funder relationship.

    Note: opportunity_id intentionally nullable - some tasks may not link
    to opportunities initially (e.g., exploratory LOIs).

    NORMALIZED DESIGN (3NF+):
    - bernie_number is FK to Funder (stored in scheduled_tasks)
    - status_id is FK to raw_statuses (stored in scheduled_tasks)
    - Program fields normalized to task level (fiscal_year, program_area, initiative)
    """
    task_id: str              # Unique identifier (from writing schedule)
    task_type: str            # "LOI", "Proposal", "Report", "Reminder"
    bernie_number: str        # FK to Funder (normalized to scheduled_tasks)
    status_id: int            # FK to raw_statuses.id (workflow status)
    deadline: datetime        # When task is due
    owner_id: Optional[int]   # FK to dev_team_members.id
    last_modified: datetime   # Last update timestamp

    # Program classification (normalized to scheduled_tasks)
    fiscal_year: Optional[str] = None      # "FY25"
    program_area: Optional[str] = None     # "Education", "Youth Development"
    initiative: Optional[str] = None       # Initiative name

    opportunity_id: Optional[str] = None   # Link to opportunity (if exists)


# --- Concrete Entity Types ---

@dataclass
class LOI:
    """
    Letter of Intent entity using composition.

    LOIs are preliminary submissions to gauge funder interest. They MAY have
    an amount requested, but it's often tentative at this stage.

    Relationship: LOI -> Proposal (optional, one-to-one)
    Most proposals don't have LOIs, so we store the relationship here to
    minimize null fields. If an LOI leads to a proposal, we link it here.

    Implements ScheduledTask protocol via property exposure.

    Note: Funder relationship is in core.bernie_number (normalized).
    Program fields (fiscal_year, program_area, initiative) are in core (normalized).
    """
    core: TaskCore                          # Composition: contains scheduling + funder data
    notification_date: Optional[datetime]   # When we expect to hear back
    amount_requested: Optional[Decimal]     # Requested amount (often tentative)

    # Relationship: Link to subsequent proposal if LOI led to full application
    related_proposal_id: Optional[str] = None  # task_id of proposal (if invited)

    # LOI-specific notes
    dev_team_notes: Optional[str] = None

    # Expose ScheduledTask protocol properties
    @property
    def task_id(self) -> str:
        return self.core.task_id

    @property
    def deadline(self) -> datetime:
        return self.core.deadline

    @property
    def task_type(self) -> str:
        return self.core.task_type

    @property
    def status_id(self) -> int:
        return self.core.status_id

    def __repr__(self) -> str:
        deadline_str = self.deadline.strftime('%Y-%m-%d')
        return f"LOI(task_id='{self.task_id}', bernie_number='{self.core.bernie_number}', deadline={deadline_str})"


@dataclass
class Proposal:
    """
    Proposal entity using composition.

    Proposals are full grant applications. Amount requested is REQUIRED
    (not optional) - you can't submit a proposal without requesting money.

    Key distinction from LOI: More detailed, committed ask for specific amount.

    Note: Funder relationship is in core.bernie_number (normalized).
    Program fields (fiscal_year, program_area, initiative) are in core (normalized).
    """
    core: TaskCore                        # Composition: contains scheduling + funder data
    amount_requested: Decimal             # Requested amount (REQUIRED for proposals!)

    # Award tracking
    award_amount: Optional[Decimal] = None

    # Dates specific to proposals
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

    # Expose ScheduledTask protocol properties
    @property
    def task_id(self) -> str:
        return self.core.task_id

    @property
    def deadline(self) -> datetime:
        return self.core.deadline

    @property
    def task_type(self) -> str:
        return self.core.task_type

    @property
    def status_id(self) -> int:
        return self.core.status_id

    def __post_init__(self):
        """Validate proposal at construction - fail fast"""
        if self.amount_requested < 0:
            raise ValueError(f"Proposal amount must be positive: {self.amount_requested}")


    def __repr__(self) -> str:
        deadline_str = self.deadline.strftime('%Y-%m-%d')
        return (
            f"Proposal(task_id='{self.task_id}', bernie_number='{self.core.bernie_number}', "
            f"amount=${self.amount_requested:,.0f}, deadline={deadline_str})"
        )


@dataclass
class Report:
    """
    Report entity using composition.

    Reports document grant performance and outcomes. They have NO amount fields
    because they're not requesting money - they're reporting on work already done.

    Relationship: Report -> Proposal (nearly always exists, one-to-one)
    Almost every report ties back to a proposal (the grant being reported on).
    We store the relationship here since proposals have 0-to-many reports.

    Key distinction: Reports are obligations, not asks. No financial request.

    Note: Funder relationship is in core.bernie_number (normalized).
    Program fields (fiscal_year, program_area, initiative) are in core (normalized).
    """
    core: TaskCore                        # Composition: contains scheduling + funder data
    report_type: str                      # "Final Report", "Interim Report", "Report"

    # Relationship: Link to the proposal this report is documenting
    related_proposal_id: Optional[str] = None  # task_id of proposal being reported on

    # Dates specific to reports
    submission_date: Optional[datetime] = None
    reporting_period_start: Optional[datetime] = None
    reporting_period_end: Optional[datetime] = None

    # Report-specific fields
    acknowledgment_needs: Optional[str] = None
    dev_team_notes: Optional[str] = None



    # Expose ScheduledTask protocol properties
    @property
    def task_id(self) -> str:
        return self.core.task_id

    @property
    def deadline(self) -> datetime:
        return self.core.deadline

    @property
    def task_type(self) -> str:
        return self.core.task_type

    @property
    def status_id(self) -> int:
        return self.core.status_id

    def __repr__(self) -> str:
        deadline_str = self.deadline.strftime('%Y-%m-%d')
        return (
            f"Report(task_id='{self.task_id}', bernie_number='{self.core.bernie_number}', "
            f"type={self.report_type}, deadline={deadline_str})"
        )


@dataclass
class Reminder:
    """
    Reminder entity using composition.

    Lightweight scheduled tasks for non-grant activities: follow-ups,
    administrative tasks, calendar events that need tracking but aren't
    LOIs, Proposals, or Reports.
    """
    core: TaskCore                        # Composition: contains scheduling data
    reminder_note: Optional[str] = None   # What this reminder is about

    # Expose ScheduledTask protocol properties
    @property
    def task_id(self) -> str:
        return self.core.task_id

    @property
    def deadline(self) -> datetime:
        return self.core.deadline

    @property
    def task_type(self) -> str:
        return self.core.task_type

    @property
    def status_id(self) -> int:
        return self.core.status_id

    def __repr__(self) -> str:
        deadline_str = self.deadline.strftime('%Y-%m-%d')
        note_preview = self.reminder_note[:30] + "..." if self.reminder_note and len(self.reminder_note) > 30 else self.reminder_note
        return f"Reminder(task_id='{self.task_id}', deadline={deadline_str}, note='{note_preview}')"

