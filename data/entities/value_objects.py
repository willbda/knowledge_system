"""
Value Objects - Explicit Contracts

Written by Claude Code on 2025-10-13

PURPOSE: Define explicit result structures instead of implicit Dict[str, Any]

PRINCIPLES:
- Immutable (frozen=True)
- Type-safe with clear contracts
- Computed properties for derived data
- No business logic (just data containers with properties)

REPLACES: Implicit dict returns from services in old dashboard
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Any


@dataclass(frozen=True)
class TimelineEvent:
    """
    A single event in a timeline

    Represents a significant date (deadline, notification, start, end)
    associated with a grant or funder.
    """
    date: datetime
    event_type: str                    # 'deadline', 'notification', 'grant_start', 'grant_end'
    description: str
    grant_id: Optional[int] = None     # Associated grant (if applicable)
    metadata: Optional[dict] = None    # Additional context


@dataclass(frozen=True)
class Timeline:
    """
    Timeline of events for a funder or grant

    Provides chronological view of significant dates with computed properties
    for accessing past/future events.
    """
    events: List[TimelineEvent]

    @property
    def sorted_events(self) -> List[TimelineEvent]:
        """Events sorted chronologically"""
        return sorted(self.events, key=lambda e: e.date)

    @property
    def next_deadline(self) -> Optional[TimelineEvent]:
        """Next upcoming deadline event"""
        now = datetime.now()
        upcoming_deadlines = [
            e for e in self.sorted_events
            if e.event_type == 'deadline' and e.date > now
        ]
        return upcoming_deadlines[0] if upcoming_deadlines else None

    @property
    def past_events(self) -> List[TimelineEvent]:
        """Events in the past"""
        now = datetime.now()
        return [e for e in self.sorted_events if e.date < now]

    @property
    def future_events(self) -> List[TimelineEvent]:
        """Events in the future"""
        now = datetime.now()
        return [e for e in self.sorted_events if e.date >= now]


@dataclass(frozen=True)
class GrantStatistics:
    """
    Statistics for a collection of grants

    Aggregated metrics for dashboard/overview display.
    All computed from grant collections - no database queries.
    """
    total_grants: int
    active_grants: int
    urgent_grants: int                 # Deadlines within 7 days
    overdue_grants: int                # Past deadline

    total_amount_requested: float
    total_amount_awarded: float
    average_award: float

    # Status breakdown
    submitted_count: int
    awarded_count: int
    denied_count: int

    # Timeline stats
    earliest_deadline: Optional[datetime]
    latest_deadline: Optional[datetime]

    @property
    def success_rate(self) -> Optional[float]:
        """Percentage of grants awarded vs submitted"""
        denominator = self.awarded_count + self.denied_count
        if denominator == 0:
            return None
        return (self.awarded_count / denominator) * 100

    @property
    def pending_rate(self) -> float:
        """Percentage of grants still active"""
        if self.total_grants == 0:
            return 0.0
        return (self.active_grants / self.total_grants) * 100


@dataclass(frozen=True)
class FunderStatistics:
    """
    Statistics specific to a funder

    Extends GrantStatistics with funder-specific metrics like
    relationship timeline, grant cycle patterns, etc.
    """
    total_opportunities: int           # All historical opportunities
    active_opportunities: int          # Currently active
    total_awarded: float               # Total $ awarded historically
    average_award: float               # Average award amount

    # Relationship timeline
    years_active: int                  # How many years we've worked with this funder
    first_grant_date: Optional[datetime]
    most_recent_grant_date: Optional[datetime]

    # Grant cycle patterns
    avg_cycle_days: Optional[float]    # Average days from deadline to award

    @property
    def grants_per_year(self) -> float:
        """Average number of grants per year"""
        if self.years_active == 0:
            return 0.0
        return self.total_opportunities / self.years_active


@dataclass(frozen=True)
class Document:
    """
    A historical document associated with a funder/grant

    Represents a file from the fundraising folder mapped to a Bernie Number.
    """
    file_path: str
    folder_path: str
    file_name: str
    bernie_number: str

    # Optional metadata
    file_size: Optional[int] = None
    modified_date: Optional[datetime] = None
    file_type: Optional[str] = None    # .docx, .pdf, .xlsx


@dataclass(frozen=True)
class FunderOverview:
    """
    Complete funder profile data structure

    REPLACES: Implicit dict from FunderService.get_funder_data()

    Explicit contract for funder profile page with type-safe access
    to all related data.
    """
    # Core funder identity
    funder: 'Funder'                   # The funder entity (forward ref)

    # Related data
    grants: List['Grant']              # All grants for this funder
    documents: List[Document]          # Historical documents
    timeline: Timeline                 # Timeline of significant dates
    statistics: FunderStatistics       # Aggregated metrics

    # Optional CRM integration
    bloomerang_data: Optional[dict] = None    # External API data

    @property
    def has_active_grants(self) -> bool:
        """Check if funder has any active grants"""
        return any(g.is_active() for g in self.grants)

    @property
    def has_urgent_grants(self) -> bool:
        """Check if funder has any urgent deadlines"""
        return any(g.is_urgent() for g in self.grants)

    @property
    def next_deadline(self) -> Optional[datetime]:
        """Next upcoming deadline for this funder"""
        event = self.timeline.next_deadline
        return event.date if event else None

    @property
    def grant_count(self) -> int:
        """Total number of grants"""
        return len(self.grants)

    @property
    def document_count(self) -> int:
        """Total number of historical documents"""
        return len(self.documents)


@dataclass(frozen=True)
class DashboardData:
    """
    Complete dashboard data structure

    REPLACES: Implicit dict from GrantService.get_dashboard_data()

    Explicit contract for dashboard view with type-safe access.
    """
    grants: List['Grant']              # Filtered/sorted grants for display
    statistics: GrantStatistics        # Aggregated dashboard stats
    timeline: Timeline                 # Upcoming deadlines timeline

    # Filter state
    current_view: str                  # Current user filter ('All', 'David', etc.)
    applied_filters: dict              # Active filters

    # Metadata
    last_updated: datetime
    total_count: int                   # Total before filtering

    @property
    def has_urgent_items(self) -> bool:
        """Quick check for urgent attention needed"""
        return self.statistics.urgent_grants > 0 or self.statistics.overdue_grants > 0

    @property
    def filtered_count(self) -> int:
        """Number of grants after filtering"""
        return len(self.grants)
