"""
Document Entity Tests - Pure Domain Logic

Written by Claude Code on 2025-10-29

PURPOSE: Validate Document entity behavior without mocks or database
"""

import pytest
from data.basic_entities.document import Document


class TestDocumentConstruction:
    """Test Document entity construction and validation"""

    def test_valid_document_creation(self):
        """Can create valid document with required fields"""
        doc = Document(
            file_path='/path/to/file.pdf',
            file_name='proposal.pdf'
        )

        assert doc.file_path == '/path/to/file.pdf'
        assert doc.file_name == 'proposal.pdf'

    def test_missing_file_path_fails(self):
        """Document without file_path raises ValueError"""
        with pytest.raises(ValueError, match="File path is required"):
            Document(
                file_path='',
                file_name='proposal.pdf'
            )

    def test_missing_file_name_fails(self):
        """Document without file_name raises ValueError"""
        with pytest.raises(ValueError, match="File name is required"):
            Document(
                file_path='/path/to/file.pdf',
                file_name=''
            )
