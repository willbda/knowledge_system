# Layer-by-Layer Implementation Roadmap

**Goal**: Achieve feature parity with Grantwriting Knowledge Dashboard using clean architecture.

**Strategy**: Complete each architectural layer systematically, validating with real data at each milestone.

---

## Layer 1: categoriae/ (Domain Entities - Data Contracts)

**Purpose**: Pure data structures with validation. Zero framework dependencies. Entities define "what things ARE."

### Current State

| Entity | Exists | Validation | Complete | Issues |
|--------|--------|------------|----------|--------|
| `Funder` | ✅ | ✅ | 95% | Missing FunderAlias |
| `Opportunity` | ✅ | ❌ | 60% | Validation removed |
| `DevTeamMember` | ✅ | ✅ | 95% | Minimal |
| `Proposal` | ✅ | ⚠️ | 80% | Status should be required |
| `Report` | ✅ | ⚠️ | 80% | OK |
| `LOI` | ✅ | ✅ | 80% | OK |
| `Prospect` | ⚠️ | ⚠️ | 50% | **Missing opportunity_id FK** |
| `Document` | ⚠️ | ⚠️ | 40% | **Missing opportunity/task FKs** |
| `FunderAlias` | ❌ | ❌ | 0% | Not implemented |

### Value Objects

| Value Object | Exists | Complete | Issues |
|--------------|--------|----------|--------|
| `OpportunityOverview` | ✅ | 80% | Defined, needs testing |
| `TaskSummary` | ✅ | 60% | success_rate logic broken |
| `Timeline` | ❌ | 0% | Not implemented |
| `TimelineEvent` | ❌ | 0% | Not implemented |
| `GrantStatistics` | ❌ | 0% | Not implemented |
| `FunderStatistics` | ❌ | 0% | Not implemented |

### Tasks to Complete

#### High Priority (Blockers)
- [ ] **FIX**: Add `opportunity_id: int` to `Prospect` entity
- [ ] **FIX**: Add `opportunity_id`, `proposal_id`, `report_id`, `loi_id` to `Document` entity
- [ ] **FIX**: Make `Proposal.status` required (not Optional)
- [ ] **FIX**: Add validation back to `Opportunity` entity

#### Medium Priority
- [ ] Implement `FunderAlias` entity for alias management
- [ ] Implement `Timeline` and `TimelineEvent` value objects
- [ ] Implement `GrantStatistics` value object
- [ ] Implement `FunderStatistics` value object
- [ ] Fix `TaskSummary.success_rate` calculation

#### Testing
- [ ] Write tests for `Opportunity` (construction, validation)
- [ ] Write tests for `Proposal` (~20 tests)
- [ ] Write tests for `Report` (~15 tests)
- [ ] Write tests for `LOI` (~15 tests)
- [ ] Write tests for `Prospect` (~15 tests)
- [ ] Write tests for `Document` (~10 tests)
- [ ] Write tests for all value objects

**Target**: 120+ unit tests, all passing, 100% coverage of entities

---

## Layer 2: politica/ (Infrastructure - Generic Storage)

**Purpose**: Generic database operations. Zero knowledge of domain entities. Provides primitives for rhetorica layer.

### Current State
- ❌ No implementation exists
- 🔲 Database class not started
- 🔲 Schema files not created
- 🔲 No connection management

### What Old Dashboard Has
```python
# Old: Fragmented database access
sqlite3.connect('bernie_registry.db')
sqlite3.connect('writing_schedule.db')
sqlite3.connect('persistent_main.db')
sqlite3.connect('grantwriting_documents.db')
# Each service manages its own connection
```

### What We Need

