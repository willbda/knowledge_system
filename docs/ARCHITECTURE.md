# Architecture Documentation: Grant Management System

**Created**: 2025-10-13
**Pattern**: Four-Layer Clean Architecture (CATEGORIAE/ETHICA/RHETORICA/POLITICA)
**Inspiration**: ten_week_goal_app proven patterns

---

## Core Architectural Principles

### **1. Dependency Direction (Enforce Strictly)**

```
CATEGORIAE (entities)     ← imports: NOTHING (Python stdlib only)
    ↑
ETHICA (business logic)   ← imports: entities only
    ↑
RHETORICA (repositories)  ← imports: entities + infrastructure
    ↑
POLITICA (infrastructure) ← imports: NOTHING (stdlib + sqlite3 only)
```

**Rule**: No layer depends on layers above it. Enforce with pre-commit hooks.

### **2. Zero Framework Coupling in Core**

| Layer | Allowed Imports | Forbidden Imports |
|-------|-----------------|-------------------|
| `data/entities/` | Python stdlib (dataclasses, datetime, typing) | pandas, Flask, SQLAlchemy, ANY framework |
| `data/business_logic/` | entities + stdlib | pandas, Flask, database libraries |
| `data/repositories/` | entities + infrastructure + stdlib | Flask, pandas (can return entities) |
| `data/services/` | entities + business_logic + repositories | Flask, pandas |
| `data/infrastructure/` | stdlib + sqlite3 ONLY | ALL frameworks and entities |

**Frameworks live ONLY in `app/`** (Flask routes, templates)

### **3. Explicit Contracts (No Implicit Dicts)**

```python
# ❌ FORBIDDEN - Implicit contract
def get_funder_data(bn: str) -> Dict[str, Any]:
    return {'name': '...', 'grants': [...]}  # What keys? What types?

# ✅ REQUIRED - Explicit value object
def get_funder_overview(bn: str) -> FunderOverview:
    return FunderOverview(funder=..., grants=...)  # Type-safe!
```

### **4. Pure Business Logic (Zero Mocks Required)**

```python
# Business logic functions must be testable without ANY mocks
def calculate_priority(grant: Grant) -> float:
    """Pure function - no database, no mocks, just math"""
    if not grant.deadline:
        return 0.0
    days = grant.days_until_deadline()
    return math.exp(-days / 30)

# Test: Just call it!
def test_priority_calculation():
    grant = Grant(bernie_number='BN000001', deadline=...)
    priority = calculate_priority(grant)
    assert 0.0 <= priority <= 1.0
```

---

## Layer Descriptions

### **CATEGORIAE: `data/entities/`**
**What things ARE** - Pure domain knowledge

- **Grant** - A grant opportunity from Writing Schedule
- **Funder** - An organization identified by Bernie Number
- **DevTeamMember** - A grant writer/developer
- **Value Objects** - FunderOverview, GrantStatistics, Timeline

**Constraints**:
- Zero external dependencies (dataclasses, datetime, typing ONLY)
- Validation happens at construction (`__post_init__`)
- Domain logic methods (e.g., `grant.is_urgent()`)
- NO database knowledge, NO storage concerns

### **ETHICA: `data/business_logic/` + `data/services/`**
**How things SHOULD behave** - Rules and orchestration

**Pure Functions** (`data/business_logic/`):
- `calculate_priority(grant: Grant) -> float`
- `build_timeline(grants: List[Grant]) -> Timeline`
- `calculate_statistics(grants: List[Grant]) -> GrantStatistics`

**Services** (`data/services/`):
- Orchestrate repositories + business logic
- Return value objects (never dicts!)
- Framework-independent (no Flask)
- Example: `FunderService.get_funder_overview() -> FunderOverview`

### **RHETORICA: `data/repositories/`**
**Translation between domains**

- `GrantRepository: Grant ↔ dict ↔ database`
- `FunderRepository: Funder ↔ dict ↔ database`
- Base class: `StorageService[T]` with generic operations
- Explicit `_to_dict()` and `_from_dict()` translation

### **POLITICA: `data/infrastructure/`**
**How things ARE DONE** - Generic storage primitives

- `Database` class: Generic SQLite operations
- `insert(table: str, records: List[dict]) -> List[int]`
- `query(table: str, filters: dict) -> List[dict]`
- Zero knowledge of Grant/Funder/any domain entity
- Works with primitives: str, dict, int, List

---

## File Organization

```
data/
├── entities/                    # CATEGORIAE
│   ├── __init__.py
│   ├── grant.py                 # @dataclass Grant
│   ├── funder.py                # @dataclass Funder
│   ├── dev_team.py              # @dataclass DevTeamMember
│   └── value_objects.py         # FunderOverview, Timeline, Statistics
│
├── business_logic/              # ETHICA (pure functions)
│   ├── __init__.py
│   ├── priority_calculation.py
│   ├── timeline_building.py
│   └── statistics.py
│
├── services/                    # ETHICA (orchestration)
│   ├── __init__.py
│   ├── funder_service.py
│   ├── grant_service.py
│   └── dashboard_service.py
│
├── repositories/                # RHETORICA
│   ├── __init__.py
│   ├── base_repository.py       # Generic StorageService[T]
│   ├── grant_repository.py
│   └── funder_repository.py
│
└── infrastructure/              # POLITICA
    ├── __init__.py
    ├── database.py              # Generic Database class
    └── schemas/
        ├── grants.sql
        └── funders.sql
```

---

## Enforcement Mechanisms

