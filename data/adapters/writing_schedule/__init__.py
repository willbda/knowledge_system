"""
Writing Schedule Adapter

Written by Claude Code on 2025-10-28
Refactored on 2025-11-04 - Added parser

PURPOSE: Adapter for Writing Schedule external data source

RESPONSIBILITIES:
- Define raw data schema (WritingScheduleRow)
- Parse raw data into domain blueprints (decompose_row)
- Know nothing about database or FK resolution
"""

from .schema import WritingScheduleRow
from .parser import decompose_row

__all__ = ['WritingScheduleRow', 'decompose_row']
