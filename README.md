# Grant Management System

**Clean Architecture Implementation**
**Pattern**: Blueprint Architecture with 3NF+ Normalization
**Started**: 2025-10-13 | **Refactored**: 2025-10-30

---

## Purpose

A grant management system built with clean architecture principles from day one.

Manages grant opportunities, funders, scheduled tasks, and development team assignments with:
- **Blueprint pattern**: Natural keys → Foreign keys (separation of concerns)
- **Zero framework coupling** in business logic
- **Pure domain entities** testable in isolation
- **3NF+ normalized database** with single source of truth
- **Composition over inheritance** for scheduled task entities

---

## Architecture

Four-layer clean architecture with strict dependency rules:

```
┌─────────────────────────────────────┐
│  CATEGORIAE (data/basic_entities/,  │  ← imports: NOTHING
│  data/composite_entities/)          │
│  Pure domain models                 │
└─────────────────────────────────────┘
              ↑
┌─────────────────────────────────────┐
│  ETHICA (data/business_logic/,      │  ← imports: entities only
│           data/services/)           │
│  Rules & orchestration              │
└─────────────────────────────────────┘
              ↑
┌─────────────────────────────────────┐
│  RHETORICA (data/repositories/,     │  ← imports: entities + infrastructure
│              data/adapters/)        │
│  Entity ↔ storage translation       │
└─────────────────────────────────────┘
              ↑
┌─────────────────────────────────────┐
│  POLITICA (data/infrastructure/)    │  ← imports: NOTHING (stdlib only)
│  Generic storage operations         │
└─────────────────────────────────────┘
```

See [docs/final_architecture_summary.md](docs/final_architecture_summary.md) for complete architectural documentation.

---

## Project Structure

```
grant_management_system/
├── data/
│   ├── basic_entities/      # Core domain models (Funder, DevTeamMember, ScheduledTasks)
│   ├── composite_entities/  # Aggregate entities (Opportunity)
│   ├── services/            # Orchestration & decomposition
│   │   ├── writing_schedule_decomposer.py  # Blueprint creation
│   │   ├── orchestrator.py                  # FK resolution & entity construction
│   │   ├── status_semantics.py              # Status business rules
│   │   └── data_parsing.py                  # Shared parsing utilities
│   ├── adapters/            # External data translation (WritingScheduleRow)
│   ├── business_logic/      # Pure functions (coming soon)
│   ├── repositories/        # Entity ↔ database translation (coming soon)
│   └── infrastructure/      # Generic storage (coming soon)
│
├── tests/
│   ├── unit/
│   │   ├── entities/        # Entity tests
│   │   └── services/        # Service layer tests
│   └── integration/         # Coming soon
│
├── docs/                    # Architecture & design documentation
│   ├── final_architecture_summary.md
│   ├── entity_relationships.md
│   └── data_transformation_pipeline.md
│
└── scripts/                 # Coming soon
```

---

## Core Entities

### **Funder** (`data/basic_entities/funder.py`)
Organization identified by Bernie Number

```python
@dataclass
class Funder:
    bernie_number: str      # BN000XXX format (validated at construction)
    canonical_name: str     # Official name
    ein: Optional[str]      # 9-digit Tax ID
```

### **DevTeamMember** (`data/basic_entities/dev_team.py`)
Development team member

```python
@dataclass
class DevTeamMember:
    name: str               # Full name (unique identifier)

    def matches_name(self, name: str) -> bool:
        """Case-insensitive name comparison"""
        return self.name.lower() == name.lower()
```

### **ScheduledTask Entities** (`data/basic_entities/schedule_task.py`)
**Composition over Inheritance**: Each task entity contains a TaskCore

```python
@dataclass
class TaskCore:
    """Shared scheduling data for all task types"""
    task_id: str                    # Unique identifier
    task_type: str                  # "LOI", "Proposal", "Report", "Reminder"
    bernie_number: str              # FK to Funder (3NF normalized)
    status_id: int                  # FK to raw_statuses.id
    deadline: datetime              # When task is due
    owner_id: Optional[int]         # FK to dev_team_members.id
    last_modified: datetime
    fiscal_year: Optional[str]      # Program fields (normalized)
    program_area: Optional[str]
    initiative: Optional[str]
    opportunity_id: Optional[str]   # Link to opportunity (if exists)

# Type-specific entities using composition
@dataclass
class LOI:
    core: TaskCore
    notification_date: Optional[datetime]
    amount_requested: Optional[Decimal]
    related_proposal_id: Optional[str]  # If LOI led to proposal
    dev_team_notes: Optional[str]

@dataclass
class Proposal:
    core: TaskCore
    amount_requested: Optional[Decimal]
    award_amount: Optional[Decimal]
    submission_date: Optional[datetime]
    notification_date: Optional[datetime]
    grant_start_date: Optional[datetime]
    grant_end_date: Optional[datetime]
    communities: Optional[str]
    members_funded: Optional[str]
    model_funded: Optional[str]
    dev_team_notes: Optional[str]
    grant_goals: Optional[str]

@dataclass
class Report:
    core: TaskCore
    report_type: str                    # "Final Report", "Interim Report"
    related_proposal_id: Optional[str]  # Grant being reported on
    submission_date: Optional[datetime]
    reporting_period_start: Optional[datetime]
    reporting_period_end: Optional[datetime]
    acknowledgment_needs: Optional[str]
    dev_team_notes: Optional[str]

@dataclass
class Reminder:
    core: TaskCore
    reminder_note: Optional[str]    # What this reminder is about
```

