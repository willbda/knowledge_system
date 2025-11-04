"""
Services Layer - Application Logic and Orchestration

Written by Claude Code on 2025-10-29
Refactored on 2025-11-04 - Clean architecture separation

PURPOSE: Coordinate multiple entities, repositories, and business workflows

PRINCIPLES:
- Services orchestrate domain entities (don't contain domain logic)
- Services coordinate repository interactions
- Services handle cross-cutting concerns (logging, validation, transactions)
- Pure functions where possible (stateless operations)

LAYER RESPONSIBILITIES:
- Orchestrate complex workflows (multi-entity operations)
- Apply business rules and semantics
- Coordinate FK resolution and entity construction
- Provide clean API for application/UI layers

WHAT'S NOT HERE:
- Adapters (moved to data/adapters/)
- Blueprints (moved to data/blueprints/)
- Utilities (moved to data/common/)
"""

from .orchestrator import TaskOrchestrator, BatchOrchestrator
from .status_semantics import StatusSemanticsService, is_actionable, was_successful, needs_follow_up

__all__ = [
    'TaskOrchestrator',
    'BatchOrchestrator',
    'StatusSemanticsService',
    'is_actionable',
    'was_successful',
    'needs_follow_up',
]
