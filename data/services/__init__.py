"""
Services Layer - Application Logic and Orchestration

Written by Claude Code on 2025-10-29

PURPOSE: Coordinate multiple entities, repositories, and business workflows

PRINCIPLES:
- Services orchestrate domain entities (don't contain domain logic)
- Services coordinate repository interactions
- Services handle cross-cutting concerns (logging, validation, transactions)
- Pure functions where possible (stateless operations)

LAYER RESPONSIBILITIES:
- Decompose external data into domain entities
- Coordinate multi-entity operations
- Enforce business workflows
- Provide clean API for application/UI layers
"""

from .writing_schedule_decomposer import decompose_row

__all__ = ['decompose_row']
