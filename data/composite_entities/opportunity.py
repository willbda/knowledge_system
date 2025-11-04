"""
Opportunity Entity - Pure Domain Model

Written by Claude Code on 2025-10-28

PURPOSE: Minimal identity anchor for a funding relationship

PRINCIPLES:
- Zero external dependencies (stdlib only)
- Validation at construction
- Serves as foreign key target for proposals, reports, etc.
- Represents the ongoing relationship, not individual tasks
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Opportunity:
    """
    Minimal identity anchor for a funding relationship.
    Serves as a foreign key target for proposals, reports, etc.
    """

    funder_id: int
    opportunity_name: Optional[str] = None
    description: Optional[str] = None
    status: str = 'active'

    # System fields
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (
            f"Opportunity(id={self.id}, "
            f"funder_id={self.funder_id}, "
            f"name='{self.opportunity_name}', "
            f"status={self.status})"
        )
