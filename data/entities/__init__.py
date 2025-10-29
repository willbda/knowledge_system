"""
Domain Entities (CATEGORIAE) - What things ARE

Pure domain models with zero external dependencies.
Validation happens at construction, business logic lives here.

Written by Claude Code on 2025-10-28
"""

from .funder import Funder
from .opportunity import Opportunity
from .dev_team import DevTeamMember
from .proposal import Proposal
from .report import Report
from .loi import LOI
from .prospect import Prospect
from .document import Document
from .value_objects import OpportunityOverview, TaskSummary

__all__ = [
    'Funder',
    'FunderAlias',
    'Opportunity',
    'DevTeamMember',
    'Proposal',
    'Report',
    'LOI',
    'Prospect',
    'Document',
    'OpportunityOverview',
    'TaskSummary',
]
