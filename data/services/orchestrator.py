"""
Orchestrator - Resolves Natural Keys to Foreign Keys

Written by Claude Code on 2025-10-30

PURPOSE: Transform blueprints (natural keys) into entities (foreign keys).
This is where we connect the decomposer output to the database.

KEY RESPONSIBILITIES:
1. Resolve status text → status_id (insert if new)
2. Resolve funder bernie_number → funder record (upsert)
3. Resolve owner name → dev_team_member_id (upsert)
4. Build final entities with resolved FKs
"""

from typing import Optional, Dict, Any
import sqlite3
from dataclasses import dataclass
from datetime import datetime

from data.basic_entities import (
    Funder,
    DevTeamMember,
    TaskCore,
    LOI,
    Proposal,
    Report,
    Reminder
)
from data.blueprints import (
    LOIBlueprint,
    ProposalBlueprint,
    ReportBlueprint,
    ReminderBlueprint,
    TaskBlueprint
)


@dataclass
class ResolutionResult:
    """Results of FK resolution"""
    status_id: int
    funder_id: Optional[str]  # Bernie number is the PK
    owner_id: Optional[int]
    was_status_new: bool
    was_funder_new: bool
    was_owner_new: bool


class TaskOrchestrator:
    """
    Orchestrates the transformation from blueprints to entities.

    This is the ONLY place that needs database access for FK resolution.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def process_decomposed_row(
        self,
        bernie_number: str,
        canonical_name: str,
        owner_name: Optional[str],
        raw_status: str,
        task_blueprint: TaskBlueprint
    ) -> tuple[Funder, Optional[DevTeamMember], Any, Dict[str, Any]]:
        """
        Process decomposer output into entities with resolved FKs.

        Args:
            bernie_number: Funder's bernie identifier
            canonical_name: Funder's name
            owner_name: Task owner's name (if any)
            raw_status: Raw status text from source
            task_blueprint: Blueprint with natural keys

        Returns:
            (funder_entity, owner_entity, task_entity, metadata)
        """

        with sqlite3.connect(self.db_path) as conn:
            # 1. Resolve all natural keys to foreign keys
            resolution = self._resolve_foreign_keys(
                conn,
                bernie_number,
                canonical_name,
                owner_name,
                raw_status,
                "writing_schedule"  # source system
            )

            # 2. Build entities with resolved FKs
            funder = Funder(
                bernie_number=bernie_number,
                canonical_name=canonical_name
            )

            owner = DevTeamMember(name=owner_name) if owner_name else None

            task = self._build_task_entity(task_blueprint, resolution)

            # 3. Build metadata for lineage tracking
            metadata = {
                'status_id': resolution.status_id,
                'was_status_new': resolution.was_status_new,
                'was_funder_new': resolution.was_funder_new,
                'was_owner_new': resolution.was_owner_new,
                'raw_status': raw_status
            }

            return funder, owner, task, metadata

    def _resolve_foreign_keys(
        self,
        conn: sqlite3.Connection,
        bernie_number: str,
        canonical_name: str,
        owner_name: Optional[str],
        raw_status: str,
        source_system: str
    ) -> ResolutionResult:
        """
        Resolve all natural keys to foreign keys.

        This is where we handle the messy reality of:
        - New statuses appearing
        - Funders being created on first encounter
        - Dev team members being added
        """

        cursor = conn.cursor()

        # 1. Resolve status (insert if new, get ID)
        cursor.execute("""
            INSERT OR IGNORE INTO raw_statuses (status_text, source_system)
            VALUES (?, ?)
        """, (raw_status, source_system))

        cursor.execute("""
            SELECT id FROM raw_statuses
            WHERE status_text = ? AND source_system = ?
        """, (raw_status, source_system))

        status_result = cursor.fetchone()
        status_id = status_result[0] if status_result else 1  # Default to 1 if somehow fails
        was_status_new = cursor.rowcount > 0  # Track if this was a new status

        # 2. Resolve funder (upsert)
        cursor.execute("""
            INSERT OR REPLACE INTO funders (bernie_number, canonical_name, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (bernie_number, canonical_name))

        was_funder_new = cursor.rowcount > 0

        # 3. Resolve owner (upsert if present)
        owner_id = None
        was_owner_new = False

        if owner_name:
            cursor.execute("""
                INSERT OR IGNORE INTO dev_team_members (full_name)
                VALUES (?)
            """, (owner_name,))

            was_owner_new = cursor.rowcount > 0

            cursor.execute("""
                SELECT id FROM dev_team_members WHERE full_name = ?
            """, (owner_name,))

            owner_result = cursor.fetchone()
            owner_id = owner_result[0] if owner_result else None

        conn.commit()

        return ResolutionResult(
            status_id=status_id,
            funder_id=bernie_number,  # Bernie number IS the FK
            owner_id=owner_id,
            was_status_new=was_status_new,
            was_funder_new=was_funder_new,
            was_owner_new=was_owner_new
        )

    def _build_task_entity(
        self,
        blueprint: TaskBlueprint,
        resolution: ResolutionResult
    ) -> Any:
        """
        Build the appropriate task entity with resolved FKs.

        Transform blueprint (natural keys) → entity (foreign keys).
        """

        # Build TaskCore with resolved FKs
        core = TaskCore(
            task_id=blueprint.core.task_id,
            task_type=blueprint.core.task_type,
            bernie_number=blueprint.core.bernie_number,  # FK to Funder
            status_id=resolution.status_id,  # Resolved FK!
            deadline=blueprint.core.deadline,
            owner_id=resolution.owner_id,  # Resolved FK to dev_team_members!
            last_modified=blueprint.core.last_modified,
            fiscal_year=blueprint.core.fiscal_year,  # Program fields (normalized)
            program_area=blueprint.core.program_area,
            initiative=blueprint.core.initiative,
            opportunity_id=blueprint.core.opportunity_id
        )

        # Build type-specific entity
        if isinstance(blueprint, LOIBlueprint):
            return LOI(
                core=core,
                notification_date=blueprint.notification_date,
                amount_requested=blueprint.amount_requested,
                related_proposal_id=blueprint.related_proposal_id,
                dev_team_notes=blueprint.dev_team_notes
            )

        elif isinstance(blueprint, ProposalBlueprint):
            return Proposal(
                core=core,
                amount_requested=blueprint.amount_requested,
                award_amount=blueprint.award_amount,
                submission_date=blueprint.submission_date,
                notification_date=blueprint.notification_date,
                grant_start_date=blueprint.grant_start_date,
                grant_end_date=blueprint.grant_end_date,
                communities=blueprint.communities,
                members_funded=blueprint.members_funded,
                model_funded=blueprint.model_funded,
                dev_team_notes=blueprint.dev_team_notes,
                grant_goals=blueprint.grant_goals
            )

        elif isinstance(blueprint, ReportBlueprint):
            return Report(
                core=core,
                report_type=blueprint.report_type,
                related_proposal_id=blueprint.related_proposal_id,
                submission_date=blueprint.submission_date,
                reporting_period_start=blueprint.reporting_period_start,
                reporting_period_end=blueprint.reporting_period_end,
                acknowledgment_needs=blueprint.acknowledgment_needs,
                dev_team_notes=blueprint.dev_team_notes
            )

        else:  # ReminderBlueprint
            return Reminder(
                core=core,
                reminder_note=blueprint.reminder_note
            )


