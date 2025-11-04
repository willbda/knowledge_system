# Data Transformation Pipeline

Written by Claude Code on 2025-10-29

## Source: Writing Schedule Database

The Writing Schedule is an external system that tracks all grant-related activities. Data comes to us as a DataFrame, where each row represents one scheduled task.

### Example Raw Data
```
task_id                         funder                      type          owner           bernie_identifier  amount
DOBBFD-GA25E-NSO-LOI-240830    Dobbs Foundation            LOI           Jane Doe   BN0002E1           100000.0
DELUCPFD-MN25E-NSO-PROP-240831 Deluxe Corporation Found.   Proposal      Jane Doe   BN0000A6           25000.0
RICHMSCH-MN25E-NSO-FIRE-240911 Richard M. Schulze Fam. F.  Final Report  Allie Handberg  BN00002C           NULL
```

## Transformation Goal

**ONE WritingScheduleRow → MULTIPLE Domain Entities**

Each row contains data for:
1. **Funder** (identified by bernie_identifier)
2. **DevTeamMember** (identified by owner/short_name)
3. **ScheduledTask** (LOI, Proposal, Report, or Reminder)

## Pipeline Architecture

```
┌────────────────────────────────────────────────────────────────┐
│ STEP 1: External System → DataFrame                            │
│ Writing Schedule API serves data as DataFrame                  │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 2: DataFrame Row → WritingScheduleRow                     │
│ Schema layer: Type each row as WritingScheduleRow object       │
│ (Pure data bag, no logic, just typed fields)                   │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 3: WritingScheduleRow → Domain Entities                   │
│ Decomposer extracts multiple entities from single row:         │
│                                                                 │
│ row.bernie_identifier → Funder                                 │
│ row.owner/short_name  → DevTeamMember                          │
│ row.type + fields     → LOI | Proposal | Report | Reminder    │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 4: Domain Entities → Repositories → Database              │
│ Each entity saved to its appropriate table via repository      │
│                                                                 │
│ Funder          → FunderRepository       → funders table       │
│ DevTeamMember   → DevTeamRepository      → dev_team table      │
│ LOI             → LOIRepository          → lois table          │
│ Proposal        → ProposalRepository     → proposals table     │
│ Report          → ReportRepository       → reports table       │
└────────────────────────────────────────────────────────────────┘
```

## Decomposition Logic

### Input: WritingScheduleRow
```python
row = WritingScheduleRow(
    task_id="DOBBFD-GA25E-NSO-LOI-240830",
    funder="Dobbs Foundation",
    bernie_identifier="BN0002E1",
    type="LOI",
    status="3. LOI Submitted",
    deadline="2024-08-30",
    amount="100000.0",
    owner="Jane Doe",
    short_name="Jane",
    ...
)
```

### Output: Multiple Domain Entities

#### 1. Extract Funder
```python
funder = Funder(
    bernie_number="BN0002E1",
    canonical_name="Dobbs Foundation",  # From row.funder
)
```

#### 2. Extract DevTeamMember
```python
dev_member = DevTeamMember(
    name="Jane Doe",      # From row.owner
    short_name="Jane",        # From row.short_name
)
```

#### 3. Extract ScheduledTask (type-specific)
```python
# Since row.type == "LOI":
loi = LOI(
    core=TaskCore(
        task_id="DOBBFD-GA25E-NSO-LOI-240830",
        task_type="LOI",
        status="submitted",  # Mapped from "3. LOI Submitted"
        deadline=datetime(2024, 8, 30),
        owner="Jane Doe",
        last_modified=datetime.now(),
    ),
    funder="Dobbs Foundation",
    amount_requested=Decimal("100000.0"),
    notification_date=None,
    ...
)
```

## Key Design Principles

### 1. Decomposition is Systematic
Every WritingScheduleRow can be decomposed into the SAME set of entity types:
- Always extract Funder (from bernie_identifier + funder name)
- Always extract DevTeamMember (from owner + short_name)
- Always extract ScheduledTask (type determines which: LOI/Proposal/Report)

### 2. Idempotency
Extracting the same row multiple times should be safe:
- Funder: Upsert by bernie_number (update canonical_name if changed)
- DevTeamMember: Upsert by name (update short_name if changed)
- ScheduledTask: Upsert by task_id (update status, deadline, etc.)

### 3. Type Safety Through Decomposition
```python
# Bad: One giant entity with nullable fields
class Task:
    amount_requested: Optional[Decimal]  # Only for LOIs and Proposals
    report_type: Optional[str]           # Only for Reports
    # ... cognitive load!

# Good: Separate entities with only relevant fields
class LOI:
    amount_requested: Optional[Decimal]  # Makes sense for LOIs

class Report:
    report_type: str                     # Makes sense for Reports
    # NO amount_requested field!
```

### 4. Easy to Test Each Transformation
```python
def test_decompose_loi_row():
    row = WritingScheduleRow(type="LOI", ...)
    funder, dev_member, loi = decompose_row(row)

    assert isinstance(funder, Funder)
    assert funder.bernie_number == "BN0002E1"

    assert isinstance(loi, LOI)
    assert loi.amount_requested == Decimal("100000.0")
```

## Implementation Strategy

### Phase 1: Decomposer Function
```python
# data/services/writing_schedule_decomposer.py

def decompose_writing_schedule_row(row: WritingScheduleRow) -> tuple[Funder, DevTeamMember, ScheduledTask]:
    """
    Decompose one WritingScheduleRow into domain entities.

    Returns:
        (Funder, DevTeamMember, ScheduledTask)
    """
    funder = _extract_funder(row)
    dev_member = _extract_dev_team_member(row)
    task = _extract_scheduled_task(row)

    return funder, dev_member, task
```

### Phase 2: Bulk Processor
```python
# data/services/writing_schedule_sync.py

def sync_writing_schedule(df: pd.DataFrame) -> dict:
    """
    Process entire Writing Schedule DataFrame.

    Returns:
        Summary stats: {funders_created, tasks_created, errors, ...}
    """
    stats = {"funders": 0, "dev_members": 0, "tasks": 0, "errors": []}

    for _, row_dict in df.iterrows():
        row = WritingScheduleRow(**row_dict)

        try:
            funder, dev_member, task = decompose_writing_schedule_row(row)

            funder_repo.upsert(funder)
            dev_team_repo.upsert(dev_member)
            task_repo.upsert(task)  # Routes to LOIRepo/ProposalRepo/ReportRepo

            stats["funders"] += 1
            stats["dev_members"] += 1
            stats["tasks"] += 1

        except Exception as e:
            stats["errors"].append({"task_id": row.task_id, "error": str(e)})

    return stats
```

## Questions to Resolve

1. **DevTeamMember Identity**: Is `owner` (full name) the unique identifier, or `short_name`, or combination?

2. **Funder Lookup**: Do we trust `row.funder` as canonical name, or do we need a separate funder registry lookup by bernie_number?

3. **Task Routing**: How does `task_repo.upsert(task)` know which specific repo to use?
   - Option A: Factory pattern inside a unified TaskRepository
   - Option B: Service layer does type checking and routes explicitly
   - Option C: Each task type has its own repository, caller decides

4. **Error Handling**: If Funder upsert succeeds but Task upsert fails, do we rollback? Or accept partial success?

5. **Relationships**: Should decomposer also extract relationships (e.g., Report.related_proposal_id)?

