"""
Grant Entity - Pure Domain Model

Written by Claude Code on 2025-10-13

PURPOSE: Represents a grant opportunity from the Writing Schedule

PRINCIPLES:
- Zero external dependencies (stdlib only)
- Validation at construction
- Domain logic methods (is_urgent, days_until_deadline)
- Immutable after creation (dataclass with frozen=False for id assignment)

EXTRACTED FROM: Grantwriting_Knowledge_Dashboard writing_schedule table schema
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class GrantStatus(Enum):
    """Grant opportunity status"""
    ACTIVE = "active"
    SUBMITTED = "submitted"
    AWARDED = "awarded"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    COMPLETED = "completed"


@dataclass
class Grant:
    """
    Grant opportunity entity - what a grant IS

    Represents a single grant opportunity from the Writing Schedule.
    Contains both identification (bernie_number, task_id) and workflow state
    (deadline, status, assigned developer).

    Domain logic:
    - is_urgent(): Deadline within 7 days
    - is_overdue(): Past deadline
    - days_until_deadline(): Time remaining calculation
    """

    # Core identification
    bernie_number: str                    # Funder identifier (BN000XXX format)
    funder_name: str                      # Funder display name
    program_name: str                     # Opportunity/program name
    task_id: Optional[str] = None         # Writing Schedule task identifier

    # Workflow state
    deadline: Optional[datetime] = None   # Due date
    dev_lead: Optional[str] = None        # Assigned developer
    status: str = GrantStatus.ACTIVE.value

    # Financial information
    amount_requested: Optional[float] = None
    amount_awarded: Optional[float] = None

    # Additional context
    type_: Optional[str] = None           # Proposal, LOI, Report, etc.
    area: Optional[str] = None            # Program area
    state: Optional[str] = None           # Geographic state
    initiative: Optional[str] = None      # Strategic initiative

    # Dates
    grant_start_date: Optional[datetime] = None
    grant_end_date: Optional[datetime] = None
    notification_date: Optional[datetime] = None

    # Notes and metadata
    dev_team_notes: Optional[str] = None

    # System fields
    id: Optional[int] = None              # Database primary key (assigned after save)
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate entity at construction - fail fast on invalid data"""

        # Required fields validation
        if not self.bernie_number:
            raise ValueError("Grant must have bernie_number (funder identifier)")

        if not self.bernie_number.startswith('BN'):
            raise ValueError(
                f"Invalid bernie_number format: {self.bernie_number}. "
                "Must start with 'BN' (e.g., BN000227)"
            )

        if not self.funder_name or not self.funder_name.strip():
            raise ValueError("Grant must have funder_name")

        if not self.program_name or not self.program_name.strip():
            raise ValueError("Grant must have program_name")

        # Validate status if provided
        valid_statuses = [s.value for s in GrantStatus]
        if self.status and self.status.lower() not in valid_statuses:
            # Log warning but don't fail - real data may have non-standard statuses
            pass  # Could add logging here if logger available

        # Validate amounts are non-negative
        if self.amount_requested is not None and self.amount_requested < 0:
            raise ValueError(f"amount_requested must be >= 0, got {self.amount_requested}")

        if self.amount_awarded is not None and self.amount_awarded < 0:
            raise ValueError(f"amount_awarded must be >= 0, got {self.amount_awarded}")

    def is_urgent(self, urgency_threshold_days: int = 7) -> bool:
        """
        Check if grant has an urgent deadline

        Domain logic - testable without database or mocks.

        Args:
            urgency_threshold_days: Number of days to consider urgent (default: 7)

        Returns:
            True if deadline is within threshold, False otherwise
        """
        if not self.deadline:
            return False

        days_remaining = self.days_until_deadline()
        if days_remaining is None:
            return False

        return 0 <= days_remaining <= urgency_threshold_days

    def is_overdue(self) -> bool:
        """
        Check if grant deadline has passed

        Returns:
            True if past deadline, False otherwise
        """
        if not self.deadline:
            return False

        days_remaining = self.days_until_deadline()
        if days_remaining is None:
            return False

        return days_remaining < 0

    def days_until_deadline(self) -> Optional[int]:
        """
        Calculate days until deadline

        Pure calculation - no side effects.

        Returns:
            Number of days until deadline (negative if past due),
            None if no deadline set
        """
        if not self.deadline:
            return None

        delta = self.deadline - datetime.now()
        return delta.days

    def is_active(self) -> bool:
        """Check if grant is in an active state (not completed/denied)"""
        inactive_statuses = [
            GrantStatus.DENIED.value,
            GrantStatus.WITHDRAWN.value,
            GrantStatus.COMPLETED.value
        ]
        return self.status.lower() not in inactive_statuses

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        deadline_str = self.deadline.strftime('%Y-%m-%d') if self.deadline else 'No deadline'
        return (
            f"Grant(bn={self.bernie_number}, "
            f"funder={self.funder_name}, "
            f"program={self.program_name}, "
            f"deadline={deadline_str}, "
            f"status={self.status})"
        )
