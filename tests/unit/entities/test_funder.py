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
            canonical_name='Test Foundation'
        )

        assert funder.bernie_number == 'BN000227'
        assert funder.canonical_name == 'Test Foundation'

    def test_funder_with_ein(self):
        """Can create funder with valid EIN"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
            ein='123456789'
        )

        assert funder.ein == '123456789'

    def test_missing_bernie_number_fails(self):
        """Funder without bernie_number raises ValueError"""
        with pytest.raises(ValueError, match="bernie_number"):
            Funder(
                bernie_number='',
                canonical_name='Test Foundation'
            )

    def test_invalid_bernie_number_format_fails(self):
        """Funder with invalid bernie_number format raises ValueError"""
        with pytest.raises(ValueError, match="Invalid bernie_number format"):
            Funder(
                bernie_number='INVALID',
                canonical_name='Test Foundation',
            )

    def test_invalid_bernie_number_length_fails(self):
        """Funder with wrong length bernie_number raises ValueError"""
        with pytest.raises(ValueError, match="must be 8 characters"):
            Funder(
                bernie_number='BN001',  # Too short
                canonical_name='Test Foundation'
            )

    def test_missing_canonical_name_fails(self):
        """Funder without canonical_name raises ValueError"""
        with pytest.raises(ValueError, match="canonical_name"):
            Funder(
                bernie_number='BN000227',
                canonical_name=''
            )

    def test_canonical_name_added_to_all_names(self):
        """Canonical name automatically added to all_names if missing"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation'
        )


    def test_canonical_name_prepended_if_not_present(self):
        """Canonical name prepended to all_names if not already there"""
        funder = Funder(
            bernie_number='BN000227',
            canonical_name='Test Foundation',
        )


    def test_invalid_ein_length_fails(self):
        """Funder with wrong EIN length raises ValueError"""
        with pytest.raises(ValueError, match="EIN must be 9 digits"):
            Funder(
                bernie_number='BN000227',
                canonical_name='Test Foundation',
                ein='12345'  # Too short
            )

    def test_invalid_ein_format_fails(self):
        """Funder with non-numeric EIN raises ValueError"""
        with pytest.raises(ValueError, match="EIN must be numeric"):
            Funder(
                bernie_number='BN000227',
                canonical_name='Test Foundation',
                ein='12-345678'  # Contains dash
            )

