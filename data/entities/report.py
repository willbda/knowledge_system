"""
Report Entity - Pure Domain Model

Written by Claude Code on 2025-10-28

PURPOSE: Represents a grant reporting requirement

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
class Report:
    """Represents a grant reporting requirement."""

    opportunity_id: int
    task_id: Optional[str] = None

    # Assignment
    dev_lead_id: Optional[int] = None
    status: str = 'active'

    # Dates
    deadline: Optional[datetime] = None
    submission_date: Optional[datetime] = None

    # Report-specific
    report_type: Optional[str] = None          # 'interim', 'final'
    reporting_period_start: Optional[datetime] = None
    reporting_period_end: Optional[datetime] = None
    fiscal_year: Optional[str] = None

    # Notes
    dev_team_notes: Optional[str] = None

    # System fields
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


    def __repr__(self) -> str:
        """Developer-friendly representation"""
        deadline_str = self.deadline.strftime('%Y-%m-%d') if self.deadline else 'No deadline'
        type_str = f", type={self.report_type}" if self.report_type else ""
        return (
            f"Report(id={self.id}, "
            f"opp_id={self.opportunity_id}, "
            f"status={self.status}, "
            f"deadline={deadline_str}{type_str})"
        )