#### Generic Database Class
```python
# politica/database.py
class Database:
    """Generic SQLite operations - works for ANY table/entity."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def insert(self, table: str, records: List[dict]) -> List[int]:
        """Insert records, return generated IDs."""

    def query(self, table: str, filters: Optional[dict] = None) -> List[dict]:
        """Query table, return dicts."""

    def update(self, table: str, record_id: int, updates: dict) -> bool:
        """Update single record."""

    def delete(self, table: str, record_id: int) -> bool:
        """Delete single record."""
```

#### SQL Schema Files

Create in `politica/schemas/`:

```
politica/
└── schemas/
    ├── funders.sql
    ├── opportunities.sql
    ├── proposals.sql
    ├── reports.sql
    ├── lois.sql
    ├── prospects.sql
    ├── dev_team.sql
    ├── documents.sql
    └── cache.sql
```

Each schema should include:
- CREATE TABLE statements
- Indexes for common queries
- CHECK constraints for enums
- Foreign key definitions

### Tasks to Complete

#### Infrastructure
- [ ] Create `Database` class with generic CRUD operations
- [ ] Implement connection pooling/management
- [ ] Create schema application logic (apply_schema, validate_schema)
- [ ] Implement transaction support

#### Schemas
- [ ] Write `funders.sql` schema
- [ ] Write `opportunities.sql` schema
- [ ] Write `proposals.sql` schema
- [ ] Write `reports.sql` schema
- [ ] Write `lois.sql` schema
- [ ] Write `prospects.sql` schema
- [ ] Write `dev_team.sql` schema
- [ ] Write `documents.sql` schema with FTS5
- [ ] Write `cache.sql` schema

#### Testing
- [ ] Test Database class with temporary SQLite file
- [ ] Test insert/query/update/delete operations
- [ ] Test transaction rollback
- [ ] Test schema application

**Target**: Generic Database class working for all entities, all schemas applied

---

## Layer 3: rhetorica/ (Repositories - Translation Layer)

**Purpose**: Translate between domain entities (categoriae) and storage (politica). Knows both entity structure and table schema.

### Current State
- ❌ No repositories implemented
- 🔲 No StorageService base class
- 🔲 No entity-specific repositories

### What Old Dashboard Has
```python
# Old: Direct pandas DataFrame manipulation in services
df = pd.read_sql("SELECT * FROM writing_schedule_current", conn)
# Services work directly with DataFrames, no entity translation
```

### What We Need

#### Base Repository Pattern
```python
# rhetorica/storage_service.py
class StorageService(ABC, Generic[T]):
    """Base class for all repositories."""

    def __init__(self, db: Database, table_name: str):
        self.db = db
        self.table_name = table_name

    def save(self, entity: T) -> T:
        """Insert or update entity, return with populated ID."""
        entity_dict = self._to_dict(entity)
        if entity.id is None:
            # Insert
            ids = self.db.insert(self.table_name, [entity_dict])
            entity.id = ids[0]
        else:
            # Update
            self.db.update(self.table_name, entity.id, entity_dict)
        return entity

    def get_by_id(self, id: int) -> Optional[T]:
        """Retrieve entity by ID."""
        records = self.db.query(self.table_name, {'id': id})
        if not records:
            return None
        return self._from_dict(records[0])

    def get_all(self, filters: Optional[dict] = None) -> List[T]:
        """Retrieve all matching entities."""
        records = self.db.query(self.table_name, filters)
        return [self._from_dict(record) for record in records]

    @abstractmethod
    def _to_dict(self, entity: T) -> dict:
        """Convert entity → dict for storage."""

    @abstractmethod
    def _from_dict(self, data: dict) -> T:
        """Convert dict → entity after retrieval."""
```

#### Entity-Specific Repositories

Each entity needs a repository with:
- Generic CRUD operations (from base class)
- Domain-specific queries (custom methods)

