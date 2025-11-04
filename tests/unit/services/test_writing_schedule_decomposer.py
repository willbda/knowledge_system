"""
Writing Schedule Decomposer Tests - Blueprint Architecture

Written by Claude Code on 2025-10-29
Updated by Claude Code on 2025-10-30 - Blueprint pattern

PURPOSE: Test decomposing WritingScheduleRow into blueprints with natural keys

DESIGN APPROACH:
- Tests validate blueprint creation from real data
- Use REAL data from writing_schedule.db
- Each test validates ONE meaningful transformation

NEW DECOMPOSITION PATTERN (Blueprint Architecture):
    WritingScheduleRow → (bernie_number, canonical_name, owner_name, raw_status, TaskBlueprint)

The orchestrator then resolves natural keys → foreign keys → entities.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from data.adapters.writing_schedule.schema import WritingScheduleRow
from data.blueprints import (
    TaskCoreBlueprint,
    LOIBlueprint,
    ProposalBlueprint,
    ReportBlueprint
)

# Import parser (formerly decomposer)
try:
    from data.adapters.writing_schedule.parser import decompose_row
    DECOMPOSER_EXISTS = True
except ImportError:
    DECOMPOSER_EXISTS = False


# Skip all tests if decomposer doesn't exist yet
pytestmark = pytest.mark.skipif(
    not DECOMPOSER_EXISTS,
    reason="Decomposer module not yet implemented"
)


class TestBlueprintDecomposition:
    """Test decompose_row returns blueprints with natural keys"""

    def test_decompose_loi_row_returns_blueprint(self):
        """Decompose LOI row → (bernie_number, canonical_name, owner_name, raw_status, LOIBlueprint)"""
        # Real LOI data from writing_schedule.db
        row = WritingScheduleRow(
            task_id="DOBBFD-GA25E-NSO-LOI-240830",
            bernie_identifier="BN0002E1",
            funder="Dobbs Foundation",
            type="LOI",
            status="3. LOI Submitted",
            deadline="2024-08-30",
            amount="100000.0",
            notification_date=None,
            owner="Jane Doe",
            last_modified="2025-09-24",
            fiscal_year="FY25",
            area="Education",
        )

        bernie_number, canonical_name, owner_name, raw_status, blueprint = decompose_row(row)

        # Validate natural keys returned
        assert bernie_number == "BN0002E1"
        assert canonical_name == "Dobbs Foundation"
        assert owner_name == "Jane Doe"
        assert raw_status == "3. LOI Submitted"

        # Validate blueprint structure
        assert isinstance(blueprint, LOIBlueprint)
        assert blueprint.core.task_id == "DOBBFD-GA25E-NSO-LOI-240830"
        assert blueprint.core.task_type == "LOI"
        assert blueprint.core.bernie_number == "BN0002E1"
        assert blueprint.core.status_text == "3. LOI Submitted"
        assert blueprint.core.owner_name == "Jane Doe"
        assert blueprint.core.deadline == datetime(2024, 8, 30)
        assert blueprint.core.fiscal_year == "FY25"
        assert blueprint.core.program_area == "Education"
        assert blueprint.amount_requested == Decimal("100000.0")

    def test_decompose_proposal_row_returns_blueprint(self):
        """Decompose Proposal row with award and community data"""
        # Real Proposal data from writing_schedule.db
        row = WritingScheduleRow(
            task_id="DELUCPFD-MN25E-NSO-PROP-240831",
            bernie_identifier="BN0000A6",
            funder="Deluxe Corporation Foundation",
            type="Proposal",
            status="8. Denied",
            deadline="2024-08-31",
            amount="25000.0",
            award="0.0",  # Denied, so award is 0
            owner="Jane Doe",
            last_modified="2025-09-25",
            fiscal_year="FY25",
            area="Education",
            communities="Greater Twin Cities",
            dev_team_notes="Reading and Math Corps in greater Twin Cities",
        )

        bernie_number, canonical_name, owner_name, raw_status, blueprint = decompose_row(row)

        # Validate natural keys
        assert bernie_number == "BN0000A6"
        assert canonical_name == "Deluxe Corporation Foundation"
        assert owner_name == "Jane Doe"
        assert raw_status == "8. Denied"

        # Validate ProposalBlueprint
        assert isinstance(blueprint, ProposalBlueprint)
        assert blueprint.core.task_id == "DELUCPFD-MN25E-NSO-PROP-240831"
        assert blueprint.core.bernie_number == "BN0000A6"
        assert blueprint.amount_requested == Decimal("25000.0")
        assert blueprint.award_amount == Decimal("0.0")
        assert blueprint.communities == "Greater Twin Cities"
        assert blueprint.dev_team_notes == "Reading and Math Corps in greater Twin Cities"

    def test_decompose_report_row_returns_blueprint(self):
        """Decompose Report row with report_type inference"""
        # Real Report data from writing_schedule.db
        row = WritingScheduleRow(
            task_id="NORTFD-MN25EL-NSO-REPO-240930",
            bernie_identifier="BN00013E",
            funder="Northland Foundation",
            type="Report",
            status="7. Report Submitted",
            deadline="2024-09-30",
            owner="David Williams",
            last_modified="2025-09-30",
            fiscal_year="FY25",
            area="Education",
        )

        bernie_number, canonical_name, owner_name, raw_status, blueprint = decompose_row(row)

        # Validate natural keys
        assert bernie_number == "BN00013E"
        assert canonical_name == "Northland Foundation"
        assert owner_name == "David Williams"
        assert raw_status == "7. Report Submitted"

        # Validate ReportBlueprint
        assert isinstance(blueprint, ReportBlueprint)
        assert blueprint.core.task_id == "NORTFD-MN25EL-NSO-REPO-240930"
        assert blueprint.report_type == "Report"

    def test_decompose_final_report_row_returns_blueprint(self):
        """Decompose Final Report row with specific report_type"""
        # Real Final Report data from writing_schedule.db
        row = WritingScheduleRow(
            task_id="RICHMSCH-MN25E-NSO-FIRE-240911",
            bernie_identifier="BN00015E",
            funder="Richard M. Schulze Family Foundation",
            type="Final Report",
            status="7. Report Submitted",
            deadline="2024-09-11",
            owner="Allie Handberg",
            last_modified="2025-04-08",
            fiscal_year="FY25",
            area="Education",
        )

        bernie_number, canonical_name, owner_name, raw_status, blueprint = decompose_row(row)

        # Validate natural keys
        assert bernie_number == "BN00015E"
        assert canonical_name == "Richard M. Schulze Family Foundation"
        assert owner_name == "Allie Handberg"

        # Validate ReportBlueprint with specific type
        assert isinstance(blueprint, ReportBlueprint)
        assert blueprint.report_type == "Final Report"

    def test_decompose_row_missing_bernie_number_uses_unknown(self):
        """Missing bernie_identifier → uses 'UNKNOWN' as bernie_number"""
        row = WritingScheduleRow(
            task_id="TEST-123",
            bernie_identifier=None,  # Missing!
            funder="Some Foundation",
            type="LOI",
            deadline="2024-12-31",
        )

        bernie_number, canonical_name, owner_name, raw_status, blueprint = decompose_row(row)

        assert bernie_number == "UNKNOWN"
        assert canonical_name == "Some Foundation"

    def test_decompose_row_missing_owner_returns_none(self):
        """Missing owner → returns None for owner_name"""
        row = WritingScheduleRow(
            task_id="TEST-123",
            bernie_identifier="BN0002E1",
            funder="Test Foundation",
            type="LOI",
            deadline="2024-12-31",
            owner=None,  # Missing!
        )

        bernie_number, canonical_name, owner_name, raw_status, blueprint = decompose_row(row)

        assert owner_name is None
        assert blueprint.core.owner_name is None

    def test_decompose_row_with_program_fields(self):
        """Program fields (fiscal_year, area, initiative) mapped to TaskCoreBlueprint"""
        row = WritingScheduleRow(
            task_id="TEST-PROG-001",
            bernie_identifier="BN0002E1",
            funder="Test Foundation",
            type="Proposal",
            deadline="2024-12-31",
            fiscal_year="FY25",
            area="Education",
            initiative="Early Childhood",
        )

        bernie_number, canonical_name, owner_name, raw_status, blueprint = decompose_row(row)

        # Validate program fields in TaskCoreBlueprint
        assert blueprint.core.fiscal_year == "FY25"
        assert blueprint.core.program_area == "Education"
        assert blueprint.core.initiative == "Early Childhood"


class TestBlueprintNaturalKeys:
    """Test that blueprints contain natural keys (strings), not foreign keys (integers)"""

    def test_blueprint_contains_bernie_number_not_funder_id(self):
        """Blueprint contains bernie_number (natural key), not funder_id (FK)"""
        row = WritingScheduleRow(
            task_id="TEST-001",
            bernie_identifier="BN0002E1",
            funder="Dobbs Foundation",
            type="LOI",
            deadline="2024-12-31",
        )

        _, _, _, _, blueprint = decompose_row(row)

        # Natural key present
        assert blueprint.core.bernie_number == "BN0002E1"
        # FK not present
        assert not hasattr(blueprint.core, 'funder_id')

    def test_blueprint_contains_status_text_not_status_id(self):
        """Blueprint contains status_text (natural key), not status_id (FK)"""
        row = WritingScheduleRow(
            task_id="TEST-001",
            bernie_identifier="BN0002E1",
            funder="Test Foundation",
            type="LOI",
            status="3. LOI Submitted",
            deadline="2024-12-31",
        )

        _, _, _, raw_status, blueprint = decompose_row(row)

        # Natural key present
        assert blueprint.core.status_text == "3. LOI Submitted"
        assert raw_status == "3. LOI Submitted"
        # FK not present
        assert not hasattr(blueprint.core, 'status_id')

    def test_blueprint_contains_owner_name_not_owner_id(self):
        """Blueprint contains owner_name (natural key), not owner_id (FK)"""
        row = WritingScheduleRow(
            task_id="TEST-001",
            bernie_identifier="BN0002E1",
            funder="Test Foundation",
            type="LOI",
            deadline="2024-12-31",
            owner="Jane Doe",
        )

        _, _, owner_name, _, blueprint = decompose_row(row)

        # Natural key present
        assert blueprint.core.owner_name == "Jane Doe"
        assert owner_name == "Jane Doe"
        # FK not present
        assert not hasattr(blueprint.core, 'owner_id')
