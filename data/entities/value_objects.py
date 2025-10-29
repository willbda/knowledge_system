"""
Value Objects - Immutable Result Containers

Written by Claude Code on 2025-10-28

PURPOSE: Define explicit result structures for aggregated views

PRINCIPLES:
- Immutable (frozen=True)
- Type-safe with clear contracts
- Computed properties for derived data
- No business logic (just data containers with properties)
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass(frozen=True)
class OpportunityOverview:
    """Complete view of an opportunity with all related tasks and documents."""

    opportunity: 'Opportunity'
    funder: 'Funder'

    proposals: List['Proposal']
    reports: List['Report']
    lois: List['LOI']
    prospects: List['Prospect']
    documents: List['Document']

    @property
    def total_requested(self) -> float:
        """Sum of all proposal amounts requested."""
        return sum(p.amount_requested or 0 for p in self.proposals)

    @property
    def total_awarded(self) -> float:
        """Sum of all proposal amounts awarded."""
        return sum(p.amount_awarded or 0 for p in self.proposals)

    @property
    def has_urgent_tasks(self) -> bool:
        """Check if any task has an urgent deadline."""
        return (
            any(p.is_urgent() for p in self.proposals) or
            any(r.is_urgent() for r in self.reports) or
            any(l.is_urgent() for l in self.lois)
        )

    @property
    def next_deadline(self) -> Optional[datetime]:
        """Get the next upcoming deadline across all tasks."""
        deadlines = []
        deadlines.extend(p.deadline for p in self.proposals if p.deadline)
        deadlines.extend(r.deadline for r in self.reports if r.deadline)
        deadlines.extend(l.deadline for l in self.lois if l.deadline)

        future_deadlines = [d for d in deadlines if d >= datetime.now()]
        return min(future_deadlines) if future_deadlines else None


@dataclass(frozen=True)
class TaskSummary:
    """Aggregated statistics across all task types."""

    total_proposals: int
    active_proposals: int
    awarded_proposals: int

    total_reports: int
    overdue_reports: int

    total_lois: int
    invited_lois: int

    total_prospects: int

    @property
    def success_rate(self) -> float:
        """Calculate proposal success rate."""
        submitted = sum(1 for _ in range(self.total_proposals) if self.total_proposals > 0)
        if submitted == 0:
            return 0.0
        return (self.awarded_proposals / submitted) * 100
