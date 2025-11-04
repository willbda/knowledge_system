#!/usr/bin/env python3
"""
Minimal Writing Schedule Import Script

Written by Claude Code on 2025-10-30

PURPOSE: Import a handful of WritingScheduleRows to see how the data looks
in the new grant_system.db with blueprint architecture.

APPROACH:
1. Read rows from source writing_schedule.db
2. Decompose each row into blueprints (natural keys)
3. Resolve natural keys → foreign keys (upsert reference data)
4. Insert task records into database

This is a MANUAL import script, not using repositories yet.
"""

import sqlite3
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.adapters.writing_schedule.schema import WritingScheduleRow
from data.adapters.writing_schedule.parser import decompose_row


def connect_source_db() -> sqlite3.Connection:
    """Connect to the source Writing Schedule database"""
    source_path = Path.home() / "Coding" / "01_ACTIVE_PROJECTS" / "Grantwriting_Knowledge_Dashboard" / "data" / "storage" / "persistent_storage" / "writing_schedule.db"

    if not source_path.exists():
        raise FileNotFoundError(f"Source database not found: {source_path}")

    return sqlite3.connect(str(source_path))


def connect_target_db() -> sqlite3.Connection:
    """Connect to the target grant_system database"""
    target_path = project_root / "data" / "grant_system.db"
    return sqlite3.connect(str(target_path))


def fetch_sample_rows(conn: sqlite3.Connection, limit: int = 10) -> list[WritingScheduleRow]:
    """Fetch a sample of rows from the source database"""
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            task_id,
            bernie_identifier,
            funder,
            type,
            status,
            deadline,
            amount,
            award,
            notification_date,
            grant_start_date,
            grant_end_date,
            owner,
            short_name,
            last_modified,
            fiscal_year,
            area,
            initiative,
            communities,
            members_funded,
            model_funded,
            dev_team_notes,
            grant_goals,
            acknowledgment_needs,
            opportunity,
            state,
            bloomerang_account,
            reports_due
        FROM writing_schedule_current
        WHERE bernie_identifier IS NOT NULL
        ORDER BY last_modified DESC
        LIMIT ?
    """, (limit,))

    rows = []
    for row in cursor.fetchall():
        rows.append(WritingScheduleRow(**dict(row)))

    return rows


def upsert_funder(conn: sqlite3.Connection, bernie_number: str, canonical_name: str) -> None:
    """Upsert funder record"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO funders (bernie_number, canonical_name, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (bernie_number, canonical_name))


def upsert_dev_team_member(conn: sqlite3.Connection, name: str) -> int:
    """Upsert dev team member and return ID"""
    cursor = conn.cursor()

    # Check if exists
    cursor.execute("SELECT id FROM dev_team_members WHERE full_name = ?", (name,))
    result = cursor.fetchone()

    if result:
        return result[0]

    # Insert new
    cursor.execute("""
        INSERT INTO dev_team_members (full_name) VALUES (?)
    """, (name,))

    return cursor.lastrowid


def upsert_status(conn: sqlite3.Connection, status_text: str, source_system: str = "writing_schedule") -> int:
    """Upsert raw status and return ID"""
    cursor = conn.cursor()

    # Check if exists
    cursor.execute("""
        SELECT id FROM raw_statuses
        WHERE status_text = ? AND source_system = ?
    """, (status_text, source_system))
    result = cursor.fetchone()

    if result:
        return result[0]

    # Insert new
    cursor.execute("""
        INSERT INTO raw_statuses (status_text, source_system)
        VALUES (?, ?)
    """, (status_text, source_system))

    return cursor.lastrowid


def insert_scheduled_task(conn: sqlite3.Connection, task_data: dict) -> None:
    """Insert scheduled_task record"""
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO scheduled_tasks (
            task_id, task_type, bernie_number, status_id, deadline, owner_id,
            last_modified_in_source, fiscal_year, program_area, initiative
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task_data['task_id'],
        task_data['task_type'],
        task_data['bernie_number'],
        task_data['status_id'],
        task_data['deadline'],
        task_data['owner_id'],
        task_data['last_modified'],
        task_data.get('fiscal_year'),
        task_data.get('program_area'),
        task_data.get('initiative')
    ))


def insert_loi(conn: sqlite3.Connection, task_id: str, loi_data: dict) -> None:
    """Insert LOI-specific record"""
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO lois (
            task_id, amount_requested,
            related_proposal_id, dev_team_notes
        ) VALUES (?, ?, ?, ?)
    """, (
        task_id,
        str(loi_data['amount_requested']) if loi_data.get('amount_requested') else None,
        loi_data.get('related_proposal_id'),
        loi_data.get('dev_team_notes')
    ))


def insert_proposal(conn: sqlite3.Connection, task_id: str, proposal_data: dict) -> None:
    """Insert Proposal-specific record"""
    cursor = conn.cursor()

    # amount_requested is required for proposals - use 0 if not provided
    amount = str(proposal_data['amount_requested']) if proposal_data.get('amount_requested') else "0.00"

    cursor.execute("""
        INSERT OR REPLACE INTO proposals (
            task_id, amount_requested, award_amount, submission_date,
            grant_start_date, grant_end_date,
            communities, members_funded, model_funded,
            dev_team_notes, grant_goals
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task_id,
        amount,
        str(proposal_data['award_amount']) if proposal_data.get('award_amount') else None,
        proposal_data.get('submission_date'),
        proposal_data.get('grant_start_date'),
        proposal_data.get('grant_end_date'),
        proposal_data.get('communities'),
        proposal_data.get('members_funded'),
        proposal_data.get('model_funded'),
        proposal_data.get('dev_team_notes'),
        proposal_data.get('grant_goals')
    ))


