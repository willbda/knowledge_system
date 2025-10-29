 Categoriae Layer: Domain Entities

  Core Domain Entities

  # data/entities/funder.py
  from dataclasses import dataclass
  from typing import Optional, List
  from datetime import datetime

  @dataclass
  class Funder:
      """Represents a grant-making organization identified by Bernie 
  Number."""

      bernie_number: str
      canonical_name: str
      all_names: List[str]
      ein: Optional[str] = None
      bloomerang_api_cid: Optional[int] = None

      # System fields
      id: Optional[int] = None
      created_at: Optional[datetime] = None
      updated_at: Optional[datetime] = None

      def __post_init__(self):
          # Validate Bernie Number format
          if not self.bernie_number.startswith('BN'):
              raise ValueError(f"Bernie Number must start with 'BN': 
  {self.bernie_number}")
          if len(self.bernie_number) != 8:
              raise ValueError(f"Bernie Number must be 8 characters: 
  {self.bernie_number}")

          # Validate canonical name
          if not self.canonical_name or not self.canonical_name.strip():
              raise ValueError("Canonical name is required")

          # Ensure canonical name is in all_names
          if self.canonical_name not in self.all_names:
              self.all_names.insert(0, self.canonical_name)

          # Validate EIN if provided
          if self.ein is not None:
              if len(self.ein) != 9 or not self.ein.isdigit():
                  raise ValueError(f"EIN must be 9 digits: {self.ein}")

      def has_alias(self, name: str) -> bool:
          """Check if name is a known alias (case-insensitive exact 
  match)."""
          return name.lower() in [alias.lower() for alias in self.all_names]

      def matches_name(self, name: str, fuzzy: bool = False) -> bool:
          """Check if name matches any known alias."""
          if not fuzzy:
              return self.has_alias(name)
          else:
              name_lower = name.lower()
              return any(name_lower in alias.lower() for alias in
  self.all_names)


  # data/entities/opportunity.py
  from dataclasses import dataclass
  from typing import Optional
  from datetime import datetime

  @dataclass
  class Opportunity:
      """
      Minimal identity anchor for a funding relationship.
      Serves as a foreign key target for proposals, reports, etc.
      """

      funder_id: int
      opportunity_name: str
      description: Optional[str] = None
      status: str = 'active'

      # System fields
      id: Optional[int] = None
      created_at: Optional[datetime] = None
      updated_at: Optional[datetime] = None

      def __post_init__(self):
          if not self.opportunity_name or not self.opportunity_name.strip():
              raise ValueError("Opportunity name is required")

          if self.status not in ('active', 'closed', 'inactive'):
              raise ValueError(f"Invalid status: {self.status}")

      def is_active(self) -> bool:
          """Check if opportunity is currently active."""
          return self.status == 'active'


  # data/entities/dev_team.py
  from dataclasses import dataclass
  from typing import Optional
  from datetime import datetime

  @dataclass
  class DevTeamMember:
      """Represents a grant writer/developer assignable to tasks."""

      name: str
      email: Optional[str] = None
      role: Optional[str] = None

      # System fields
      id: Optional[int] = None
      created_at: Optional[datetime] = None
      updated_at: Optional[datetime] = None

      def __post_init__(self):
          if not self.name or not self.name.strip():
              raise ValueError("Name is required")

          if self.email and '@' not in self.email:
              raise ValueError(f"Invalid email format: {self.email}")

      def matches_name(self, name: str) -> bool:
          """Case-insensitive name comparison."""
          return self.name.lower() == name.lower()


  # data/entities/proposal.py
  from dataclasses import dataclass
  from typing import Optional
  from datetime import datetime

  @dataclass
  class Proposal:
      """Represents a full grant application with award potential."""

      opportunity_id: int
      task_id: Optional[str] = None

      # Assignment
      dev_lead_id: Optional[int] = None
      status: str = 'active'

      # Dates
      deadline: Optional[datetime] = None
      submission_date: Optional[datetime] = None
      notification_date: Optional[datetime] = None
      grant_start_date: Optional[datetime] = None
      grant_end_date: Optional[datetime] = None

      # Financial
      amount_requested: Optional[float] = None
      amount_awarded: Optional[float] = None

      # Proposal-specific
      proposal_type: Optional[str] = None        # 'new', 'renewal', 
  'continuation'
      fiscal_year: Optional[str] = None
      program_area: Optional[str] = None
      initiative: Optional[str] = None
      communities: Optional[str] = None

      # Notes
      dev_team_notes: Optional[str] = None

      # System fields
      id: Optional[int] = None
      created_at: Optional[datetime] = None
      updated_at: Optional[datetime] = None

      def __post_init__(self):
          # Validate status
          valid_statuses = ('active', 'submitted', 'awarded', 'denied',
  'withdrawn')
          if self.status not in valid_statuses:
              raise ValueError(f"Invalid status: {self.status}. Must be one 
  of {valid_statuses}")

          # Validate amounts
          if self.amount_requested is not None and self.amount_requested <
  0:
              raise ValueError(f"Amount requested cannot be negative: 
  {self.amount_requested}")

          if self.amount_awarded is not None and self.amount_awarded < 0:
              raise ValueError(f"Amount awarded cannot be negative: 
  {self.amount_awarded}")

          # Validate proposal type if provided
          if self.proposal_type is not None:
              valid_types = ('new', 'renewal', 'continuation')
              if self.proposal_type not in valid_types:
                  raise ValueError(f"Invalid proposal type: 
  {self.proposal_type}")

      def is_urgent(self, urgency_threshold_days: int = 7) -> bool:
          """Check if deadline is within urgency threshold."""
          if not self.deadline:
              return False
          days_until = self.days_until_deadline()
          return days_until is not None and 0 <= days_until <=
  urgency_threshold_days

      def is_overdue(self) -> bool:
          """Check if deadline has passed."""
          if not self.deadline:
              return False
          return datetime.now() > self.deadline

      def days_until_deadline(self) -> Optional[int]:
          """Calculate days until deadline (negative if overdue)."""
          if not self.deadline:
              return None
          delta = self.deadline - datetime.now()
          return delta.days

      def is_awarded(self) -> bool:
          """Check if proposal was awarded."""
          return self.status == 'awarded'


  # data/entities/report.py
  from dataclasses import dataclass
  from typing import Optional
  from datetime import datetime

  @dataclass
  class Report:
      """Represents a grant reporting requirement."""

      opportunity_id: int
      task_id: Optional[str] = None

      # Assignment
      dev_lead_id: Optional[int] = None
      status: str = 'active'

      # Dates
      deadline: Optional[datetime] = None
      submission_date: Optional[datetime] = None

      # Report-specific
      report_type: Optional[str] = None          # 'interim', 'final', 
  'annual', 'financial'
      reporting_period_start: Optional[datetime] = None
      reporting_period_end: Optional[datetime] = None
      fiscal_year: Optional[str] = None

      # Notes
      dev_team_notes: Optional[str] = None

      # System fields
      id: Optional[int] = None
      created_at: Optional[datetime] = None
      updated_at: Optional[datetime] = None

      def __post_init__(self):
          # Validate status
          valid_statuses = ('active', 'submitted', 'completed', 'overdue')
          if self.status not in valid_statuses:
              raise ValueError(f"Invalid status: {self.status}. Must be one 
  of {valid_statuses}")

          # Validate report type if provided
          if self.report_type is not None:
              valid_types = ('interim', 'final', 'annual', 'financial')
              if self.report_type not in valid_types:
                  raise ValueError(f"Invalid report type: 
  {self.report_type}")

          # Validate reporting period
          if self.reporting_period_start and self.reporting_period_end:
              if self.reporting_period_start > self.reporting_period_end:
                  raise ValueError("Reporting period start must be before 
  end")

      def is_urgent(self, urgency_threshold_days: int = 7) -> bool:
          """Check if deadline is within urgency threshold."""
          if not self.deadline:
              return False
          days_until = self.days_until_deadline()
          return days_until is not None and 0 <= days_until <=
  urgency_threshold_days

      def is_overdue(self) -> bool:
          """Check if deadline has passed and report not submitted."""
          if not self.deadline or self.status in ('submitted', 'completed'):
              return False
          return datetime.now() > self.deadline

      def days_until_deadline(self) -> Optional[int]:
          """Calculate days until deadline (negative if overdue)."""
          if not self.deadline:
              return None
          delta = self.deadline - datetime.now()
          return delta.days


  # data/entities/loi.py
  from dataclasses import dataclass
  from typing import Optional
  from datetime import datetime

  @dataclass
  class LOI:
      """Represents a Letter of Intent."""

      opportunity_id: int
      task_id: Optional[str] = None

      # Assignment
      dev_lead_id: Optional[int] = None
      status: str = 'active'

      # Dates
      deadline: Optional[datetime] = None
      submission_date: Optional[datetime] = None
      notification_date: Optional[datetime] = None

      # LOI-specific
      amount_requested: Optional[float] = None
      invited_to_apply: Optional[bool] = None    # None=pending, 
  True=invited, False=declined
      fiscal_year: Optional[str] = None
      program_area: Optional[str] = None

      # Notes
      dev_team_notes: Optional[str] = None

      # System fields
      id: Optional[int] = None
      created_at: Optional[datetime] = None
      updated_at: Optional[datetime] = None

      def __post_init__(self):
          # Validate status
          valid_statuses = ('active', 'submitted', 'invited', 'declined')
          if self.status not in valid_statuses:
              raise ValueError(f"Invalid status: {self.status}. Must be one 
  of {valid_statuses}")

          # Validate amount
          if self.amount_requested is not None and self.amount_requested <
  0:
              raise ValueError(f"Amount requested cannot be negative: 
  {self.amount_requested}")

      def is_urgent(self, urgency_threshold_days: int = 7) -> bool:
          """Check if deadline is within urgency threshold."""
          if not self.deadline:
              return False
          days_until = self.days_until_deadline()
          return days_until is not None and 0 <= days_until <=
  urgency_threshold_days

      def days_until_deadline(self) -> Optional[int]:
          """Calculate days until deadline."""
          if not self.deadline:
              return None
          delta = self.deadline - datetime.now()
          return delta.days


  # data/entities/prospect.py
  from dataclasses import dataclass
  from typing import Optional
  from datetime import datetime

  @dataclass
  class Prospect:
      """Represents an early-stage funding opportunity under research."""

      opportunity_id: int
      task_id: Optional[str] = None

      # Assignment
      dev_lead_id: Optional[int] = None
      status: str = 'active'

      # Dates
      target_deadline: Optional[datetime] = None

      # Prospect-specific
      estimated_amount: Optional[float] = None
      likelihood: Optional[str] = None           # 'high', 'medium', 'low'
      program_area: Optional[str] = None

      # Notes
      dev_team_notes: Optional[str] = None

      # System fields
      id: Optional[int] = None
      created_at: Optional[datetime] = None
      updated_at: Optional[datetime] = None

      def __post_init__(self):
          # Validate status
          valid_statuses = ('active', 'researching', 'pursuing', 'declined')
          if self.status not in valid_statuses:
              raise ValueError(f"Invalid status: {self.status}. Must be one 
  of {valid_statuses}")

          # Validate likelihood
          if self.likelihood is not None:
              valid_likelihoods = ('high', 'medium', 'low')
              if self.likelihood not in valid_likelihoods:
                  raise ValueError(f"Invalid likelihood: {self.likelihood}")

          # Validate amount
          if self.estimated_amount is not None and self.estimated_amount <
  0:
              raise ValueError(f"Estimated amount cannot be negative: 
  {self.estimated_amount}")


  # data/entities/document.py
  from dataclasses import dataclass, field
  from typing import Optional
  from datetime import datetime

  @dataclass(frozen=True)
  class Document:
      """
      Immutable value object representing a file linked to an opportunity.
      Frozen because documents shouldn't change identity after creation.
      """

      opportunity_id: int
      file_path: str
      file_name: str

      # Optional task links
      proposal_id: Optional[int] = None
      report_id: Optional[int] = None
      loi_id: Optional[int] = None

      # File metadata
      file_type: Optional[str] = None
      file_size: Optional[int] = None
      modified_date: Optional[datetime] = None

      # Content
      indexed_content: Optional[str] = None

      # System fields
      id: Optional[int] = None
      created_at: Optional[datetime] = None

      def __post_init__(self):
          if not self.file_path:
              raise ValueError("File path is required")
          if not self.file_name:
              raise ValueError("File name is required")

  Value Objects (Immutable Result Containers)

  # data/entities/value_objects.py
  from dataclasses import dataclass
  from typing import List, Optional
  from datetime import datetime

  @dataclass(frozen=True)
  class OpportunityOverview:
      """Complete view of an opportunity with all related tasks and 
  documents."""

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
          submitted = sum(1 for _ in range(self.total_proposals) if
  self.total_proposals > 0)
          if submitted == 0:
              return 0.0
          return (self.awarded_proposals / submitted) * 100

  Entity Module Exports

  # data/entities/__init__.py
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

