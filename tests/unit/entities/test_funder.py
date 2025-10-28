"""
Funder Entity Tests - Pure Domain Logic

Written by Claude Code on 2025-10-13

PURPOSE: Validate Funder entity behavior without mocks or database
"""

import pytest
from data.entities import Funder


class TestFunderConstruction:
    """Test Funder entity construction and validation"""

    def test_valid_funder_creation(self):
        """Can create valid funder with required fields"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation', 'Test Fund']
        )

        assert funder.bernie_number == 'BN000227'
        assert funder.canonical_name == 'Test Foundation'
        assert len(funder.all_names) == 2

    def test_funder_with_ein(self):
        """Can create funder with valid EIN"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation'],
            ein='123456789'
        )

        assert funder.ein == '123456789'

    def test_missing_bernie_number_fails(self):
        """Funder without bernie_number raises ValueError"""
        with pytest.raises(ValueError, match="bernie_number"):
            Funder(
                bernie_number='',
                canonical_name='Test Foundation',
                all_names=[]
            )

    def test_invalid_bernie_number_format_fails(self):
        """Funder with invalid bernie_number format raises ValueError"""
        with pytest.raises(ValueError, match="Invalid bernie_number format"):
            Funder(
                bernie_number='INVALID',
                canonical_name='Test Foundation',
                all_names=[]
            )

    def test_invalid_bernie_number_length_fails(self):
        """Funder with wrong length bernie_number raises ValueError"""
        with pytest.raises(ValueError, match="must be 8 characters"):
            Funder(
                bernie_number='BN001',  # Too short
                canonical_name='Test Foundation',
                all_names=[]
            )

    def test_missing_canonical_name_fails(self):
        """Funder without canonical_name raises ValueError"""
        with pytest.raises(ValueError, match="canonical_name"):
            Funder(
                bernie_number='BN000227',
                canonical_name='',
                all_names=[]
            )

    def test_canonical_name_added_to_all_names(self):
        """Canonical name automatically added to all_names if missing"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=[]  # Empty
        )

        assert 'Test Foundation' in funder.all_names
        assert len(funder.all_names) == 1

    def test_canonical_name_prepended_if_not_present(self):
        """Canonical name prepended to all_names if not already there"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Fund', 'TF']  # Doesn't include canonical
        )

        assert funder.all_names[0] == 'Test Foundation'
        assert len(funder.all_names) == 3

    def test_invalid_ein_length_fails(self):
        """Funder with wrong EIN length raises ValueError"""
        with pytest.raises(ValueError, match="EIN must be 9 digits"):
            Funder(
                bernie_number='BN000227',
                canonical_name='Test Foundation',
                all_names=[],
                ein='12345'  # Too short
            )

    def test_invalid_ein_format_fails(self):
        """Funder with non-numeric EIN raises ValueError"""
        with pytest.raises(ValueError, match="EIN must be numeric"):
            Funder(
                bernie_number='BN000227',
                canonical_name='Test Foundation',
                all_names=[],
                ein='12-345678'  # Contains dash
            )


class TestFunderAliasMatching:
    """Test alias matching - core domain logic"""

    def test_has_alias_exact_match(self):
        """Finds exact alias match (case-insensitive)"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation', 'Test Fund', 'TF Inc']
        )

        assert funder.has_alias('Test Fund') is True

    def test_has_alias_case_insensitive(self):
        """Alias matching is case-insensitive"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation']
        )

        assert funder.has_alias('TEST FOUNDATION') is True
        assert funder.has_alias('test foundation') is True
        assert funder.has_alias('Test FOUNDATION') is True

    def test_has_alias_with_whitespace(self):
        """Alias matching handles whitespace"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation']
        )

        assert funder.has_alias('  Test Foundation  ') is True

    def test_has_alias_no_match(self):
        """Returns False for non-matching name"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation']
        )

        assert funder.has_alias('Different Foundation') is False

    def test_has_alias_empty_string(self):
        """Returns False for empty string"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation']
        )

        assert funder.has_alias('') is False


class TestFunderNameMatching:
    """Test name matching with exact and fuzzy modes"""

    def test_matches_name_exact(self):
        """Exact name matching works"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation', 'Test Fund']
        )

        assert funder.matches_name('Test Foundation') is True
        assert funder.matches_name('Test Fund') is True

    def test_matches_name_fuzzy_substring(self):
        """Fuzzy matching finds substrings"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation']
        )

        # Fuzzy mode finds substrings
        assert funder.matches_name('Test', fuzzy=True) is True
        assert funder.matches_name('Foundation', fuzzy=True) is True

    def test_matches_name_fuzzy_false_no_substring(self):
        """Fuzzy matching still requires substring match"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation']
        )

        # Even in fuzzy mode, no match for completely different string
        assert funder.matches_name('Gates', fuzzy=True) is False

    def test_matches_name_exact_no_fuzzy(self):
        """Exact mode doesn't find partial matches"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation']
        )

        # Exact mode requires full match
        assert funder.matches_name('Test', fuzzy=False) is False


class TestFunderAddAlias:
    """Test adding aliases (mutable operation)"""

    def test_add_new_alias(self):
        """Can add new alias to funder"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation']
        )

        original_count = len(funder.all_names)
        funder.add_alias('Test Fund')

        assert len(funder.all_names) == original_count + 1
        assert 'Test Fund' in funder.all_names

    def test_add_duplicate_alias_ignored(self):
        """Adding duplicate alias is ignored"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation', 'Test Fund']
        )

        original_count = len(funder.all_names)
        funder.add_alias('Test Fund')  # Already exists

        assert len(funder.all_names) == original_count

    def test_add_empty_alias_ignored(self):
        """Adding empty alias is ignored"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation']
        )

        original_count = len(funder.all_names)
        funder.add_alias('')
        funder.add_alias('   ')

        assert len(funder.all_names) == original_count


class TestFunderRepresentation:
    """Test string representation"""

    def test_repr_includes_key_fields(self):
        """String representation includes identifying fields"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation', 'Test Fund'],
            ein='123456789'
        )

        repr_str = repr(funder)
        assert 'BN000227' in repr_str
        assert 'Test Foundation' in repr_str
        assert '123456789' in repr_str

    def test_repr_without_ein(self):
        """String representation works without EIN"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            all_names=['Test Foundation']
        )

        repr_str = repr(funder)
        assert 'BN000227' in repr_str
        assert 'ein=None' in repr_str
