"""
Development Team Member Entity - Pure Domain Model

Written by Claude Code on 2025-10-28

PURPOSE: Represents a grant writer/developer on the team

PRINCIPLES:
- Zero external dependencies (stdlib only)
- Validation at construction
- Simple identity model

EXTRACTED FROM: Grantwriting_Knowledge_Dashboard (implicit in owner/assignee fields)
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class DevTeamMember:
    """Represents a grant writer/developer assignable to tasks."""

    name: str

    # System fields
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate entity at construction - fail fast"""

        if not self.name or not self.name.strip():
            raise ValueError("Name is required")


    def matches_name(self, name: str) -> bool:
        """Case-insensitive name comparison."""
        return self.name.lower() == name.lower()
