-- Grant Management System Database Schema
-- Written by Claude Code on 2025-10-30
--
-- Design Principles:
-- 1. 3NF+ normalization to eliminate redundancy
-- 2. Simple status system: raw text → auto-increment ID (semantics in code)
-- 3. Natural keys for external data, surrogate keys for internal
-- 4. Audit trail through timestamps and lineage tracking

-- =============================================================================
-- REFERENCE DATA (Enumeration Tables)
-- =============================================================================

-- Capture exactly what external systems give us
CREATE TABLE raw_statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_text TEXT NOT NULL,              -- "1. Awarded", "7. Report Submitted"
    source_system TEXT NOT NULL,            -- "writing_schedule", "bloomerang"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(status_text, source_system)      -- Natural key
);

-- Note: Status semantics are defined in code (data/services/status_semantics.py)
-- The database only stores the raw text and assigns an ID

-- =============================================================================
-- CORE ENTITIES
-- =============================================================================

-- Funders (organizations that give grants)
CREATE TABLE funders (
    bernie_number TEXT PRIMARY KEY,         -- Bernie Numbers are the PK
    canonical_name TEXT NOT NULL,           -- "Dobbs Foundation"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Funder aliases (alternate names for same funder)
CREATE TABLE funder_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bernie_number TEXT NOT NULL,            -- FK to funders.bernie_number
    alias TEXT NOT NULL,                    -- Alternate name
    usage TEXT,                             -- Context where this alias appears
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (bernie_number) REFERENCES funders(bernie_number),
    UNIQUE(bernie_number, alias)            -- Can't have duplicate aliases for same funder
);

-- Development team members
CREATE TABLE dev_team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL UNIQUE,         -- "Jane Doe"
    short_name TEXT                         -- "Jane"
);

-- Opportunities (funding relationships/programs)
-- We're not ready to define the opportunity table, as this will be composed from the more basic tasks and the table might be a junction table largely


-- =============================================================================
-- SCHEDULED TASKS (Core task tracking)
-- =============================================================================

-- Base table for all scheduled tasks (implements inheritance via type field)
CREATE TABLE scheduled_tasks (
    task_id TEXT PRIMARY KEY,               -- "DOBBFD-GA25E-NSO-LOI-240830"
    task_type TEXT NOT NULL,                -- "LOI", "Proposal", "Report", "Reminder"

    -- Foreign Keys
    bernie_number TEXT NOT NULL,            -- FK to funders.bernie_number
    status_id INTEGER,                      -- FK to raw_statuses.id
    owner_id INTEGER,                       -- Assigned team member

    -- Core scheduling fields
    deadline DATE NOT NULL,
    notification_date DATE,                 -- When we expect to hear back

    -- Program classification (normalized to scheduled_tasks)
    fiscal_year TEXT,                       -- "FY25"
    program_area TEXT,                      -- "Education", "Youth Development"
    initiative TEXT,                        -- Initiative name

    -- System fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified_in_source TIMESTAMP,      -- From external system

    FOREIGN KEY (bernie_number) REFERENCES funders(bernie_number),
    FOREIGN KEY (status_id) REFERENCES raw_statuses(id),
    FOREIGN KEY (owner_id) REFERENCES dev_team_members(id)
);

-- LOI-specific fields
CREATE TABLE lois (
    task_id TEXT PRIMARY KEY,
    amount_requested DECIMAL(12,2),         -- Often tentative at LOI stage

    -- Relationship to subsequent proposal
    related_proposal_id TEXT,               -- FK to proposals.task_id

    -- Notes
    dev_team_notes TEXT,

    FOREIGN KEY (task_id) REFERENCES scheduled_tasks(task_id),
    FOREIGN KEY (related_proposal_id) REFERENCES proposals(task_id) ON DELETE SET NULL
);

-- Proposal-specific fields
CREATE TABLE proposals (
    task_id TEXT PRIMARY KEY,
    amount_requested DECIMAL(12,2) NOT NULL,  -- Required for proposals
    award_amount DECIMAL(12,2),               -- If awarded

    -- Key dates
    submission_date DATE,
    grant_start_date DATE,
    grant_end_date DATE,

    -- Proposal-specific program details
    communities TEXT,                          -- Communities served
    members_funded TEXT,                       -- Team members supported
    model_funded TEXT,                         -- Program model

    -- Content
    grant_goals TEXT,
    dev_team_notes TEXT,

    FOREIGN KEY (task_id) REFERENCES scheduled_tasks(task_id)
);

-- Report-specific fields
CREATE TABLE reports (
    task_id TEXT PRIMARY KEY,
    report_type TEXT NOT NULL,                -- "Final Report", "Interim Report"

    -- Relationship to proposal being reported on
    related_proposal_id TEXT,                 -- FK to proposals.task_id

    -- Report period
    submission_date DATE,
    reporting_period_start DATE,
    reporting_period_end DATE,

    -- Report specifics
    acknowledgment_needs TEXT,                -- Special requirements
    dev_team_notes TEXT,

    FOREIGN KEY (task_id) REFERENCES scheduled_tasks(task_id),
    FOREIGN KEY (related_proposal_id) REFERENCES proposals(task_id) ON DELETE SET NULL
);

-- Reminder-specific fields (lightweight tasks)
CREATE TABLE reminders (
    task_id TEXT PRIMARY KEY,
    reminder_note TEXT,
    reminder_category TEXT,                   -- "follow-up", "deadline", "meeting"

    FOREIGN KEY (task_id) REFERENCES scheduled_tasks(task_id)
);

-- =============================================================================
-- AUDIT & LINEAGE TABLES
-- =============================================================================

-- Track transformations from source data to entities
CREATE TABLE etl_lineage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_system TEXT NOT NULL,              -- "writing_schedule"
    source_row_id TEXT NOT NULL,              -- Original identifier
    target_table TEXT NOT NULL,               -- "proposals", "lois", etc.
    target_id TEXT NOT NULL,                  -- task_id in target table

    -- Transformation metadata
    raw_status_id INTEGER,
    raw_status_text TEXT,                     -- Original text for audit

    -- Processing metadata
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processor_version TEXT,
    warnings TEXT,                            -- JSON array of warnings

    FOREIGN KEY (raw_status_id) REFERENCES raw_statuses(id)
);

-- Track changes to entities over time
CREATE TABLE change_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by TEXT,
    change_source TEXT                        -- "manual", "sync", "import"
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================
-- leave indexes blank while we aling on the fundamentals

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================
-- leave views blank while we align on the fundamentals