"""
Funder Entity - Pure Domain Model

Written by Claude Code on 2025-10-28

PURPOSE: Represents an organization (funder) in the Bernie Number registry

PRINCIPLES:
- Zero external dependencies (stdlib only)
- Validation at construction
- Domain logic for name matching
- Immutable identity (bernie_number)

EXTRACTED FROM: Grantwriting_Knowledge_Dashboard funder_registry table schema
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Funder:
    """
    Funder entity - what a funder/organization IS

    Represents a grant-making organization identified by a unique Bernie Number.
    Canonical name represents the official/preferred name.
    """

    # Core identification
    bernie_number: str                     # Unique identifier (BN000XXX format)
    canonical_name: str                    # Official/preferred name

    # Tax identification
    ein: Optional[str] = None              # 9-digit EIN (may be unknown)

    # CRM integration

    # System fields
    id: Optional[int] = None               # Database primary key
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate entity at construction - fail fast"""

        # Validate Bernie Number format
        if not self.bernie_number.startswith('BN'):
            raise ValueError(f"Bernie Number must start with 'BN': {self.bernie_number}")
        if len(self.bernie_number) != 8:
            raise ValueError(f"Bernie Number must be 8 characters: {self.bernie_number}")

        # Validate canonical name
        if not self.canonical_name or not self.canonical_name.strip():
            raise ValueError("Canonical name is required")

        # Validate EIN if provided
        if self.ein is not None:
            if len(self.ein) != 9 or not self.ein.isdigit():
                raise ValueError(f"EIN must be 9 digits: {self.ein}")

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        ein_str = f"ein={self.ein}" if self.ein else "ein=None"
        return (
            f"Funder(bn={self.bernie_number}, "
            f"name='{self.canonical_name}', "
            f"{ein_str})"
        )


@dataclass
class FunderAlias:
    """
    Represents an alias or name variation for a funder.

    One BN (Bernie Number) can have many aliases.
    Usage field tracks how often this alias appears in historical documents.
    """

    bernie_number: str  # Foreign key to Funder
    alias: str               # Alias name variation
    usage: Optional[str] = None # In what context this alias is used

    # System fields
    id: Optional[int] = None  # Autoincrementing primary key
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate entity at construction - fail fast"""

        # Validate Bernie Number format
        if not self.bernie_number.startswith('BN'):
            raise ValueError(f"Bernie Number must start with 'BN': {self.bernie_number}")
        if len(self.bernie_number) != 8:
            raise ValueError(f"Bernie Number must be 8 characters: {self.bernie_number}")

        # Catches empty or whitespace-only strings
        if not self.alias or not self.alias.strip():
            raise ValueError("Alias is required") 
