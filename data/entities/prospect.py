"""
Prospect Entity - Pure Domain Model

Written by Claude Code on 2025-10-28

PURPOSE: Represents an early-stage funding opportunity under research

PRINCIPLES:
- Zero external dependencies (stdlib only)
- Validation at construction
- Domain logic for likelihood and status tracking
- Linked to Opportunity as anchor
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Prospect:
    """Represents an early-stage funding opportunity under research."""

    task_id: str

    # Assignment
    dev_lead_id: Optional[int] = None
    status: Optional[str] = 'researching'

    # Dates
    target_deadline: Optional[datetime] = None

    program_area: Optional[str] = None

    # Notes
    dev_team_notes: Optional[str] = None

    # System fields
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (
            f"Prospect(id={self.id}, "
            f"task_id={self.task_id}, "
            f"status={self.status})"
        )
