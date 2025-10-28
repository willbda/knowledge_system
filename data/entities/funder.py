"""
Funder Entity - Pure Domain Model

Written by Claude Code on 2025-10-13

PURPOSE: Represents an organization (funder) in the Bernie Number registry

PRINCIPLES:
- Zero external dependencies (stdlib only)
- Validation at construction
- Domain logic for name matching
- Immutable identity (bernie_number)

EXTRACTED FROM: Grantwriting_Knowledge_Dashboard funder_registry table schema
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Funder:
    """
    Funder entity - what a funder/organization IS

    Represents a grant-making organization identified by a unique Bernie Number.
    Maintains canonical name and all known aliases for matching purposes.

    Domain logic:
    - has_alias(): Check if a name matches any known variant
    - matches_name(): Fuzzy name matching against aliases
    """

    # Core identification
    bernie_number: str                     # Unique identifier (BN000XXX format)
    canonical_name: str                    # Official/preferred name

    # Name variations for matching
    all_names: List[str]                   # All known aliases including canonical

    # Tax identification
    ein: Optional[str] = None              # 9-digit EIN (may be unknown)

    # CRM integration
    bloomerang_api_cid: Optional[int] = None        # Bloomerang constituent ID
    bloomerang_account_id: Optional[int] = None     # Bloomerang account number

    # System fields
    id: Optional[int] = None               # Database primary key

    def __post_init__(self):
        """Validate entity at construction - fail fast"""

        # Bernie Number validation
        if not self.bernie_number:
            raise ValueError("Funder must have bernie_number")

        if not self.bernie_number.startswith('BN'):
            raise ValueError(
                f"Invalid bernie_number format: {self.bernie_number}. "
                "Must start with 'BN' (e.g., BN000227)"
            )

        if len(self.bernie_number) != 8:
            raise ValueError(
                f"Bernie number must be 8 characters (BN + 6 hex digits), "
                f"got {len(self.bernie_number)}: {self.bernie_number}"
            )

        # Canonical name validation
        if not self.canonical_name or not self.canonical_name.strip():
            raise ValueError("Funder must have canonical_name")

        # Ensure all_names includes canonical name
        if not self.all_names:
            self.all_names = [self.canonical_name]
        elif self.canonical_name not in self.all_names:
            self.all_names.insert(0, self.canonical_name)

        # EIN validation if provided
        if self.ein is not None:
            if len(self.ein) != 9:
                raise ValueError(
                    f"EIN must be 9 digits, got {len(self.ein)}: {self.ein}"
                )
            if not self.ein.isdigit():
                raise ValueError(f"EIN must be numeric, got: {self.ein}")

    def has_alias(self, name: str) -> bool:
        """
        Check if name matches any known alias (case-insensitive)

        Domain logic - pure function, testable without database.

        Args:
            name: Name to check against aliases

        Returns:
            True if name matches any alias, False otherwise
        """
        if not name:
            return False

        name_lower = name.lower().strip()
        return any(alias.lower().strip() == name_lower for alias in self.all_names)

    def matches_name(self, name: str, fuzzy: bool = False) -> bool:
        """
        Check if name matches this funder

        Args:
            name: Name to check
            fuzzy: If True, use substring matching

        Returns:
            True if name matches (exact or fuzzy)
        """
        if not name:
            return False

        name_lower = name.lower().strip()

        # Exact match
        if self.has_alias(name):
            return True

        # Fuzzy match (substring)
        if fuzzy:
            return any(name_lower in alias.lower() or alias.lower() in name_lower
                      for alias in self.all_names)

        return False

    def add_alias(self, alias: str) -> None:
        """
        Add a new alias if not already present

        Note: This mutates the object. In a more strict functional approach,
        we'd return a new Funder instance. For pragmatism, we allow mutation.

        Args:
            alias: New alias to add
        """
        if not alias or not alias.strip():
            return

        alias_clean = alias.strip()
        if not self.has_alias(alias_clean):
            self.all_names.append(alias_clean)

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        alias_count = len(self.all_names) - 1  # Exclude canonical name
        ein_str = f"ein={self.ein}" if self.ein else "ein=None"
        return (
            f"Funder(bn={self.bernie_number}, "
            f"name='{self.canonical_name}', "
            f"aliases={alias_count}, "
            f"{ein_str})"
        )
