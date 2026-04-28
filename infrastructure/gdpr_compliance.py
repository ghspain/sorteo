"""
GDPR compliance utilities for the raffle application.

This module provides tools and utilities to ensure compliance with the
General Data Protection Regulation (GDPR) when handling participant data.
"""
import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional

from utils.csv_privacy import (
    create_gdpr_compliant_csv,
    check_gdpr_compliance,
    apply_data_retention_policy
)

logger = logging.getLogger(__name__)


class GDPRComplianceManager:
    """
    Manager for GDPR compliance across the raffle application.
    
    This class provides methods to enforce GDPR compliance, including:
    - Data retention policies
    - Data minimization
    - Consent management
    - Right to be forgotten
    - Right to access
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the GDPR compliance manager.
        
        Args:
            config_file: Path to a configuration file for GDPR settings
        """
        self.config = self._load_config(config_file)
        
        # Default settings if not specified in config
        self.data_retention_days = self.config.get('data_retention_days', 30)
        self.enabled = self.config.get('enabled', True)
        self.require_consent = self.config.get('require_consent', True)
        self.logs_dir = self.config.get('logs_dir', 'gdpr_logs')
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir, exist_ok=True)
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """
        Load GDPR configuration from a file or use defaults.
        
        Args:
            config_file: Path to the configuration file
            
        Returns:
            Dictionary of configuration settings
        """
        default_config = {
            'data_retention_days': 30,
            'enabled': True,
            'require_consent': True,
            'logs_dir': 'gdpr_logs',
            'allowed_purposes': ['raffle', 'winners_notification'],
            'minimum_required_fields': ['email', 'first_name', 'last_name', 'check_in']
        }
        
        if not config_file or not os.path.exists(config_file):
            logger.info("No GDPR config file found. Using default settings.")
            return default_config
            
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing settings
                return {**default_config, **config}
        except Exception as e:
            logger.error(f"Error loading GDPR config: {e}")
            return default_config
    
    def enforce_data_retention(self, data_dir: str) -> Dict[str, Any]:
        """
        Apply data retention policy to CSV files in the specified directory.
        
        Args:
            data_dir: Directory containing CSV files to manage
            
        Returns:
            Report of actions taken
        """
        if not self.enabled:
            logger.info("GDPR compliance is disabled. Skipping data retention enforcement.")
            return {'status': 'skipped', 'reason': 'GDPR compliance disabled'}
        
        logger.info(f"Applying data retention policy ({self.data_retention_days} days) to {data_dir}")
        
        result = apply_data_retention_policy(data_dir, self.data_retention_days)
        
        # Log the action
        self._log_action({
            'action': 'data_retention',
            'directory': data_dir,
            'retention_days': self.data_retention_days,
            'files_processed': result.get('files_scanned', 0),
            'files_deleted': result.get('files_deleted', 0),
            'bytes_reclaimed': result.get('bytes_reclaimed', 0)
        })
        
        return result
    
    def create_compliant_dataset(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        Create a GDPR-compliant dataset from an input CSV file.
        
        Args:
            input_file: Path to the input CSV file
            output_file: Path to write the GDPR-compliant CSV file
            
        Returns:
            Report of actions taken
        """
        if not self.enabled:
            logger.info("GDPR compliance is disabled. Skipping compliant dataset creation.")
            return {'status': 'skipped', 'reason': 'GDPR compliance disabled'}
        
        logger.info(f"Creating GDPR-compliant dataset from {input_file}")
        
        result = create_gdpr_compliant_csv(input_file, output_file)
        
        # Log the action
        self._log_action({
            'action': 'create_compliant_dataset',
            'input_file': input_file,
            'output_file': output_file,
            'original_columns': result.get('original_columns', 0),
            'retained_columns': result.get('retained_columns', 0),
            'removed_columns': result.get('removed_columns', 0),
            'pii_items_minimized': result.get('pii_items_minimized', 0)
        })
        
        return result
    
    def check_file_compliance(self, file_path: str) -> Dict[str, Any]:
        """
        Check if a CSV file complies with GDPR principles.
        
        Args:
            file_path: Path to the CSV file to check
            
        Returns:
            Report of compliance status
        """
        if not self.enabled:
            logger.info("GDPR compliance is disabled. Skipping compliance check.")
            return {'status': 'skipped', 'reason': 'GDPR compliance disabled'}
        
        logger.info(f"Checking GDPR compliance of {file_path}")
        
        result = check_gdpr_compliance(file_path)
        
        # Log the action
        self._log_action({
            'action': 'check_compliance',
            'file_path': file_path,
            'compliant': result.get('compliant', False),
            'issues_count': len(result.get('issues', [])),
            'recommendations_count': len(result.get('recommendations', []))
        })
        
        return result
    
    def handle_right_to_be_forgotten(self, email: str, data_dir: str) -> Dict[str, Any]:
        """
        Handle a right to be forgotten request for a specific email.
        
        Searches for the email in all CSV files in the data directory and
        removes all instances of that email.
        
        Args:
            email: Email address to remove
            data_dir: Directory containing CSV files to search
            
        Returns:
            Report of actions taken
        """
        import pandas as pd
        import glob
        
        if not self.enabled:
            logger.info("GDPR compliance is disabled. Skipping right to be forgotten.")
            return {'status': 'skipped', 'reason': 'GDPR compliance disabled'}
        
        logger.info(f"Processing right to be forgotten request for {email}")
        
        result = {
            'files_processed': 0,
            'files_modified': 0,
            'records_removed': 0
        }
        
        # Find all CSV files
        for csv_file in glob.glob(os.path.join(data_dir, '**', '*.csv'), recursive=True):
            result['files_processed'] += 1
            
            try:
                # Read the CSV file
                df = pd.read_csv(csv_file)
                
                # Check if email column exists
                email_column = next((col for col in df.columns if col.lower() in ['email', 'email_address']), None)
                
                if email_column and email in df[email_column].values:
                    # Count records to be removed
                    records_to_remove = df[df[email_column] == email].shape[0]
                    result['records_removed'] += records_to_remove
                    
                    # Remove records with the email
                    df = df[df[email_column] != email]
                    
                    # Write back to the file
                    df.to_csv(csv_file, index=False)
                    result['files_modified'] += 1
            except Exception as e:
                logger.error(f"Error processing {csv_file}: {e}")
        
        # Log the action
        self._log_action({
            'action': 'right_to_be_forgotten',
            'email': email,
            'data_dir': data_dir,
            'files_processed': result['files_processed'],
            'files_modified': result['files_modified'],
            'records_removed': result['records_removed']
        })
        
        return result
    
    def handle_data_access_request(self, email: str, data_dir: str) -> Dict[str, Any]:
        """
        Handle a data access request for a specific email.
        
        Searches for the email in all CSV files in the data directory and
        extracts all data related to that email.
        
        Args:
            email: Email address to search for
            data_dir: Directory containing CSV files to search
            
        Returns:
            Dictionary with all data found for the email
        """
        import pandas as pd
        import glob
        
        if not self.enabled:
            logger.info("GDPR compliance is disabled. Skipping data access request.")
            return {'status': 'skipped', 'reason': 'GDPR compliance disabled'}
        
        logger.info(f"Processing data access request for {email}")
        
        result = {
            'email': email,
            'files_processed': 0,
            'records_found': 0,
            'data': []
        }
        
        # Find all CSV files
        for csv_file in glob.glob(os.path.join(data_dir, '**', '*.csv'), recursive=True):
            result['files_processed'] += 1
            
            try:
                # Read the CSV file
                df = pd.read_csv(csv_file)
                
                # Check if email column exists
                email_column = next((col for col in df.columns if col.lower() in ['email', 'email_address']), None)
                
                if email_column and email in df[email_column].values:
                    # Extract records with the email
                    records = df[df[email_column] == email].to_dict('records')
                    result['records_found'] += len(records)
                    
                    for record in records:
                        result['data'].append({
                            'source_file': csv_file,
                            'record': record
                        })
            except Exception as e:
                logger.error(f"Error processing {csv_file}: {e}")
        
        # Log the action
        self._log_action({
            'action': 'data_access_request',
            'email': email,
            'data_dir': data_dir,
            'files_processed': result['files_processed'],
            'records_found': result['records_found']
        })
        
        return result
    
    def _log_action(self, action_data: Dict[str, Any]) -> None:
        """
        Log a GDPR compliance action.
        
        Args:
            action_data: Dictionary with action details
        """
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            **action_data
        }
        
        # Create a log file for the current month
        current_month = datetime.datetime.now().strftime('%Y-%m')
        log_file = os.path.join(self.logs_dir, f'gdpr_log_{current_month}.jsonl')
        
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing to GDPR log: {e}")


# Helper functions for GDPR compliance

def is_personal_data(data_type: str) -> bool:
    """
    Check if a data type is considered personal data under GDPR.
    
    Args:
        data_type: The type of data to check
        
    Returns:
        True if the data type is personal data, False otherwise
    """
    personal_data_types = {
        'email', 'name', 'full_name', 'first_name', 'last_name',
        'address', 'phone', 'phone_number', 'mobile', 'mobile_number',
        'date_of_birth', 'dob', 'birth_date', 'gender',
        'ip_address', 'id', 'user_id', 'account_id',
        'ssn', 'social_security', 'passport', 'id_number',
        'location', 'geo', 'gps', 'coordinates',
        'credit_card', 'bank_account', 'iban'
    }
    
    return data_type.lower().replace('_', '') in personal_data_types

def generate_privacy_policy(app_name: str, email: str, organization: str) -> str:
    """
    Generate a basic GDPR-compliant privacy policy.
    
    Args:
        app_name: Name of the application
        email: Contact email for privacy questions
        organization: Organization name
        
    Returns:
        A GDPR-compliant privacy policy text
    """
    return f"""
# Privacy Policy for {app_name}

Last updated: {datetime.datetime.now().strftime('%Y-%m-%d')}

## 1. Introduction

{organization} ("we", "us", or "our") operates the {app_name} application (the "Service"). This page informs you of our policies regarding the collection, use, and disclosure of personal data when you use our Service.

We use your data to provide and improve the Service. By using the Service, you agree to the collection and use of information in accordance with this policy.

## 2. Data Collection and Use

We collect several types of information for various purposes to provide and improve our Service to you:

- **Email address**: To identify participants and prevent duplicate entries
- **Name**: To identify winners and address them properly
- **Check-in information**: To verify eligibility for the raffle

## 3. Data Retention

We will retain your personal data only for as long as is necessary for the purposes set out in this Privacy Policy. We will retain and use your personal data to the extent necessary to comply with our legal obligations, resolve disputes, and enforce our legal agreements and policies.

## 4. Data Security

The security of your data is important to us, but remember that no method of transmission over the Internet, or method of electronic storage is 100% secure. While we strive to use commercially acceptable means to protect your personal data, we cannot guarantee its absolute security.

## 5. Your Data Protection Rights

Under the General Data Protection Regulation (GDPR), you have certain data protection rights:

- The right to access, update, or delete the information we have on you
- The right of rectification
- The right to object
- The right of restriction
- The right to data portability
- The right to withdraw consent

## 6. Contact Us

If you have any questions about this Privacy Policy, please contact us at {email}.
    """

def generate_consent_form(app_name: str, purposes: List[str]) -> str:
    """
    Generate a GDPR-compliant consent form.
    
    Args:
        app_name: Name of the application
        purposes: List of purposes for data collection
        
    Returns:
        A GDPR-compliant consent form text
    """
    purposes_text = "\n".join([f"- {purpose}" for purpose in purposes])
    
    return f"""
# Consent Form for {app_name}

By submitting your data, you consent to the collection and processing of your personal information for the following purposes:

{purposes_text}

You understand that:

- Your participation is voluntary
- You can withdraw your consent at any time
- Your data will be kept secure and confidential
- Your data will be deleted after it is no longer needed for the stated purposes
- You can request access to your data or request its deletion at any time

□ I consent to the collection and processing of my personal data for the purposes listed above.

□ I have read and understood the privacy policy.
    """