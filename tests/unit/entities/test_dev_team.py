"""
DevTeamMember Entity Tests - Pure Domain Logic

Written by Claude Code on 2025-10-29

PURPOSE: Validate DevTeamMember entity behavior without mocks or database
"""

import pytest
from data.basic_entities.dev_team import DevTeamMember


class TestDevTeamMemberConstruction:
    """Test DevTeamMember entity construction and validation"""

    def test_valid_member_creation(self):
        """Can create valid team member with name"""
        member = DevTeamMember(name='David Williams')

        assert member.name == 'David Williams'

    def test_missing_name_fails(self):
        """Member without name raises ValueError"""
        with pytest.raises(ValueError, match="Name is required"):
            DevTeamMember(name='')

    def test_whitespace_only_name_fails(self):
        """Member with whitespace-only name raises ValueError"""
        with pytest.raises(ValueError, match="Name is required"):
            DevTeamMember(name='   ')


class TestDevTeamMemberNameMatching:
    """Test name comparison logic"""

    def test_matches_name_case_insensitive(self):
        """Name matching is case-insensitive"""
        member = DevTeamMember(name='David Williams')

        assert member.matches_name('david williams')
        assert member.matches_name('DAVID WILLIAMS')
        assert member.matches_name('David Williams')

    def test_matches_name_different_name_fails(self):
        """Different names don't match"""
        member = DevTeamMember(name='David Williams')

        assert not member.matches_name('Jane Doe')