**Example**:
```python
# rhetorica/proposal_repository.py
class ProposalRepository(StorageService[Proposal]):
    table_name = 'proposals'

    def _to_dict(self, proposal: Proposal) -> dict:
        # Entity → database dict

    def _from_dict(self, data: dict) -> Proposal:
        # Database dict → entity

    # Domain-specific queries
    def get_by_opportunity(self, opportunity_id: int) -> List[Proposal]:
        return self.get_all({'opportunity_id': opportunity_id})

    def get_urgent(self, threshold_days: int = 7) -> List[Proposal]:
        # Query proposals with deadlines within threshold

    def get_by_dev_lead(self, dev_lead_id: int) -> List[Proposal]:
        return self.get_all({'dev_lead_id': dev_lead_id})
```

### Tasks to Complete

#### Base Infrastructure
- [ ] Create `StorageService[T]` generic base class
- [ ] Implement save/get_by_id/get_all methods
- [ ] Add batch operations (save_many, delete_many)

#### Entity Repositories
- [ ] Implement `FunderRepository`
  - [ ] get_by_bernie_number
  - [ ] get_by_name (fuzzy matching via ethica layer)
- [ ] Implement `OpportunityRepository`
  - [ ] get_by_funder
  - [ ] get_with_tasks (return OpportunityOverview)
- [ ] Implement `ProposalRepository`
  - [ ] get_by_opportunity
  - [ ] get_by_dev_lead
  - [ ] get_urgent
  - [ ] get_by_status
- [ ] Implement `ReportRepository`
  - [ ] get_by_opportunity
  - [ ] get_overdue
- [ ] Implement `LOIRepository`
  - [ ] get_by_opportunity
  - [ ] get_invited
- [ ] Implement `ProspectRepository`
  - [ ] get_by_opportunity
- [ ] Implement `DevTeamRepository`
  - [ ] get_by_name
- [ ] Implement `DocumentRepository`
  - [ ] get_by_opportunity
  - [ ] full_text_search (via FTS5)

#### Testing
- [ ] Integration tests for each repository with real SQLite
- [ ] Test round-trip (entity → save → retrieve → entity)
- [ ] Test domain-specific queries
- [ ] Test foreign key enforcement

**Target**: All entities can be saved and retrieved, all queries working

---

## Layer 4: adapters/ (External Data Source Integration)

**Purpose**: Translate external data formats → domain entities. One adapter per external system.

### Current State

| Adapter | Schema | Parser | Complete | Issues |
|---------|--------|--------|----------|--------|
| Writing Schedule | ✅ | ✅ | 90% | Missing dev_lead lookup |
| CRM | ❌ | ❌ | 0% | Not started |
| File System | ❌ | ❌ | 0% | Not started |

### What Old Dashboard Has
```python
# Old: Direct integration scattered across services
from SHARED_TOOLS.writing_schedule import fetch_writing_schedule
df = fetch_writing_schedule()  # Returns pandas DataFrame

# CRM integration
from data.storage.external.bloomerang_loader import fetch_constituent
data = fetch_constituent(cid=123)  # Returns dict
```

### What We Need

#### Writing Schedule Adapter (90% Complete)
```python
# adapters/writing_schedule/schema.py ✅
@dataclass
class WritingScheduleRow:
    task_id: str
    funder: Optional[str]
    opportunity: Optional[str]
    type: Optional[str]
    # ... 47 fields

# adapters/writing_schedule/parser.py ✅
def parse_row(row: WritingScheduleRow) -> List[Entity]:
    # Dispatches to create Proposal/Report/LOI/Prospect
```

**Gap**: Parser doesn't handle dev_lead_id lookup (needs DevTeamRepository)

#### CRM Adapter (0% Complete)
```python
# adapters/constituent_relationship_manager/schema.py 🔲
@dataclass
class BloomerangConstituent:
    cid: int
    name: str
    # ... fields from Bloomerang API

# adapters/constituent_relationship_manager/parser.py 🔲
def parse_constituent(constituent: BloomerangConstituent) -> Funder:
    # Map CRM data → Funder entity
```

