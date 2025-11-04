"""
Domain Entities (CATEGORIAE) - What things ARE

Pure domain models with zero external dependencies.
Validation happens at construction, business logic lives here.

Written by Claude Code on 2025-10-28
Updated by Claude Code on 2025-10-29 - Consolidated scheduled task entities
"""

from .funder import Funder
from ..composite_entities.opportunity import Opportunity
from .dev_team import DevTeamMember
from .document import Document

# Scheduled task entities (composition-based architecture)
from .schedule_task import (
    ScheduledTask,  # Protocol
    TaskCore,       # Composition component
    LOI,            # Letter of Intent
    Proposal,       # Full grant application
    Report,         # Grant reporting
    Reminder,       # Lightweight scheduled task
)

__all__ = [
    # Core entities
    'Funder',
    'Opportunity',
    'DevTeamMember',
    'Document',

    # Scheduled task entities
    'ScheduledTask',
    'TaskCore',
    'LOI',
    'Proposal',
    'Report',
    'Reminder',
]
