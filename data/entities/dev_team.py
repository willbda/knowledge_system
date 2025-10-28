"""
Development Team Member Entity - Pure Domain Model

Written by Claude Code on 2025-10-13

PURPOSE: Represents a grant writer/developer on the team

PRINCIPLES:
- Zero external dependencies (stdlib only)
- Validation at construction
- Simple identity model

EXTRACTED FROM: Grantwriting_Knowledge_Dashboard (implicit in owner/assignee fields)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DevTeamMember:
    """
    Development team member entity - what a team member IS

    Represents a grant writer/developer who can be assigned to opportunities.
    Currently simple, but can be extended with workload capacity, specializations, etc.

    Domain logic:
    - Future: workload_capacity checks
    - Future: specialization matching
    """

    # Core identification
    name: str                              # Full name as it appears in Writing Schedule

    # Optional metadata
    email: Optional[str] = None
    role: Optional[str] = None             # e.g., "Grant Writer", "Development Lead"

    # System fields
    id: Optional[int] = None               # Database primary key

    def __post_init__(self):
        """Validate entity at construction"""

        # Name validation
        if not self.name or not self.name.strip():
            raise ValueError("DevTeamMember must have name")

        # Email validation (basic)
        if self.email and '@' not in self.email:
            raise ValueError(f"Invalid email format: {self.email}")

    def matches_name(self, name: str) -> bool:
        """
        Check if given name matches this team member

        Simple case-insensitive comparison. Could be extended for
        nickname matching, etc.

        Args:
            name: Name to check

        Returns:
            True if names match (case-insensitive)
        """
        if not name:
            return False

        return self.name.lower().strip() == name.lower().strip()

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        role_str = f", role={self.role}" if self.role else ""
        return f"DevTeamMember(name='{self.name}'{role_str})"
