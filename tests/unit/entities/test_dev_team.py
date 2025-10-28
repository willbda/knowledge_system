"""
DevTeamMember Entity Tests - Pure Domain Logic

Written by Claude Code on 2025-10-13

PURPOSE: Validate DevTeamMember entity behavior
"""

import pytest
from data.entities import DevTeamMember


class TestDevTeamMemberConstruction:
    """Test DevTeamMember entity construction and validation"""

    def test_valid_member_creation(self):
        """Can create valid team member with required fields"""
        member = DevTeamMember(name='David Williams')

        assert member.name == 'David Williams'
        assert member.email is None
        assert member.role is None

    def test_member_with_all_fields(self):
        """Can create member with all fields"""
        member = DevTeamMember(
            name='David Williams',
            email='david@example.com',
            role='Grant Writer'
        )

        assert member.name == 'David Williams'
        assert member.email == 'david@example.com'
        assert member.role == 'Grant Writer'

    def test_missing_name_fails(self):
        """Member without name raises ValueError"""
        with pytest.raises(ValueError, match="name"):
            DevTeamMember(name='')

    def test_whitespace_only_name_fails(self):
        """Member with whitespace-only name raises ValueError"""
        with pytest.raises(ValueError, match="name"):
            DevTeamMember(name='   ')

    def test_invalid_email_fails(self):
        """Member with invalid email format raises ValueError"""
        with pytest.raises(ValueError, match="Invalid email format"):
            DevTeamMember(
                name='David Williams',
                email='not-an-email'  # Missing @
            )


class TestDevTeamMemberNameMatching:
    """Test name matching logic"""

    def test_matches_name_exact(self):
        """Exact name match works"""
        member = DevTeamMember(name='David Williams')

        assert member.matches_name('David Williams') is True

    def test_matches_name_case_insensitive(self):
        """Name matching is case-insensitive"""
        member = DevTeamMember(name='David Williams')

        assert member.matches_name('DAVID WILLIAMS') is True
        assert member.matches_name('david williams') is True
        assert member.matches_name('David WILLIAMS') is True

    def test_matches_name_with_whitespace(self):
        """Name matching handles whitespace"""
        member = DevTeamMember(name='David Williams')

        assert member.matches_name('  David Williams  ') is True

    def test_matches_name_no_match(self):
        """Returns False for non-matching name"""
        member = DevTeamMember(name='David Williams')

        assert member.matches_name('Jane Smith') is False

    def test_matches_name_empty_string(self):
        """Returns False for empty string"""
        member = DevTeamMember(name='David Williams')

        assert member.matches_name('') is False


class TestDevTeamMemberRepresentation:
    """Test string representation"""

    def test_repr_includes_name(self):
        """String representation includes name"""
        member = DevTeamMember(name='David Williams')

        repr_str = repr(member)
        assert 'David Williams' in repr_str

    def test_repr_includes_role_if_present(self):
        """String representation includes role when set"""
        member = DevTeamMember(
            name='David Williams',
            role='Grant Writer'
        )

        repr_str = repr(member)
        assert 'David Williams' in repr_str
        assert 'Grant Writer' in repr_str