class BatchOrchestrator:
    """
    Process multiple rows efficiently with connection pooling.
    """

    def __init__(self, db_path: str):
        self.orchestrator = TaskOrchestrator(db_path)
        self.db_path = db_path

    def process_batch(self, decomposed_rows: list) -> Dict[str, Any]:
        """
        Process a batch of decomposed rows.

        Args:
            decomposed_rows: List of tuples from decomposer

        Returns:
            Processing statistics and results
        """
        results = {
            'processed': 0,
            'errors': [],
            'new_statuses': 0,
            'new_funders': 0,
            'new_owners': 0,
            'entities': []
        }

        for row_data in decomposed_rows:
            try:
                bernie_number, canonical_name, owner_name, raw_status, blueprint = row_data

                funder, owner, task, metadata = self.orchestrator.process_decomposed_row(
                    bernie_number,
                    canonical_name,
                    owner_name,
                    raw_status,
                    blueprint
                )

                results['entities'].append({
                    'funder': funder,
                    'owner': owner,
                    'task': task,
                    'metadata': metadata
                })

                if metadata['was_status_new']:
                    results['new_statuses'] += 1
                if metadata['was_funder_new']:
                    results['new_funders'] += 1
                if metadata['was_owner_new']:
                    results['new_owners'] += 1

                results['processed'] += 1

            except Exception as e:
                results['errors'].append({
                    'row': row_data[4].core.task_id if row_data and len(row_data) > 4 else 'unknown',
                    'error': str(e)
                })

        return results