"""
Document Entity - Pure Domain Model (Immutable Value Object)

Written by Claude Code on 2025-10-28

PURPOSE: Immutable value object representing a file linked to an opportunity

PRINCIPLES:
- Zero external dependencies (stdlib only)
- Validation at construction
- Can link to specific tasks (proposals, reports, LOIs)
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Document:
    """
    Object representing a file linked to an opportunity.
    """

    file_path: str
    file_name: str

    # File metadata
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    modified_date: Optional[datetime] = None

    # Content
    indexed_content: Optional[str] = None

    # System fields
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate entity at construction - fail fast"""

        if not self.file_path:
            raise ValueError("File path is required")
        if not self.file_name:
            raise ValueError("File name is required")
