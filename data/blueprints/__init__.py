"""
Task Blueprints - Intermediate Representations

Written by Claude Code on 2025-11-04

PURPOSE: Define typed intermediate structures used between adapters and services.

ARCHITECTURE:
- Blueprints are the interface contract between adapters and orchestrator
- Use NATURAL KEYS (strings) not FOREIGN KEYS (ints)
- Orchestrator layer resolves natural keys → foreign keys
- Then builds final domain entities with proper FKs

WORKFLOW:
1. Adapter: ExternalRow → Blueprint (natural keys)
2. Orchestrator: Blueprint + DB lookups → DomainEntity (FKs resolved)
"""

from .task_blueprints import (
    TaskCoreBlueprint,
    LOIBlueprint,
    ProposalBlueprint,
    ReportBlueprint,
    ReminderBlueprint,
    TaskBlueprint
)

__all__ = [
    'TaskCoreBlueprint',
    'LOIBlueprint',
    'ProposalBlueprint',
    'ReportBlueprint',
    'ReminderBlueprint',
    'TaskBlueprint',
]
