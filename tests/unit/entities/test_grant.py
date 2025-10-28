"""
Grant Entity Tests - Pure Domain Logic

Written by Claude Code on 2025-10-13

PURPOSE: Validate Grant entity behavior without mocks or database

PRINCIPLES:
- Pure entity testing - just construct and call methods
- Zero external dependencies
- Test validation, business logic, edge cases
"""

import pytest
from datetime import datetime, timedelta
from data.entities import Grant, GrantStatus


class TestGrantConstruction:
    """Test Grant entity construction and validation"""

    def test_valid_grant_creation(self):
        """Can create valid grant with required fields"""
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Annual Grant Program'
        )

        assert grant.bernie_number == 'BN000227'
        assert grant.funder_name == 'Test Foundation'
        assert grant.program_name == 'Annual Grant Program'
        assert grant.status == GrantStatus.ACTIVE.value

    def test_grant_with_all_fields(self):
        """Can create grant with all optional fields"""
        deadline = datetime(2025, 12, 31)
        start_date = datetime(2026, 1, 1)
        end_date = datetime(2026, 12, 31)

        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Annual Grant Program',
            task_id='TASK-123',
            deadline=deadline,
            dev_lead='David',
            status=GrantStatus.SUBMITTED.value,
            amount_requested=50000.0,
            amount_awarded=45000.0,
            type_='Proposal',
            area='Education',
            state='MN',
            initiative='Civic Engagement',
            grant_start_date=start_date,
            grant_end_date=end_date,
            dev_team_notes='Priority grant'
        )

        assert grant.task_id == 'TASK-123'
        assert grant.deadline == deadline
        assert grant.dev_lead == 'David'
        assert grant.amount_requested == 50000.0
        assert grant.type_ == 'Proposal'

    def test_missing_bernie_number_fails(self):
        """Grant without bernie_number raises ValueError"""
        with pytest.raises(ValueError, match="bernie_number"):
            Grant(
                bernie_number='',
                funder_name='Test Foundation',
                program_name='Test Program'
            )

    def test_invalid_bernie_number_format_fails(self):
        """Grant with invalid bernie_number format raises ValueError"""
        with pytest.raises(ValueError, match="Invalid bernie_number format"):
            Grant(
                bernie_number='INVALID',
                funder_name='Test Foundation',
                program_name='Test Program'
            )

    def test_missing_funder_name_fails(self):
        """Grant without funder_name raises ValueError"""
        with pytest.raises(ValueError, match="funder_name"):
            Grant(
                bernie_number='BN000227',
                funder_name='',
                program_name='Test Program'
            )

    def test_missing_program_name_fails(self):
        """Grant without program_name raises ValueError"""
        with pytest.raises(ValueError, match="program_name"):
            Grant(
                bernie_number='BN000227',
                funder_name='Test Foundation',
                program_name=''
            )

    def test_negative_amount_requested_fails(self):
        """Grant with negative amount_requested raises ValueError"""
        with pytest.raises(ValueError, match="amount_requested must be >= 0"):
            Grant(
                bernie_number='BN000227',
                funder_name='Test Foundation',
                program_name='Test Program',
                amount_requested=-1000.0
            )

    def test_negative_amount_awarded_fails(self):
        """Grant with negative amount_awarded raises ValueError"""
        with pytest.raises(ValueError, match="amount_awarded must be >= 0"):
            Grant(
                bernie_number='BN000227',
                funder_name='Test Foundation',
                program_name='Test Program',
                amount_awarded=-1000.0
            )


class TestGrantUrgency:
    """Test Grant urgency detection - core business logic"""

    def test_urgent_grant_within_7_days(self):
        """Grant with deadline in 5 days is urgent"""
        deadline = datetime.now() + timedelta(days=5)
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            deadline=deadline
        )

        assert grant.is_urgent() is True

    def test_urgent_grant_exact_threshold(self):
        """Grant with deadline exactly at threshold (7 days) is urgent"""
        deadline = datetime.now() + timedelta(days=7)
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            deadline=deadline
        )

        assert grant.is_urgent() is True

    def test_not_urgent_beyond_threshold(self):
        """Grant with deadline in 14 days is not urgent"""
        deadline = datetime.now() + timedelta(days=14)
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            deadline=deadline
        )

        assert grant.is_urgent() is False

    def test_not_urgent_without_deadline(self):
        """Grant without deadline is not urgent"""
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            deadline=None
        )

        assert grant.is_urgent() is False

    def test_custom_urgency_threshold(self):
        """Can use custom urgency threshold"""
        deadline = datetime.now() + timedelta(days=10)
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            deadline=deadline
        )

        # Not urgent with default 7-day threshold
        assert grant.is_urgent() is False

        # Urgent with 14-day threshold
        assert grant.is_urgent(urgency_threshold_days=14) is True


class TestGrantOverdue:
    """Test overdue detection"""

    def test_overdue_past_deadline(self):
        """Grant past deadline is overdue"""
        deadline = datetime.now() - timedelta(days=5)
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            deadline=deadline
        )

        assert grant.is_overdue() is True

    def test_not_overdue_future_deadline(self):
        """Grant with future deadline is not overdue"""
        deadline = datetime.now() + timedelta(days=5)
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            deadline=deadline
        )

        assert grant.is_overdue() is False

    def test_not_overdue_without_deadline(self):
        """Grant without deadline is not overdue"""
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            deadline=None
        )

        assert grant.is_overdue() is False


class TestGrantDaysUntilDeadline:
    """Test days until deadline calculation"""

    def test_days_until_future_deadline(self):
        """Calculate days until future deadline"""
        deadline = datetime.now() + timedelta(days=10)
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            deadline=deadline
        )

        days = grant.days_until_deadline()
        assert days is not None
        assert 9 <= days <= 10  # Account for time precision

    def test_days_until_past_deadline_negative(self):
        """Days until past deadline is negative"""
        deadline = datetime.now() - timedelta(days=5)
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            deadline=deadline
        )

        days = grant.days_until_deadline()
        assert days is not None
        assert days < 0

    def test_days_until_deadline_none_without_deadline(self):
        """Returns None when no deadline set"""
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            deadline=None
        )

        assert grant.days_until_deadline() is None


class TestGrantActiveStatus:
    """Test active status detection"""

    def test_active_status_is_active(self):
        """Grant with active status is active"""
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            status=GrantStatus.ACTIVE.value
        )

        assert grant.is_active() is True

    def test_submitted_status_is_active(self):
        """Grant with submitted status is active"""
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            status=GrantStatus.SUBMITTED.value
        )

        assert grant.is_active() is True

    def test_denied_status_not_active(self):
        """Grant with denied status is not active"""
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            status=GrantStatus.DENIED.value
        )

        assert grant.is_active() is False

    def test_completed_status_not_active(self):
        """Grant with completed status is not active"""
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Test Program',
            status=GrantStatus.COMPLETED.value
        )

        assert grant.is_active() is False


class TestGrantRepresentation:
    """Test string representation"""

    def test_repr_includes_key_fields(self):
        """String representation includes key identifying fields"""
        deadline = datetime(2025, 12, 31)
        grant = Grant(
            bernie_number='BN000227',
            funder_name='Test Foundation',
            program_name='Annual Program',
            deadline=deadline,
            status=GrantStatus.ACTIVE.value
        )

        repr_str = repr(grant)
        assert 'BN000227' in repr_str
        assert 'Test Foundation' in repr_str
        assert 'Annual Program' in repr_str
        assert '2025-12-31' in repr_str
        assert 'active' in repr_str
