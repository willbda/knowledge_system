"""
Domain Entities (CATEGORIAE) - What things ARE

Pure domain models with zero external dependencies.
Validation happens at construction, business logic lives here.

Written by Claude Code on 2025-10-13
"""

from .grant import Grant, GrantStatus
from .funder import Funder
from .dev_team import DevTeamMember
from .value_objects import (
    FunderOverview,
    GrantStatistics,
    Timeline,
    TimelineEvent,
    FunderStatistics,
    Document,
    DashboardData,
)

__all__ = [
    "Grant",
    "GrantStatus",
    "Funder",
    "DevTeamMember",
    "FunderOverview",
    "GrantStatistics",
    "Timeline",
    "TimelineEvent",
    "FunderStatistics",
    "Document",
    "DashboardData",
]