#### File System Adapter (0% Complete)
```python
# adapters/file_system/scanner.py 🔲
def scan_directory(path: str) -> List[Document]:
    # Discover files, extract metadata → Document entities
```

### Tasks to Complete

#### Writing Schedule Adapter
- [ ] Add dev_lead lookup to parser (requires DevTeamRepository)
- [ ] Handle "Reminder" task type (currently ignored)
- [ ] Add comprehensive tests for type dispatch

#### CRM Adapter
- [ ] Create `BloomerangConstituent` schema
- [ ] Create parser: CRM → Funder entity
- [ ] Handle alias extraction from CRM names
- [ ] Test with sample Bloomerang data

#### File System Adapter
- [ ] Create file scanner for fundraising/ directory
- [ ] Extract metadata (file size, modified date, type)
- [ ] Match files to Bernie Numbers (fuzzy or exact)
- [ ] Create Document entities

#### Testing
- [ ] Test WS parser with all task types
- [ ] Test WS parser with edge cases (missing fields, invalid dates)
- [ ] Test CRM parser with sample data
- [ ] Test file scanner with sample directory

**Target**: All adapters can convert external data → domain entities

---

## Layer 5: ethica/ (Business Logic - Pure Functions)

**Purpose**: Domain calculations and rules. Pure functions with no side effects. Zero knowledge of storage or frameworks.

### Current State
- ❌ No business logic implemented
- 🔲 No priority calculation
- 🔲 No urgency detection
- 🔲 No statistics aggregation

### What Old Dashboard Has
```python
# Old: Business logic scattered in services and models
# data/models/priority_calculator.py (working algorithm)
def calculate_priority(deadline, status, amount):
    # Multi-factor asymptotic formula

# data/models/statistics_calculator.py
def calculate_statistics(df):
    # Aggregations on DataFrame
```

### What We Need

Pure functions organized by domain concern:

#### Priority & Urgency
```python
# ethica/priority_calculation.py
def calculate_priority(proposal: Proposal) -> float:
    """
    Multi-factor priority score (0.0 to 1.0).
    Pure function - same inputs = same outputs.
    """

def rank_tasks(tasks: List[Union[Proposal, Report, LOI]]) -> List[Task]:
    """Sort tasks by priority descending."""

def is_urgent(task: Union[Proposal, Report, LOI], threshold_days: int = 7) -> bool:
    """Check if deadline within threshold."""

def is_overdue(task: Union[Proposal, Report, LOI]) -> bool:
    """Check if past deadline."""

def days_until_deadline(task: Union[Proposal, Report, LOI]) -> Optional[int]:
    """Calculate days remaining (negative if overdue)."""
```

#### Statistics Aggregation
```python
# ethica/statistics.py
def calculate_proposal_statistics(proposals: List[Proposal]) -> ProposalStatistics:
    """Aggregate counts, amounts, success rate."""

def calculate_opportunity_statistics(opportunity: OpportunityOverview) -> OpportunityStatistics:
    """Cross-task aggregations for an opportunity."""

def calculate_funder_statistics(funder: Funder, opportunities: List[Opportunity]) -> FunderStatistics:
    """Historical engagement metrics."""
```

#### Timeline Generation
```python
# ethica/timeline_building.py
def build_timeline(tasks: List[Union[Proposal, Report, LOI]]) -> Timeline:
    """Generate chronological event list from tasks."""

def get_next_milestones(timeline: Timeline, count: int = 5) -> List[TimelineEvent]:
    """Extract next N upcoming events."""
```

#### Search & Matching
```python
# ethica/fuzzy_matching.py
def fuzzy_match_funder(query: str, funders: List[Funder], threshold: int = 80) -> List[Funder]:
    """Fuzzy name matching with RapidFuzz."""

def search_suggestions(query: str, entities: List[Any]) -> List[str]:
    """Generate ranked search suggestions."""
```

### Tasks to Complete

