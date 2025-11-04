# Final Architecture Summary - Grant Management System

Written by Claude Code on 2025-10-30

## Core Simplification: Signal vs Noise

Based on your feedback, we've radically simplified the architecture to focus on what actually matters for daily workflows while preserving historical data.

## The Pipeline

```
WritingSchedule → Decomposer → Blueprints → Orchestrator → Entities → Database
                  (pure logic)  (nat. keys)  (FK resolver)  (domain)   (storage)
```

## Key Components

### 1. Database (schema.sql)
**Simplified to essentials:**
- `raw_statuses`: Store status text as-is, get auto-increment ID
- `funders`: Bernie number as PK, canonical name
- `dev_team_members`: ID, full name, short name
- `scheduled_tasks`: Core task data with status_id FK
- Task-specific tables: `lois`, `proposals`, `reports`, `reminders`

**What we removed:**
- Occurrence counting (can be calculated with COUNT)
- Complex semantic mapping tables
- Unnecessary timestamps and flags
- Status number parsing

### 2. Decomposer (writing_schedule_decomposer.py)
**Returns blueprints with natural keys:**
```python
def decompose_row(row) -> Tuple:
    # Returns natural keys, not entities
    return (
        bernie_number,      # "BN0002E1"
        canonical_name,     # "Dobbs Foundation"
        owner_name,         # "Jane Doe"
        raw_status,         # "1. Awarded" (exactly as received)
        task_blueprint      # Blueprint with natural keys
    )
```

### 3. Orchestrator (orchestrator.py)
**Resolves natural keys to foreign keys:**
```python
# Status text → ID (auto-increment)
INSERT OR IGNORE INTO raw_statuses (status_text, source_system)
VALUES ("1. Awarded", "writing_schedule")
# Returns id=1 (or whatever)

# Build entity with resolved FK
task.status_id = 1  # Just an integer now
```

### 4. Status Semantics (status_semantics.py)
**THE single place for business rules:**
```python
def get_semantics(status_id: int, task_type: str) -> StatusSemantics:
    """What does this status mean for workflow?"""

    if task_type == "LOI":
        match status_id:
            case 1:  # Whatever "1. Awarded" got as ID
                return StatusSemantics(
                    is_actionable=True,
                    needs_follow_up=True,
                    description="Invited to submit proposal"
                )
```

## What This Achieves

### Lossless Storage
- Keep exactly what external systems send
- No information thrown away
- Perfect audit trail

### Simple Database
- Status table is just text + auto-increment ID
- No complex mappings to maintain
- Foreign keys are just integers

### Clear Business Logic
- `status_semantics.py` is THE place for semantic rules
- Easy to find, easy to change
- Colleagues can modify without touching database

### Focus on Real Questions
```python
# 1. What needs work today?
actionable = is_actionable(task.status_id, task.task_type)

# 2. Was it successful?
success = was_successful(task.status_id, task.task_type)

# 3. Does it need follow-up?
follow_up = needs_follow_up(task.status_id, task.task_type)

# 4. When is it due?
# Already in task.deadline - no status needed
```

## Files Changed

1. **data/schema.sql** - Simplified to essential tables only
2. **data/services/writing_schedule_decomposer.py** - Returns blueprints with natural keys
3. **data/services/orchestrator.py** - Resolves natural keys to FKs
4. **data/services/status_semantics.py** - Business rules for status meaning
5. **data/services/task_service.py** - Blueprint definitions with natural keys

## Migration Notes

To load existing data:
```sql
-- 1. Load all unique statuses
INSERT INTO raw_statuses (status_text, source_system)
SELECT DISTINCT status, 'writing_schedule'
FROM writing_schedule_current;

-- 2. They'll get auto-increment IDs (1, 2, 3, etc.)

-- 3. Use those IDs in scheduled_tasks.status_id
```

## Key Insight

The status strings from external systems ("1. Awarded", "10. Forgone") are **historical noise**. What matters for workflow is answering simple questions (actionable? successful? needs follow-up?) and those answers live in code, not the database.

This architecture preserves all the historical data while keeping the domain logic clean and maintainable.