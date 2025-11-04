"""
Common Utilities - Shared Low-Level Functions

Written by Claude Code on 2025-11-04

PURPOSE: Provide reusable utility functions used across adapters and services.

PRINCIPLES:
- No business logic (that belongs in services)
- No domain knowledge (that belongs in entities)
- Pure, reusable functions
- No external system dependencies
"""

from .parsing import parse_date, parse_decimal

__all__ = ['parse_date', 'parse_decimal']
