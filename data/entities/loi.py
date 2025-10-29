"""
LOI (Letter of Intent) Entity - Pure Domain Model

Written by Claude Code on 2025-10-28

PURPOSE: Represents a Letter of Intent submission

PRINCIPLES:
- Zero external dependencies (stdlib only)
- Validation at construction
- Domain logic for urgency and deadline tracking
- Linked to Opportunity as anchor
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class LOI:
    """Represents a Letter of Intent."""

    opportunity_id: int
    task_id: Optional[str] = None

    # Assignment
    dev_lead_id: Optional[int] = None
    status: str = 'active'

    # Dates
    deadline: Optional[datetime] = None
    submission_date: Optional[datetime] = None
    notification_date: Optional[datetime] = None

    # LOI-specific
    amount_requested: Optional[float] = None
    invited_to_apply: Optional[bool] = None    # None=pending, True=invited, False=declined
    fiscal_year: Optional[str] = None
    program_area: Optional[str] = None

    # Notes
    dev_team_notes: Optional[str] = None

    # System fields
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate entity at construction - fail fast"""

        # Validate status
        valid_statuses = ('active', 'submitted', 'invited', 'declined')
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")

        # Validate amount
        if self.amount_requested is not None and self.amount_requested < 0:
            raise ValueError(f"Amount requested cannot be negative: {self.amount_requested}")


    def __repr__(self) -> str:
        """Developer-friendly representation"""
        deadline_str = self.deadline.strftime('%Y-%m-%d') if self.deadline else 'No deadline'
        invited_str = ""
        if self.invited_to_apply is not None:
            invited_str = f", invited={self.invited_to_apply}"
        return (
            f"LOI(id={self.id}, "
            f"opp_id={self.opportunity_id}, "
            f"status={self.status}, "
            f"deadline={deadline_str}{invited_str})"
        )
