"""
Proposal Entity - Pure Domain Model

Written by Claude Code on 2025-10-28

PURPOSE: Represents a full grant application with award potential

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
class Proposal:
    """Represents a full grant application with award potential."""

    opportunity_id: int
    task_id: str

    # Assignment
    dev_lead_id: Optional[int] = None
    status: Optional[str] = None

    # Dates
    deadline: Optional[datetime] = None
    submission_date: Optional[datetime] = None
    notification_date: Optional[datetime] = None
    grant_start_date: Optional[datetime] = None
    grant_end_date: Optional[datetime] = None

    # Financial
    amount_requested: Optional[float] = None
    amount_awarded: Optional[float] = None


    fiscal_year: Optional[str] = None
    program_area: Optional[str] = None
    initiative: Optional[str] = None
    communities: Optional[str] = None

    # Notes
    dev_team_notes: Optional[str] = None

    # System fields
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate entity at construction - fail fast"""


        # Validate amounts
        if self.amount_requested is not None and self.amount_requested < 0:
            raise ValueError(f"Amount requested cannot be negative: {self.amount_requested}")

        if self.amount_awarded is not None and self.amount_awarded < 0:
            raise ValueError(f"Amount awarded cannot be negative: {self.amount_awarded}")




    def __repr__(self) -> str:
        """Developer-friendly representation"""
        deadline_str = self.deadline.strftime('%Y-%m-%d') if self.deadline else 'No deadline'
        return (
            f"Proposal(id={self.id}, "
            f"opp_id={self.opportunity_id}, "
            f"status={self.status}, "
            f"deadline={deadline_str})"
        )