#### Priority & Urgency
- [ ] Implement `calculate_priority()` matching old algorithm
- [ ] Implement `rank_tasks()`
- [ ] Implement `is_urgent()`
- [ ] Implement `is_overdue()`
- [ ] Implement `days_until_deadline()`
- [ ] Test: Priority scores match old dashboard within 5%

#### Statistics
- [ ] Implement `calculate_proposal_statistics()`
- [ ] Implement `calculate_report_statistics()`
- [ ] Implement `calculate_opportunity_statistics()`
- [ ] Implement `calculate_funder_statistics()`
- [ ] Test: Aggregations match old dashboard exactly

#### Timeline
- [ ] Implement `build_timeline()`
- [ ] Implement `get_next_milestones()`
- [ ] Implement date range filtering
- [ ] Test: Timeline generation from mixed task types

#### Search
- [ ] Implement `fuzzy_match_funder()` with RapidFuzz
- [ ] Implement `search_suggestions()`
- [ ] Implement cross-entity search
- [ ] Test: Search results match old dashboard

**Target**: 100% unit test coverage, zero database/framework dependencies

---

## Layer 6: app/routes/ (HTTP Handlers - Thin Adapters)

**Purpose**: HTTP request/response handling. Thin layer over services. Framework-specific.

### Current State
- ❌ No routes implemented
- 🔲 No Flask app created

### What Old Dashboard Has
```python
# Old: 2,207 lines across routes/
app/routes/
├── main.py              # Dashboard, calendar, search
├── admin.py             # Admin interface
├── bn_admin.py          # Bernie Number admin
├── entities/
│   ├── funders.py       # Funder profiles (18 lines) ✅ Thin adapter
│   ├── grants.py        # Grant details (20 lines) ✅ Thin adapter
│   └── dev_team.py      # Team pages (48 lines)
└── api/
    ├── search.py        # Search endpoints
    ├── data.py          # Sync and pagination
    ├── system.py        # Health checks
    ├── documents.py     # Document access
    ├── entities.py      # Entity detail API
    └── rendering.py     # AJAX HTML rendering
```

### What We Need

Thin route handlers following pattern:
```python
@app.route('/proposals/<int:id>')
def proposal_detail(id: int):
    # 1. Get service (injected)
    proposal_service = get_proposal_service()

    # 2. Call service method
    proposal = proposal_service.get_proposal_detail(id)

    # 3. Render template
    return render_template('proposal_detail.html', proposal=proposal)
```

### Tasks to Complete

#### Core Routes
- [ ] Implement dashboard route (personalized view)
- [ ] Implement funder profile routes
- [ ] Implement opportunity detail routes
- [ ] Implement proposal detail routes
- [ ] Implement report detail routes
- [ ] Implement dev team workload routes

#### Search Routes
- [ ] Implement unified search endpoint
- [ ] Implement search suggestions endpoint
- [ ] Implement filter composition endpoint

#### Admin Routes
- [ ] Implement data sync endpoint
- [ ] Implement cache management
- [ ] Implement Bernie Number admin

#### API Routes
- [ ] Implement JSON API for proposals
- [ ] Implement JSON API for opportunities
- [ ] Implement pagination endpoints
- [ ] Implement health check endpoint

**Target**: All routes <50 lines, zero business logic, pure HTTP adapters

---

## Layer 7: app/templates/ (User Interface - Jinja2)

**Purpose**: HTML rendering. Uses data from routes, minimal logic.

### Current State
- ❌ No templates implemented

### What Old Dashboard Has
```
app/templates/
├── base.html            # Base layout with navigation
├── dashboard.html       # Main dashboard view
├── calendar.html        # Timeline/calendar view
├── funder_profile.html  # Funder detail page
├── grant_detail.html    # Proposal/report detail
├── admin/
│   ├── cache_status.html
│   └── sync.html
└── components/
    ├── summary_cards.html
    ├── task_table.html
    └── search_form.html
```