### **Pre-commit Hook: Import Validation**

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check entities/ imports nothing forbidden
if grep -r "^import pandas\|^from pandas\|^import flask" data/entities/*.py; then
    echo "ERROR: entities/ must not import frameworks!"
    exit 1
fi

# Check infrastructure/ imports no entities
if grep -r "from data.entities\|from ..entities" data/infrastructure/*.py; then
    echo "ERROR: infrastructure/ must not import entities!"
    exit 1
fi

echo "✅ Architecture boundaries validated"
```

### **Type Checking: mypy**

```ini
# mypy.ini
[mypy]
strict = True
disallow_untyped_defs = True
disallow_any_unimported = True

# Enforce no pandas in entities
[mypy-data.entities.*]
disallow_any_decorated = True
```

---

## Testing Strategy by Layer

### **Entities (Unit Tests)**
```python
# tests/unit/entities/test_grant.py
def test_grant_urgency_without_database():
    """Pure entity logic - zero mocks"""
    grant = Grant(
        bernie_number='BN000227',
        funder_name='Test Foundation',
        deadline=datetime.now() + timedelta(days=5)
    )
    assert grant.is_urgent() == True
```

### **Business Logic (Unit Tests)**
```python
# tests/unit/business_logic/test_priority.py
def test_priority_calculation_pure_function():
    """Pure function - zero mocks"""
    grant = Grant(bernie_number='BN000001', deadline=...)
    priority = calculate_priority(grant)
    assert 0.0 <= priority <= 1.0
```

### **Repositories (Integration Tests)**
```python
# tests/integration/repositories/test_grant_repository.py
def test_grant_round_trip(test_database):
    """Test entity → dict → database → entity"""
    original = Grant(bernie_number='BN000001', ...)

    repo = GrantRepository(test_database)
    saved = repo.save(original)
    retrieved = repo.get_by_id(saved.id)

    assert retrieved.bernie_number == original.bernie_number
```

### **Services (Unit Tests with Mock Repositories)**
```python
# tests/unit/services/test_funder_service.py
def test_funder_overview_orchestration(mock_repos):
    """Test orchestration logic with mocks"""
    mock_funder_repo, mock_grant_repo = mock_repos

    mock_funder_repo.get_by_bn.return_value = Funder(...)
    mock_grant_repo.get_by_funder_bn.return_value = [Grant(...)]

    service = FunderService(mock_funder_repo, mock_grant_repo)
    overview = service.get_funder_overview('BN000227')

    assert isinstance(overview, FunderOverview)
```

---

## Migration Strategy

See `architecture_refactor_plan.md` for complete 5-phase migration from old dashboard.

**Key principle**: Build new system alongside old, migrate data once patterns are proven.

---

## Success Criteria

### **Code Quality**
- ✅ Zero pandas/DataFrame in `data/` (except legacy)
- ✅ Entities have zero external dependencies
- ✅ Business logic testable without mocks
- ✅ All tests pass with real objects

### **Architecture Validation**
- ✅ Can swap Flask → FastAPI by changing `app/` only
- ✅ Can swap SQLite → Postgres by changing `infrastructure/` only
- ✅ Can test business logic without database
- ✅ Pre-commit hooks prevent violations

---

# 1. Data Sources:
- Writing Schedule (WS)
  - Development team tool
  - Accessible via API (Google Sheets)
  - Can eventually be taken offline or stored internal to this system if full CRUD is reliable 
  - Main entry point for the most dynamic data entries
  - Hundreds of records plus an archive
  - **Key data:**
    - funders
    - opportunities / tasks
    - due dates
    - dev team lead
    - statuses
    - request amount
    - award amount
    - freeform notes
    - opportunity type
    - communities supported
    - fiscal year
- Filesystem, nested directories
  - Can be ingested via GREP
  - Next stage is spaCy analysis (on hold)
    - **Key data:**
      - rich files that are useful for historical view, tracking etc.
      - drafts
      - final submissions
      - languages
- CRM
  - funders
  - awards
  - applications
  - "notes" -> application lifecycle
        "Note": "\r\n7/11/25 - Application submitted\r\n7/17/2025 - Application denied"
- IRS / Nonprofit explorer
  - **Key data:**
    - Public tax information including giving amounts
\

# 2 Relations (db tables)

1. Funders
2. Aliases(?)
3. Tasks
4. Dev Team Leads
5. Files
6. Subtask Relations (separate tables)
   1. Proposals
   2. LOIs(?)
   3. Reports
7. ...

# 3 What is an opportunity?

CRM stores them as 'notes' but this is a free-form field that isn't an ideal. We want to capture the lifecycle that stretches from prospect to report, but we don't know ahead of time which prospects move to applications and which applications move to reports. 
So perhaps the proposals, reports, etc. tables have to have an opportunities field, where opportunity is an fk for an opportunities table that is populated by any prior stage? 
What makes an opportunity distinguishable? This might largely be a manual distinction. We can pre-populate an opportunity for each proposal. And then as more details are added to the writing schedule it is a shallow manual task to say that a given task is a new opportunity? Or else - we do know that opportunities are per funder, so we can surface all the opportunities for a given funder and when adding a new funder task it should be easy to ask, does this task belong to a pre-existing opportunity or is it a part of a new opportunity. ... 

# 4 Goal

We think largely in terms of funders and opportunities. The writing schedule has atomic records of tasks and was largely designed to support calendaring and planning for due dates. With more data and more work in the schedule it would be beneficial to have a more sophisticated understanding of opportunities as higher order projects that relate a number of tasks. *moreover* with opportunities properly articulated, it becomes possible to tie documents to opportunities as a whole, and then tasks and opportunity details can function along with document locations to make document text queriably by opportunity details (e.g. it becomes trivial to quary the text of all recovery corps grants.)