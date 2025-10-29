# Changelog

All notable changes to the Grant Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),


## [Unreleased]

### Added
- **Opportunity-centric entity model**: Replaced monolithic Grant entity with opportunity-focused design
  - `Opportunity`: Minimal identity anchor for funding relationships
  - `Proposal`: Full grant applications with award tracking
  - `Report`: Grant reporting requirements (no award fields)
  - `LOI`: Letters of intent with invitation tracking
  - `Prospect`: Early-stage research opportunities
  - `Document`: Historical files with opportunity linking
- **Writing Schedule adapter**: Schema and parser for external data ingestion (data/adapters/writing_schedule/)
- **CRM adapter structure**: Placeholder for Bloomerang integration (data/adapters/constituent_relationship_manager/)
- **Value objects**: OpportunityOverview, TaskSummary for explicit result contracts
- **Comprehensive documentation**: ARCHITECTURE.md, Categoriae Layer: Domain Entities.md
- **Layer-by-layer roadmap**: Implementation plan organized by architectural layers (.github/LAYER_BY_LAYER_ROADMAP.md)
- **GitHub issues**: 5 issues tracking implementation milestones (#1-#5)

### Changed
- Removed monolithic `Grant` entity in favor of type-specific task entities
- Updated entity structure to support master task routing table pattern

### Architecture Decisions
- **Task entities**: Separate tables (proposals, reports, lois) with master task table for routing by task_id
- **Opportunity grouping**: Manual creation (not auto-derived from Writing Schedule)
- **Document linking**: Manual association (no fuzzy matching initially)
- **Business logic location**: Pure functions in ethica layer, not entity methods

### In Progress
- Issue #1: Fix categoriae layer entities (Prospect FK, Document FKs, validation)
- Issue #2: Implement politica layer (Database class + SQL schemas)
- Issue #3: Implement rhetorica layer (repositories)
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