def insert_report(conn: sqlite3.Connection, task_id: str, report_data: dict) -> None:
    """Insert Report-specific record"""
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO reports (
            task_id, report_type, related_proposal_id, submission_date,
            reporting_period_start, reporting_period_end,
            acknowledgment_needs, dev_team_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task_id,
        report_data['report_type'],
        report_data.get('related_proposal_id'),
        report_data.get('submission_date'),
        report_data.get('reporting_period_start'),
        report_data.get('reporting_period_end'),
        report_data.get('acknowledgment_needs'),
        report_data.get('dev_team_notes')
    ))


def import_row(target_conn: sqlite3.Connection, row: WritingScheduleRow) -> None:
    """Import a single row using the blueprint architecture"""

    # Step 1: Decompose into blueprint with natural keys
    bernie_number, canonical_name, owner_name, raw_status, task_blueprint = decompose_row(row)

    print(f"  Importing: {task_blueprint.core.task_id} ({task_blueprint.core.task_type})")

    # Step 2: Resolve natural keys → foreign keys
    # Upsert funder
    upsert_funder(target_conn, bernie_number, canonical_name)

    # Upsert owner (if present)
    owner_id = upsert_dev_team_member(target_conn, owner_name) if owner_name else None

    # Upsert status
    status_id = upsert_status(target_conn, raw_status)

    # Step 3: Build task data with resolved FKs
    task_data = {
        'task_id': task_blueprint.core.task_id,
        'task_type': task_blueprint.core.task_type,
        'bernie_number': bernie_number,
        'status_id': status_id,
        'deadline': task_blueprint.core.deadline.isoformat() if task_blueprint.core.deadline else None,
        'owner_id': owner_id,
        'last_modified': task_blueprint.core.last_modified.isoformat() if task_blueprint.core.last_modified else None,
        'fiscal_year': task_blueprint.core.fiscal_year,
        'program_area': task_blueprint.core.program_area,
        'initiative': task_blueprint.core.initiative
    }

    # Insert scheduled_task
    insert_scheduled_task(target_conn, task_data)

    # Step 4: Insert type-specific data
    from data.blueprints import LOIBlueprint, ProposalBlueprint, ReportBlueprint

    if isinstance(task_blueprint, LOIBlueprint):
        loi_data = {
            'notification_date': task_blueprint.notification_date.isoformat() if task_blueprint.notification_date else None,
            'amount_requested': task_blueprint.amount_requested,
            'related_proposal_id': task_blueprint.related_proposal_id,
            'dev_team_notes': task_blueprint.dev_team_notes
        }
        insert_loi(target_conn, task_blueprint.core.task_id, loi_data)

    elif isinstance(task_blueprint, ProposalBlueprint):
        proposal_data = {
            'amount_requested': task_blueprint.amount_requested,
            'award_amount': task_blueprint.award_amount,
            'submission_date': task_blueprint.submission_date.isoformat() if task_blueprint.submission_date else None,
            'notification_date': task_blueprint.notification_date.isoformat() if task_blueprint.notification_date else None,
            'grant_start_date': task_blueprint.grant_start_date.isoformat() if task_blueprint.grant_start_date else None,
            'grant_end_date': task_blueprint.grant_end_date.isoformat() if task_blueprint.grant_end_date else None,
            'communities': task_blueprint.communities,
            'members_funded': task_blueprint.members_funded,
            'model_funded': task_blueprint.model_funded,
            'dev_team_notes': task_blueprint.dev_team_notes,
            'grant_goals': task_blueprint.grant_goals
        }
        insert_proposal(target_conn, task_blueprint.core.task_id, proposal_data)

    elif isinstance(task_blueprint, ReportBlueprint):
        report_data = {
            'report_type': task_blueprint.report_type,
            'related_proposal_id': task_blueprint.related_proposal_id,
            'submission_date': task_blueprint.submission_date.isoformat() if task_blueprint.submission_date else None,
            'reporting_period_start': task_blueprint.reporting_period_start.isoformat() if task_blueprint.reporting_period_start else None,
            'reporting_period_end': task_blueprint.reporting_period_end.isoformat() if task_blueprint.reporting_period_end else None,
            'acknowledgment_needs': task_blueprint.acknowledgment_needs,
            'dev_team_notes': task_blueprint.dev_team_notes
        }
        insert_report(target_conn, task_blueprint.core.task_id, report_data)


def main():
    """Main import function"""
    print("Starting Writing Schedule import...")

    # Connect to databases
    source_conn = connect_source_db()
    target_conn = connect_target_db()

    try:
        # Fetch sample rows
        print("\nFetching 10 sample rows from source database...")
        rows = fetch_sample_rows(source_conn, limit=10)
        print(f"Found {len(rows)} rows to import")

        # Import each row
        print("\nImporting rows...")
        for row in rows:
            import_row(target_conn, row)

        # Commit all changes
        target_conn.commit()
        print(f"\n✅ Successfully imported {len(rows)} records!")

        # Show summary stats
        cursor = target_conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM funders")
        funder_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dev_team_members")
        owner_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM raw_statuses")
        status_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scheduled_tasks")
        task_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM lois")
        loi_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM proposals")
        proposal_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM reports")
        report_count = cursor.fetchone()[0]

        print("\n" + "="*60)
        print("DATABASE SUMMARY")
        print("="*60)
        print(f"Funders:          {funder_count}")
        print(f"Dev Team Members: {owner_count}")
        print(f"Raw Statuses:     {status_count}")
        print(f"Scheduled Tasks:  {task_count}")
        print(f"  - LOIs:         {loi_count}")
        print(f"  - Proposals:    {proposal_count}")
        print(f"  - Reports:      {report_count}")
        print("="*60)

    finally:
        source_conn.close()
        target_conn.close()


if __name__ == "__main__":
    main()
