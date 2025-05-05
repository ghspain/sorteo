import os
import sys
import pytest
import pandas as pd

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from infrastructure.csv_repository import CSVRepository
from domain.models import Participant


class TestCSVImport:
    
    def test_csv_import_with_default_format(self):
        """Test importing a CSV with the default column format."""
        # Create a test CSV file
        test_file = "test_default_format.csv"
        data = pd.DataFrame({
            "Email": ["test1@example.com", "test2@example.com"],
            "First Name": ["John", "Jane"],
            "Last Name": ["Doe", "Smith"],
            "Checkin Date (UTC)": ["2023-01-01 10:00:00", ""]
        })
        data.to_csv(test_file, index=False)
        
        try:
            # Test the import
            repository = CSVRepository()
            with open(test_file, 'rb') as f:
                file_content = f.read()
                participants = repository.load_participants(file_content)
            
            # Assertions
            assert len(participants) == 2
            assert participants[0].email.value == "test1@example.com"
            assert participants[0].name.first_name == "John"
            assert participants[0].name.last_name == "Doe"
            assert participants[0].checked_in_at.is_checked_in
            
            assert participants[1].email.value == "test2@example.com"
            assert participants[1].checked_in_at.is_checked_in is False
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
                
    def test_csv_import_with_alternative_format(self):
        """Test importing a CSV with an alternative column format."""
        # Create a test CSV file
        test_file = "test_alt_format.csv"
        data = pd.DataFrame({
            "email": ["test1@example.com", "test2@example.com"],
            "first_name": ["John", "Jane"],
            "last_name": ["Doe", "Smith"],
            "checked_in_at": ["2023-01-01 10:00:00", ""]
        })
        data.to_csv(test_file, index=False)
        
        try:
            # Test the import
            repository = CSVRepository()
            with open(test_file, 'rb') as f:
                file_content = f.read()
                participants = repository.load_participants(file_content)
            
            # Assertions
            assert len(participants) == 2
            assert participants[0].email.value == "test1@example.com"
            assert participants[0].name.first_name == "John"
            assert participants[0].name.last_name == "Doe"
            assert participants[0].checked_in_at.is_checked_in
            
            assert participants[1].email.value == "test2@example.com"
            assert participants[1].checked_in_at.is_checked_in is False
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)