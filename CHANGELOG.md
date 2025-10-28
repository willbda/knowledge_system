# Changelog

All notable changes to the Grant Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),


## [Unreleased]

### Added
- Core entities: Grant, Funder, DevTeamMember
- Comprehensive test suite (60 tests)
- Standard .gitignore for Python projects
- This CHANGELOG

### Architecture
- Four-layer clean architecture (CATEGORIAE/ETHICA/RHETORICA/POLITICA)
- Pure domain entities with no framework coupling
- Value objects for explicit contracts
- Generic storage layer

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

