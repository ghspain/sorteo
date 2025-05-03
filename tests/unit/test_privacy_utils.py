"""
Unit tests for privacy and cleanup utilities.
"""
import os
import sys
import tempfile
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.privacy import mask_pii, generate_pseudonym
from utils.csv_privacy import (
    anonymize_csv, pseudonymize_csv, create_gdpr_compliant_csv,
    check_gdpr_compliance, identify_pii_fields
)


class TestPrivacyUtils(unittest.TestCase):
    """Test case for privacy utilities."""
    
    def test_mask_pii_email(self):
        """Test that emails are properly masked."""
        # Arrange
        email = "john.doe@example.com"
        
        # Act
        masked = mask_pii(email)
        
        # Assert
        self.assertNotEqual(masked, email)
        self.assertTrue('@example.com' in masked)
        self.assertTrue(masked.startswith('j'))
        self.assertTrue(masked[1:-10].replace('*', '') == '')
    
    def test_mask_pii_phone(self):
        """Test that phone numbers are properly masked."""
        # Arrange
        phone = "+1 (555) 123-4567"
        
        # Act
        masked = mask_pii(phone)
        
        # Assert
        self.assertNotEqual(masked, phone)
        self.assertTrue(masked.endswith('4567'))
        self.assertFalse('+1' in masked)
    
    def test_mask_pii_name(self):
        """Test that names are properly masked."""
        # Arrange
        name = "John Doe"
        
        # Act
        masked = mask_pii(name)
        
        # Assert
        self.assertNotEqual(masked, name)
        self.assertTrue(masked.startswith('J'))
        self.assertTrue(' D' in masked)
    
    def test_mask_pii_combined(self):
        """Test that text with multiple PII items is properly masked."""
        # Arrange
        text = "Contact John Doe at john.doe@example.com or +1 (555) 123-4567"
        
        # Act
        masked = mask_pii(text)
        
        # Assert
        self.assertNotEqual(masked, text)
        self.assertTrue('@example.com' in masked)
        self.assertTrue('4567' in masked)
        self.assertTrue('J***' in masked)
        self.assertTrue('D**' in masked)
    
    def test_generate_pseudonym(self):
        """Test that pseudonyms are consistent for the same input."""
        # Arrange
        text = "john.doe@example.com"
        
        # Act
        pseudo1 = generate_pseudonym(text)
        pseudo2 = generate_pseudonym(text)
        pseudo3 = generate_pseudonym(text, "different-salt")
        
        # Assert
        self.assertEqual(pseudo1, pseudo2)
        self.assertNotEqual(pseudo1, pseudo3)
        self.assertEqual(len(pseudo1), 8)
    
    def test_identify_pii_fields(self):
        """Test that PII fields are correctly identified."""
        # Arrange
        columns = ["Email", "First Name", "Last Name", "Order ID", "IP Address", "other_field"]
        
        # Act
        pii_fields = identify_pii_fields(columns)
        
        # Assert
        self.assertIn("Email", pii_fields)
        self.assertIn("First Name", pii_fields)
        self.assertIn("Last Name", pii_fields)
        self.assertIn("IP Address", pii_fields)
        self.assertNotIn("Order ID", pii_fields)
        self.assertNotIn("other_field", pii_fields)


class TestCsvPrivacy(unittest.TestCase):
    """Test case for CSV privacy utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary CSV file for testing
        self.test_data = pd.DataFrame({
            'Email': ['john.doe@example.com', 'jane.smith@example.com'],
            'First Name': ['John', 'Jane'],
            'Last Name': ['Doe', 'Smith'],
            'Checkin Date (UTC)': ['2023-05-01T10:30:00Z', '2023-05-01T11:45:00Z'],
            'Order ID': ['ORD123', 'ORD456']
        })
        
        self.temp_dir = tempfile.mkdtemp()
        self.input_csv = os.path.join(self.temp_dir, 'input.csv')
        self.output_csv = os.path.join(self.temp_dir, 'output.csv')
        
        self.test_data.to_csv(self.input_csv, index=False)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary files
        if os.path.exists(self.input_csv):
            os.unlink(self.input_csv)
        
        if os.path.exists(self.output_csv):
            os.unlink(self.output_csv)
        
        os.rmdir(self.temp_dir)
    
    def test_anonymize_csv(self):
        """Test that CSV anonymization works correctly."""
        # Act
        stats = anonymize_csv(self.input_csv, self.output_csv)
        
        # Assert
        self.assertIn('pii_fields_identified', stats)
        self.assertGreater(stats['pii_items_masked'], 0)
        
        # Check output file
        df = pd.read_csv(self.output_csv)
        self.assertEqual(len(df), len(self.test_data))
        
        # Verify anonymization
        self.assertNotEqual(df['Email'][0], 'john.doe@example.com')
        self.assertIn('@example.com', df['Email'][0])
    
    def test_pseudonymize_csv(self):
        """Test that CSV pseudonymization works correctly."""
        # Act
        stats = pseudonymize_csv(self.input_csv, self.output_csv, "test-salt")
        
        # Assert
        self.assertGreater(stats['pii_items_replaced'], 0)
        
        # Check output file
        df = pd.read_csv(self.output_csv)
        self.assertEqual(len(df), len(self.test_data))
        
        # Verify pseudonymization
        self.assertNotEqual(df['Email'][0], 'john.doe@example.com')
        self.assertEqual(df['Email'][0], df['Email'][0])  # Should be consistent
    
    def test_create_gdpr_compliant_csv(self):
        """Test that GDPR-compliant CSV creation works correctly."""
        # Act
        stats = create_gdpr_compliant_csv(self.input_csv, self.output_csv)
        
        # Assert
        self.assertTrue(stats['retained_columns'] >= 4)  # Should keep required fields
        
        # Check output file
        df = pd.read_csv(self.output_csv)
        self.assertEqual(len(df), len(self.test_data))
        
        # Verify required columns are preserved
        self.assertIn('Email', df.columns)
        self.assertIn('First Name', df.columns)
        self.assertIn('Last Name', df.columns)
        self.assertIn('Checkin Date (UTC)', df.columns)
    
    def test_check_gdpr_compliance(self):
        """Test that GDPR compliance checking works correctly."""
        # Act
        report = check_gdpr_compliance(self.input_csv)
        
        # Assert - should be compliant since we have standard fields
        self.assertTrue(report['compliant'])


if __name__ == '__main__':
    unittest.main()