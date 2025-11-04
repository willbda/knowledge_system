# Entity Relationship Design

Written by Claude Code on 2025-10-29

## Core Principle: Minimize Null Fields Through Smart Relationship Placement

Instead of creating bidirectional relationships that leave many null fields, we place foreign keys on the "many" or "optional" side of relationships.

## Relationship Patterns

### LOI → Proposal (Optional, One-to-One)

```
LOI.related_proposal_id → Proposal.task_id
```

**Rationale**: Most proposals DON'T have LOIs. Only a subset of grants require a Letter of Intent before full application. By placing the relationship in LOI, we ensure:
- Proposals remain lean (no nullable `loi_id` field)
- When an LOI exists, it naturally links forward to its resulting proposal
- Easy to query: "Did this LOI lead to a proposal?"

**Example Flow**:
1. Submit LOI (no `related_proposal_id` yet)
2. Get invited to apply
3. Submit Proposal
4. Update LOI: set `related_proposal_id = proposal.task_id`

### Report → Proposal (Nearly Always, One-to-One)

```
Report.related_proposal_id → Proposal.task_id
```

**Rationale**: Almost EVERY report documents an awarded proposal (the grant being reported on). However, proposals may have:
- 0 reports (just awarded, reporting not due yet)
- 1 report (annual report)
- Multiple reports (interim + final)

By placing the relationship in Report:
- Proposals remain clean (no complex array of report IDs)
- Each report explicitly knows what it's reporting on
- Easy to query: "What are all reports for this proposal?" → `SELECT * FROM reports WHERE related_proposal_id = ?`

**Example Flow**:
1. Submit Proposal → Award received
2. Create Report(s) with `related_proposal_id = proposal.task_id`
3. Query all reports for a grant: filter by `related_proposal_id`

## Schema Implications

### LOIs Table
```sql
CREATE TABLE lois (
    task_id TEXT PRIMARY KEY,
    funder TEXT NOT NULL,
    amount_requested DECIMAL,
    notification_date TEXT,
    related_proposal_id TEXT,  -- FK to proposals.task_id
    ...
    FOREIGN KEY (task_id) REFERENCES scheduled_tasks(task_id),
    FOREIGN KEY (related_proposal_id) REFERENCES proposals(task_id)
);
```

### Proposals Table
```sql
CREATE TABLE proposals (
    task_id TEXT PRIMARY KEY,
    funder TEXT NOT NULL,
    amount_requested DECIMAL NOT NULL,  -- REQUIRED for proposals!
    award_amount DECIMAL,
    ...
    FOREIGN KEY (task_id) REFERENCES scheduled_tasks(task_id)
    -- NO loi_id or report_ids fields needed!
);
```

### Reports Table
```sql
CREATE TABLE reports (
    task_id TEXT PRIMARY KEY,
    funder TEXT NOT NULL,
    report_type TEXT NOT NULL,
    related_proposal_id TEXT,  -- FK to proposals.task_id
    ...
    FOREIGN KEY (task_id) REFERENCES scheduled_tasks(task_id),
    FOREIGN KEY (related_proposal_id) REFERENCES proposals(task_id)
    -- NO amount fields! Reports don't request money.
);
```

## Query Patterns

### Find all tasks for a grant opportunity
```python
# Get the proposal
proposal = proposal_repo.get(proposal_id)

# Find related LOI (if any)
loi = loi_repo.find_by_related_proposal(proposal_id)

# Find all related reports
reports = report_repo.find_by_related_proposal(proposal_id)
```

### Trace a grant lifecycle
```python
# Start with LOI
loi = loi_repo.get(loi_id)

# Did it lead to a proposal?
if loi.related_proposal_id:
    proposal = proposal_repo.get(loi.related_proposal_id)

    # Are there reports on this grant?
    reports = report_repo.find_by_related_proposal(proposal.task_id)
```

## Benefits of This Design

1. **Minimal Nulls**: Only fields that are truly optional are nullable
2. **Clear Semantics**: The relationship direction tells you the business logic
3. **Easy Queries**: Standard SQL foreign key patterns
4. **Type Safety**: Each entity has exactly the fields it needs (no amount fields in Reports!)
5. **Flexible Evolution**: Can add more relationship types (e.g., amendments, renewals) without modifying existing entities

## Edge Cases

### What if a Report doesn't have a Proposal?
In rare cases, a funder might request a report without a formal proposal process (e.g., general update to a longtime donor). In this case, `related_proposal_id` is `None` - the Report stands alone.

### What if we submit multiple LOIs to the same funder?
Each LOI is a separate entity with its own `task_id`. If both lead to proposals, each LOI links to its respective proposal.

### What about multi-year grants with renewal applications?
A renewal is a new Proposal entity with its own `task_id`. You might add a `renewal_of_proposal_id` field to Proposal if you need to track the lineage.