### What We Need

Templates following design system:
- Consistent layout (base.html inheritance)
- Component-based approach (reusable partials)
- Minimal logic (display only, no calculations)

### Tasks to Complete

#### Base Templates
- [ ] Create `base.html` with navigation
- [ ] Create design system CSS (tokens, components)
- [ ] Create responsive grid system

#### Dashboard Templates
- [ ] Create `dashboard.html` (personalized view)
- [ ] Create summary cards component
- [ ] Create task table component
- [ ] Create urgency indicators

#### Detail Templates
- [ ] Create `funder_profile.html`
- [ ] Create `opportunity_detail.html`
- [ ] Create `proposal_detail.html`
- [ ] Create `report_detail.html`

#### Search Templates
- [ ] Create search form component
- [ ] Create search results layout
- [ ] Create filter sidebar

**Target**: Complete UI matching old dashboard design, mobile-responsive

---

## Parity Validation Checklist

After completing all layers, validate feature parity:

### Data Integrity
- [ ] All 500 funders migrated from `bernie_registry.db`
- [ ] All 242 tasks migrated from `writing_schedule.db`
- [ ] All 3,600 documents migrated from `grantwriting_documents.db`
- [ ] All foreign keys enforced (no orphaned records)
- [ ] No data loss (reconciliation report clean)

### Functional Parity
- [ ] Dashboard loads personalized view per developer
- [ ] Priority scoring matches old algorithm (±5% tolerance)
- [ ] Search returns same results as old dashboard
- [ ] Statistics calculations match exactly
- [ ] Timeline view shows all deadlines correctly
- [ ] Document search finds correct files
- [ ] Bloomerang data integrates correctly

### Architectural Quality
- [ ] Zero framework imports in categoriae/ethica layers
- [ ] All business logic testable without database
- [ ] Generic Database class works for all entities
- [ ] All routes <50 lines (thin adapters)
- [ ] 100% test coverage on business logic
- [ ] Can swap Flask for CLI without changing core logic

### Performance
- [ ] Dashboard loads in <2 seconds
- [ ] Search returns in <500ms
- [ ] Full-text search across 3,600 docs in <1s
- [ ] No N+1 query problems

---

## Implementation Order

### Week 1: Foundation
1. Complete **categoriae/** (fix Prospect, Document, add tests)
2. Implement **politica/** (Database class, all schemas)
3. Start **rhetorica/** (base StorageService, 2-3 repositories)

### Week 2: Data Layer
4. Complete **rhetorica/** (all repositories, integration tests)
5. Migrate data: 500 funders + 242 tasks
6. Validation: Can store and retrieve all entities

### Week 3: Business Logic
7. Implement **ethica/** (priority, statistics, timeline)
8. Complete **adapters/** (WS parser with dev_lead lookup)
9. Test: Business logic matches old algorithm

### Week 4: External Integration
10. Implement CRM adapter
11. Implement file system scanner
12. Link 3,600 documents to opportunities

### Week 5: User Interface
13. Implement **app/routes/** (all HTTP handlers)
14. Implement **app/templates/** (all views)
15. End-to-end testing with real data

### Week 6: Polish & Cutover
16. Performance optimization
17. Final reconciliation with old dashboard
18. Deploy and cutover

---

## Questions for Discussion

1. **Phase 1 Priority**: Start with categoriae fixes or jump straight to politica/rhetorica?
2. **Testing Approach**: Write tests as we go, or batch after layer complete?
3. **Data Migration**: Migrate all data at once (Week 2) or incrementally per entity?
4. **Old Dashboard**: Keep running during development or cutover immediately?
5. **Repository Pattern**: Use generic StorageService[T] or hand-code each repository?

---

**Status**: Ready to begin implementation
**Next Milestone**: Complete categoriae layer (fix entities, add tests)
**Estimated Timeline**: 6 weeks to feature parity
