"""
Shared parsing utilities for external data ingestion.

Written by Claude Code on 2025-10-30

PURPOSE: Provide reusable parsing functions for converting external data
formats (strings) into typed domain values (datetime, Decimal).

These utilities are shared across all adapters and decomposers to ensure
consistent data parsing throughout the system.
"""

from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Optional


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse YYYY-MM-DD string to datetime.

    Args:
        date_str: Date string in "YYYY-MM-DD" format, or None

    Returns:
        datetime object if parsing succeeds, None otherwise

    Examples:
        >>> parse_date("2024-08-30")
        datetime.datetime(2024, 8, 30, 0, 0)
        >>> parse_date(None)
        None
        >>> parse_date("invalid")
        None
    """
    if not date_str:
        return None

    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


def parse_decimal(amount_str: Optional[str]) -> Optional[Decimal]:
    """
    Parse numeric string to Decimal.

    Args:
        amount_str: Numeric string (e.g., "100000.50"), or None

    Returns:
        Decimal object if parsing succeeds, None otherwise

    Examples:
        >>> parse_decimal("100000.50")
        Decimal('100000.50')
        >>> parse_decimal(None)
        None
        >>> parse_decimal("")
        None
        >>> parse_decimal("invalid")
        None
    """
    if not amount_str or not amount_str.strip():
        return None

    try:
        return Decimal(amount_str)
    except (InvalidOperation, ValueError):
        return None
