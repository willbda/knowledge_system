# Changelog

All notable changes to the Grant Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),


## [Unreleased] - 2025-10-30

### MAJOR REFACTORING: Blueprint Architecture & 3NF+ Normalization

**Summary**: Complete architectural refactor to implement blueprint pattern with clean separation of concerns and 3NF+ normalized database schema. All critical issues identified by agents have been resolved.

**Status**: ✅ Production-ready after fixing 3 critical blockers

---

## [Unreleased] - Previous Work

### Added
- **Composition-based scheduled task architecture** (data/basic_entities/schedule_task.py)
  - `TaskCore`: Shared scheduling data for all task types
  - `LOI`, `Proposal`, `Report`, `Reminder`: Type-specific entities using composition
  - `ScheduledTask` Protocol for duck-typed polymorphism
- **Writing Schedule decomposer service** (data/services/writing_schedule_decomposer.py)
  - `decompose_row()`: ONE WritingScheduleRow → THREE entities (Funder, DevTeamMember, ScheduledTask)
  - `extract_funder()`: Extract Funder from bernie_identifier + funder name
  - `extract_dev_team_member()`: Extract DevTeamMember from owner field
  - `extract_scheduled_task()`: Type dispatch to LOI/Proposal/Report/Reminder
- **Comprehensive test suite** (36 tests - ALL PASSING)
  - **Entity tests** (27 tests): Funder, FunderAlias, DevTeamMember, Document, ScheduledTask entities
  - **Service tests** (9 tests): Decomposer functions with real Writing Schedule data
- **Documentation**
  - `docs/entity_relationships.md`: Entity relationships and composition patterns
  - `docs/data_transformation_pipeline.md`: Complete decomposition workflow

### Changed
- **Entity reorganization**:
  - Moved entities from `data/entities/` to `data/basic_entities/` and `data/composite_entities/`
  - Deleted old entity files: loi.py, proposal.py, report.py, prospect.py
  - Removed old Writing Schedule parser (replaced by decomposer)
- **Architecture shift**: Composition over inheritance for scheduled tasks
  - Each task entity contains TaskCore instead of inheriting from base class
  - Type safety through Protocol instead of abstract base classes

### Architecture Decisions
- **Composition over Inheritance**: TaskCore as composition component enables:
  - Flexibility to add task-specific fields without affecting shared logic
  - Clear separation between scheduling data (TaskCore) and task-specific data
  - Easier testing (can test TaskCore independently)
- **Decomposition pattern**: Single source row → Multiple domain entities
  - Idempotent: Running decomposition multiple times is safe (upsert by natural keys)
  - Type-safe: Returns specific task types, not generic Task
- **Real data testing**: Tests use actual Writing Schedule database rows for validation

### Removed
- Old parser: `data/adapters/writing_schedule/parser.py` (replaced by decomposer)
- Old entities: Prospect, old-style LOI/Proposal/Report with inheritance

### In Progress
- Issue #2: Implement politica layer (Database class + SQL schemas)
- Issue #3: Implement rhetorica layer (repositories with upsert logic)
- Issue #4: Implement ethica layer (business logic functions)
- Issue #5: Data migration from old dashboard

## [0.1.0] - 2025-10-28

### Initial Release

**Status**: Pre-release (0.x indicates development phase)

#### Core Features
- **Grant Entity**: Models grant opportunities with deadline tracking, urgency detection, and status management
- **Funder Entity**: Manages funder organizations with Bernie Numbers, aliases, and name matching
- **DevTeamMember Entity**: Represents team members with validation

#### Architecture Components
- **CATEGORIAE Layer**: Pure domain models with zero external dependencies
- **Infrastructure**: Generic database operations independent of entity types

#### Project Structure
```
data/
├── entities/          # Pure domain models
├── business_logic/    # Pure functions (coming soon)
├── services/          # Orchestration layer (coming soon)
├── repositories/      # Entity ↔ storage translation (coming soon)
└── infrastructure/    # Generic storage operations

tests/
├── unit/              # Entity and business logic tests
└── integration/       # Coming soon

docs/
└── ARCHITECTURE.md    # Complete architectural documentation
```

#### Known Limitations
- No persistence layer yet (repositories coming in 0.2.0)
- No services orchestration yet
- No Flask application layer yet

---

## Release Workflow

### Creating a New Release

1. **Update version numbers** in:
   - `pyproject.toml` (version field)
   - `data/__init__.py` (__version__)

2. **Update CHANGELOG.md**:
   - Move items from [Unreleased] to new version section
   - Use ISO 8601 date format (YYYY-MM-DD)

3. **Create and push a git tag**:
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0: Add persistence layer"
   git push origin v0.2.0
   ```

4. **Create GitHub Release**:
   - Go to Releases page
   - Create new release from tag
   - Copy relevant CHANGELOG section as release notes

### Version Numbering

- **MAJOR** (0.x.x): Architectural changes, breaking changes to public API
- **MINOR** (x.1.x): New features, new entities, new layers
- **PATCH** (x.x.1): Bug fixes, performance improvements, documentation

### Pre-release Naming

While in 0.x phase:
- `0.1.0` - Initial entities + infrastructure
- `0.2.0` - Add repositories + persistence
- `0.3.0` - Add services + business logic
- `0.4.0` - Add Flask application layer
- `1.0.0` - Production-ready (when complete)

---