## Blueprint Pattern: Data Transformation Pipeline

**WritingScheduleRow → Blueprint → Resolution → Entity**

The decomposer creates blueprints with natural keys, the orchestrator resolves foreign keys:

```python
from data.services.writing_schedule_decomposer import decompose_row
from data.services.orchestrator import resolve_and_build_entity

# Step 1: Decompose row into blueprint with natural keys
bernie_number, canonical_name, owner_name, raw_status, task_blueprint = decompose_row(row)

# bernie_number: "BN0002E1" (natural key)
# canonical_name: "Dobbs Foundation"
# owner_name: "Jane Doe" (natural key)
# raw_status: "Active Development" (natural key)
# task_blueprint: LOIBlueprint with natural keys

# Step 2: Orchestrator resolves natural keys → foreign keys
resolution = orchestrator.resolve_foreign_keys(bernie_number, canonical_name, owner_name, raw_status)
# resolution.status_id: 42 (FK to raw_statuses)
# resolution.owner_id: 7 (FK to dev_team_members)

# Step 3: Build entity with resolved FKs
entity = orchestrator.build_entity_from_blueprint(task_blueprint, resolution)
# entity: LOI with core.status_id=42, core.owner_id=7, core.bernie_number="BN0002E1"
```

See [docs/data_transformation_pipeline.md](docs/data_transformation_pipeline.md) for complete workflow.

---

## Testing

### **Run All Tests**
```bash
pytest -v
```

### **Test Entities**
```bash
pytest tests/unit/entities/ -v
```
- Funder & FunderAlias construction/validation
- DevTeamMember name matching
- Document file path validation
- ScheduledTask composition & relationships

### **Test Services (Blueprint Decomposition)**
```bash
pytest tests/unit/services/ -v
```
- Blueprint creation from WritingScheduleRow
- LOI, Proposal, Report, Reminder decomposition
- Full integration tests

---

## Development Setup

### **Prerequisites**
- Python 3.11+
- Poetry (for dependency management)

### **Install Dependencies**
```bash
poetry install
```

### **Run Tests**
```bash
poetry run pytest
```

### **Type Checking**
```bash
poetry run mypy data/
```

---

## Architectural Principles

### **Blueprint Pattern**
1. **Decomposer**: Creates blueprints with natural keys (strings like "Jane Doe", "Active")
2. **Orchestrator**: Resolves natural keys → foreign keys (integers like user_id=7)
3. **Entities**: Built with resolved FKs, ready for database persistence

### **3NF+ Normalization**
- Single source of truth for each data point
- `bernie_number` normalized to `scheduled_tasks` table (not duplicated)
- Program fields (`fiscal_year`, `program_area`, `initiative`) normalized to `scheduled_tasks`
- Funder names resolved via `funder_aliases` table

### **Status Semantics in Code**
- Raw status text stored with auto-increment ID (lossless)
- Business rules in `status_semantics.py`, NOT in database
- Focus on signal: "Is this actionable? When is it due? Was it successful?"

### **Import Rules**

1. **`data/basic_entities/`** - NO external imports (stdlib only)
2. **`data/services/`** - Imports entities only
3. **`data/infrastructure/`** - NO entity imports (generic operations)
4. **Frameworks (pandas, Flask)** - ONLY in `app/`

### **Testing Philosophy**

- **Entities**: Pure logic, zero mocks
- **Services**: Unit tests with real data
- **Repositories**: Integration tests with database (coming soon)

---

## Key Principles

1. **Framework Independence** - Core logic has zero framework dependencies
2. **Composition over Inheritance** - TaskCore as composition component
3. **Blueprint Pattern** - Separation of concerns (natural keys vs foreign keys)
4. **3NF+ Normalization** - Single source of truth, no duplication
5. **Clear Boundaries** - Layer violations prevented by import rules

---

## Status

**Phase 0**: ✅ Repository structure established
**Phase 1**: ✅ Basic entities with composition architecture
**Phase 1.5**: ✅ Blueprint pattern & decomposition pipeline
**Phase 2**: ⏳ Repository layer (upsert logic with FK resolution)
**Phase 3**: ⏳ Business logic and services
**Phase 4**: ⏳ Flask application layer
**Phase 5**: ⏳ Data migration from old dashboard

---

## References

- **Architecture**: [docs/final_architecture_summary.md](docs/final_architecture_summary.md)
- **Entity Relationships**: [docs/entity_relationships.md](docs/entity_relationships.md)
- **Data Pipeline**: [docs/data_transformation_pipeline.md](docs/data_transformation_pipeline.md)
- **CHANGELOG**: [CHANGELOG.md](CHANGELOG.md)

---

**Built with principled architecture from day one.**
