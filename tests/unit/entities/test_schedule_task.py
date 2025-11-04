"""
Scheduled Task Entity Tests - Pure Domain Logic

Written by Claude Code on 2025-10-29

PURPOSE: Validate LOI, Proposal, Report, and Reminder entities
Focus on composition and entity-specific validation
"""

import pytest
from datetime import datetime
from decimal import Decimal
from data.basic_entities.schedule_task import (
    TaskCore, LOI, Proposal, Report, Reminder
)


class TestTaskCoreComposition:
    """Test that TaskCore provides scheduling data to all entities"""

    def test_loi_exposes_task_properties(self):
        """LOI exposes TaskCore properties via protocol"""
        core = TaskCore(
            task_id='L123',
            task_type='LOI',
            bernie_number='BN0002E1',
            status_id=1,
            deadline=datetime(2025, 12, 1),
            owner_id=5,
            last_modified=datetime.now()
        )
        loi = LOI(
            core=core,
            notification_date=None,
            amount_requested=None
        )

        assert loi.task_id == 'L123'
        assert loi.deadline == datetime(2025, 12, 1)
        assert loi.task_type == 'LOI'
        assert loi.core.status_id == 1
        assert loi.core.bernie_number == 'BN0002E1'
        assert loi.core.owner_id == 5

    def test_proposal_exposes_task_properties(self):
        """Proposal exposes TaskCore properties via protocol"""
        core = TaskCore(
            task_id='P456',
            task_type='Proposal',
            bernie_number='BN0000A6',
            status_id=2,
            deadline=datetime(2025, 12, 15),
            owner_id=5,
            last_modified=datetime.now()
        )
        proposal = Proposal(
            core=core,
            amount_requested=Decimal('50000')
        )

        assert proposal.task_id == 'P456'
        assert proposal.deadline == datetime(2025, 12, 15)
        assert proposal.task_type == 'Proposal'
        assert proposal.core.status_id == 2
        assert proposal.core.bernie_number == 'BN0000A6'


class TestProposalValidation:
    """Test Proposal-specific validation rules"""

    def test_negative_amount_fails(self):
        """Proposal with negative amount raises ValueError"""
        core = TaskCore(
            task_id='P999',
            task_type='Proposal',
            bernie_number='BN0002E1',
            status_id=3,
            deadline=datetime(2025, 12, 1),
            owner_id=5,
            last_modified=datetime.now()
        )

        with pytest.raises(ValueError, match="amount must be positive"):
            Proposal(
                core=core,
                amount_requested=Decimal('-1000')
            )

    def test_positive_amount_succeeds(self):
        """Proposal with positive amount succeeds"""
        core = TaskCore(
            task_id='P999',
            task_type='Proposal',
            bernie_number='BN0002E1',
            status_id=3,
            deadline=datetime(2025, 12, 1),
            owner_id=5,
            last_modified=datetime.now()
        )

        proposal = Proposal(
            core=core,
            amount_requested=Decimal('50000')
        )
        assert proposal.amount_requested == Decimal('50000')


class TestEntityRelationships:
    """Test relationship fields between entities"""

    def test_loi_can_link_to_proposal(self):
        """LOI can reference a related proposal via task_id"""
        core = TaskCore(
            task_id='L100',
            task_type='LOI',
            bernie_number='BN0002E1',
            status_id=4,
            deadline=datetime(2025, 11, 1),
            owner_id=5,
            last_modified=datetime.now()
        )
        loi = LOI(
            core=core,
            notification_date=None,
            amount_requested=None,
            related_proposal_id='P200'
        )

        assert loi.related_proposal_id == 'P200'

    def test_report_can_link_to_proposal(self):
        """Report can reference the proposal being reported on"""
        core = TaskCore(
            task_id='R300',
            task_type='Report',
            bernie_number='BN0002E1',
            status_id=5,
            deadline=datetime(2026, 1, 15),
            owner_id=5,
            last_modified=datetime.now()
        )
        report = Report(
            core=core,
            report_type='Final Report',
            related_proposal_id='P200'
        )

        assert report.related_proposal_id == 'P200'
