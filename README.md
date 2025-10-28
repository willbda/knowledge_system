# Grant Management System

**Clean Architecture Implementation**
**Pattern**: Four-Layer (CATEGORIAE/ETHICA/RHETORICA/POLITICA)
**Started**: 2025-10-13

---

## Purpose

A grant management system built with clean architecture principles from day one.

Manages grant opportunities, funders, and development team assignments with:
- **Zero framework coupling** in business logic
- **Pure domain entities** testable in isolation
- **Explicit contracts** via value objects
- **Generic storage layer** that works for any entity

---

## Architecture

Four-layer clean architecture with strict dependency rules:

```
┌─────────────────────────────────────┐
│  CATEGORIAE (data/entities/)        │  ← imports: NOTHING
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
│  RHETORICA (data/repositories/)     │  ← imports: entities + infrastructure
│  Entity ↔ storage translation       │
└─────────────────────────────────────┘
              ↑
┌─────────────────────────────────────┐
│  POLITICA (data/infrastructure/)    │  ← imports: NOTHING (stdlib only)
│  Generic storage operations         │
└─────────────────────────────────────┘
```

See `docs/ARCHITECTURE.md` for complete architectural documentation.

---

## Project Structure

```
grant_management_system/
├── data/
│   ├── entities/          # Pure domain models (Grant, Funder, etc.)
│   ├── business_logic/    # Pure functions (priority, statistics, etc.)
│   ├── services/          # Orchestration (FunderService, GrantService)
│   ├── repositories/      # Entity ↔ database translation
│   └── infrastructure/    # Generic storage (Database class)
│
├── app/
│   ├── routes/            # Flask HTTP adapters (thin, 15-25 lines)
│   └── templates/         # Jinja2 templates
│
├── tests/
│   ├── unit/              # Entities, business logic, services
│   ├── integration/       # Repositories + database
│   └── fixtures/          # Test data and utilities
│
├── scripts/               # Data migration, setup
└── docs/                  # Architecture documentation
```

---

## Core Entities

### **Grant** (`data/entities/grant.py`)
A grant opportunity from the Writing Schedule

```python
@dataclass
class Grant:
    bernie_number: str           # Funder identifier
    funder_name: str             # Funder name
    program_name: str            # Program/opportunity name
    deadline: Optional[datetime]
    dev_lead: Optional[str]      # Assigned developer
    amount_requested: Optional[float]
    status: str = 'active'

    def is_urgent(self) -> bool:
        """Domain logic - testable without database"""
        if not self.deadline:
            return False
        return (self.deadline - datetime.now()).days <= 7
```

### **Funder** (`data/entities/funder.py`)
An organization identified by Bernie Number

```python
@dataclass
class Funder:
    bernie_number: str      # BN000001 format
    canonical_name: str     # Official name
    all_names: List[str]    # Known aliases
    ein: Optional[str]      # Tax ID (9 digits)

    def has_alias(self, name: str) -> bool:
        """Check if name matches any known variant"""
        return name.lower() in [n.lower() for n in self.all_names]
```

---

## Testing

### **Run All Tests**
```bash
pytest
```

### **Test Entities (No Database)**
```bash
pytest tests/unit/entities/ -v
```

### **Test Business Logic (Pure Functions)**
```bash
pytest tests/unit/business_logic/ -v
```

### **Test Repositories (Integration with Database)**
```bash
pytest tests/integration/ -v
```

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

## Architectural Constraints

### **Import Rules (Enforced by Pre-commit)**

1. **`data/entities/`** - NO external imports (stdlib only)
2. **`data/business_logic/`** - Imports entities only
3. **`data/infrastructure/`** - NO entity imports (generic operations)
4. **Frameworks (pandas, Flask)** - ONLY in `app/`

### **Testing Philosophy**

- **Entities**: Pure logic, zero mocks
- **Business Logic**: Pure functions, zero mocks
- **Repositories**: Integration tests with real database
- **Services**: Unit tests with mock repositories

---

## Key Principles

1. **Framework Independence** - Core logic has zero framework dependencies
2. **Explicit Contracts** - Value objects instead of `Dict[str, Any]`
3. **Pure Business Logic** - Testable without mocks or database
4. **Generic Storage** - `Database` class works for any entity
5. **Clear Boundaries** - Layer violations prevented by pre-commit hooks

---

## Status

**Phase 0**: ✅ Repository structure established
**Phase 1**: 🔄 Implementing entities and infrastructure
**Phase 2**: ⏳ Repository layer
**Phase 3**: ⏳ Business logic and services
**Phase 4**: ⏳ Flask application layer
**Phase 5**: ⏳ Data migration from old dashboard

---

## References

- **Architecture Docs**: `docs/ARCHITECTURE.md`
- **Refactor Plan**: `../Grantwriting_Knowledge_Dashboard/documentation/architecture_refactor_plan.md`
- **Inspiration**: ten_week_goal_app clean architecture patterns

---

**Built with principled architecture from day one.**
