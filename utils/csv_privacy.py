"""
Utilities for handling privacy and data protection in CSV files.

This module provides functions to:
1. Anonymize PII in CSV files
2. Create pseudonymized versions of CSV files
3. Apply GDPR-compliant data processing to CSV files
"""
import os
import csv
import pandas as pd
from typing import List, Dict, Any, Optional, Set
from utils.privacy import mask_pii, generate_pseudonym

# Fields that typically contain PII in a CSV file
PII_FIELDS = {
    'Email', 'email', 'Email Address', 'email_address',
    'First Name', 'first_name', 'FirstName', 'firstname',
    'Last Name', 'last_name', 'LastName', 'lastname',
    'Full Name', 'full_name', 'FullName', 'fullname',
    'Phone', 'phone', 'Phone Number', 'phone_number',
    'Address', 'address', 'Street', 'street',
    'City', 'city', 'State', 'state',
    'Zip', 'zip', 'Postal Code', 'postal_code',
    'SSN', 'ssn', 'Social Security', 'social_security',
    'DOB', 'dob', 'Date of Birth', 'date_of_birth',
    'IP Address', 'ip_address', 'IP', 'ip',
}

# Fields required for the raffle application
REQUIRED_FIELDS = {
    'Email': ['email', 'Email', 'email_address', 'Email Address'],
    'First Name': ['first_name', 'First Name', 'firstname', 'FirstName'],
    'Last Name': ['last_name', 'Last Name', 'lastname', 'LastName'],
    'Checkin Date (UTC)': ['checked_in_at', 'Checkin Date (UTC)', 'checkin_date', 'CheckinDate']
}

def identify_pii_fields(columns: List[str]) -> List[str]:
    """
    Identify which columns in a CSV file likely contain PII.
    
    Args:
        columns: List of column names from the CSV file
        
    Returns:
        List of column names that likely contain PII
    """
    return [col for col in columns if col in PII_FIELDS]

def anonymize_csv(input_path: str, output_path: str) -> Dict[str, Any]:
    """
    Create an anonymized version of a CSV file with PII masked.
    
    Args:
        input_path: Path to the input CSV file
        output_path: Path to write the anonymized CSV file
        
    Returns:
        Dictionary with statistics about the anonymization
    """
    # Read the CSV file
    df = pd.read_csv(input_path)
    
    # Track statistics for the report
    stats = {
        'total_rows': len(df),
        'columns_anonymized': [],
        'pii_items_masked': 0
    }
    
    # Identify PII columns
    pii_columns = identify_pii_fields(df.columns)
    stats['pii_fields_identified'] = len(pii_columns)
    
    # Anonymize each PII column
    for column in pii_columns:
        if column in df.columns:
            # Count non-null values before masking
            non_null_count = df[column].count()
            
            # Apply masking to non-null values
            df[column] = df[column].apply(lambda x: mask_pii(str(x)) if pd.notnull(x) else x)
            
            # Update stats
            stats['columns_anonymized'].append(column)
            stats['pii_items_masked'] += non_null_count
    
    # Write the anonymized data to the output file
    df.to_csv(output_path, index=False)
    
    return stats

def pseudonymize_csv(input_path: str, output_path: str, salt: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a pseudonymized version of a CSV file where PII is replaced with consistent pseudonyms.
    
    This preserves the ability to link related records while obscuring actual PII.
    
    Args:
        input_path: Path to the input CSV file
        output_path: Path to write the pseudonymized CSV file
        salt: Salt to use for pseudonym generation (for consistent pseudonyms across runs)
        
    Returns:
        Dictionary with statistics about the pseudonymization
    """
    # Read the CSV file
    df = pd.read_csv(input_path)
    
    # Track statistics for the report
    stats = {
        'total_rows': len(df),
        'columns_pseudonymized': [],
        'pii_items_replaced': 0
    }
    
    # Use a default salt if none provided
    if not salt:
        salt = "raffle-app-pseudonymization"
    
    # Identify PII columns
    pii_columns = identify_pii_fields(df.columns)
    stats['pii_fields_identified'] = len(pii_columns)
    
    # Pseudonymize each PII column
    for column in pii_columns:
        if column in df.columns:
            # Count non-null values before pseudonymizing
            non_null_count = df[column].count()
            
            # Apply pseudonymization to non-null values
            column_salt = f"{salt}-{column}"  # Make salt specific to this column
            df[column] = df[column].apply(
                lambda x: generate_pseudonym(str(x), column_salt) if pd.notnull(x) else x
            )
            
            # Update stats
            stats['columns_pseudonymized'].append(column)
            stats['pii_items_replaced'] += non_null_count
    
    # Write the pseudonymized data to the output file
    df.to_csv(output_path, index=False)
    
    return stats

def create_gdpr_compliant_csv(input_path: str, output_path: str) -> Dict[str, Any]:
    """
    Create a GDPR-compliant version of a CSV file, keeping only necessary fields
    and applying minimization principles.
    
    Args:
        input_path: Path to the input CSV file
        output_path: Path to write the GDPR-compliant CSV file
        
    Returns:
        Dictionary with statistics about the compliance processing
    """
    # Read the CSV file
    df = pd.read_csv(input_path)
    
    # Track statistics for the report
    stats = {
        'total_rows': len(df),
        'original_columns': len(df.columns),
        'retained_columns': 0,
        'removed_columns': 0,
        'pii_items_minimized': 0
    }
    
    # Identify and keep only required fields
    retained_columns = []
    column_mapping = {}
    
    # Map columns to standardized names
    for std_name, variants in REQUIRED_FIELDS.items():
        found = False
        for variant in variants:
            if variant in df.columns:
                column_mapping[variant] = std_name
                retained_columns.append(variant)
                found = True
                break
    
    # Keep any non-PII columns that might be useful
    for column in df.columns:
        if column not in retained_columns and column not in PII_FIELDS:
            retained_columns.append(column)
    
    # Create a new DataFrame with only the required columns
    df_minimal = df[retained_columns].copy()
    
    # Rename columns to standardized names
    df_minimal = df_minimal.rename(columns=column_mapping)
    
    # Anonymize all PII columns
    for column in df_minimal.columns:
        if column in PII_FIELDS or column in REQUIRED_FIELDS.keys():
            non_null_count = df_minimal[column].count()
            df_minimal[column] = df_minimal[column].apply(
                lambda x: mask_pii(str(x)) if pd.notnull(x) else x
            )
            stats['pii_items_minimized'] += non_null_count
    
    # Update stats
    stats['retained_columns'] = len(df_minimal.columns)
    stats['removed_columns'] = len(df.columns) - len(df_minimal.columns)
    
    # Write the GDPR-compliant data to the output file
    df_minimal.to_csv(output_path, index=False)
    
    return stats

def apply_data_retention_policy(directory: str, max_age_days: int = 30) -> Dict[str, Any]:
    """
    Apply data retention policy by removing CSV files older than max_age_days.
    
    Args:
        directory: Directory to scan for CSV files
        max_age_days: Maximum age of files in days
        
    Returns:
        Dictionary with statistics about the files processed
    """
    import time
    from datetime import datetime, timedelta
    
    stats = {
        'files_scanned': 0,
        'files_deleted': 0,
        'bytes_reclaimed': 0
    }
    
    # Calculate cutoff time
    cutoff_time = time.time() - (max_age_days * 86400)  # 86400 seconds per day
    
    # Scan directory for CSV files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.csv'):
                stats['files_scanned'] += 1
                file_path = os.path.join(root, file)
                
                # Check file modification time
                if os.path.getmtime(file_path) < cutoff_time:
                    file_size = os.path.getsize(file_path)
                    try:
                        os.remove(file_path)
                        stats['files_deleted'] += 1
                        stats['bytes_reclaimed'] += file_size
                    except Exception as e:
                        print(f"Error deleting {file_path}: {str(e)}")
    
    return stats

def check_gdpr_compliance(input_path: str) -> Dict[str, Any]:
    """
    Check if a CSV file complies with GDPR principles.
    
    Args:
        input_path: Path to the CSV file to check
        
    Returns:
        Dictionary with compliance status and issues
    """
    # Read the CSV file
    df = pd.read_csv(input_path)
    
    report = {
        'compliant': True,
        'issues': [],
        'recommendations': []
    }
    
    # Check for unnecessary PII
    pii_columns = identify_pii_fields(df.columns)
    necessary_pii = set()
    for variants in REQUIRED_FIELDS.values():
        necessary_pii.update(variants)
    
    unnecessary_pii = [col for col in pii_columns if col not in necessary_pii]
    if unnecessary_pii:
        report['compliant'] = False
        report['issues'].append(f"Unnecessary PII columns found: {', '.join(unnecessary_pii)}")
        report['recommendations'].append("Remove unnecessary PII columns or pseudonymize them")
    
    # Check for data minimization
    if len(df.columns) > len(REQUIRED_FIELDS) + 3:  # Allow a few extra utility columns
        report['recommendations'].append("Consider applying data minimization by removing non-essential columns")
    
    # Check for email patterns that might indicate personal emails vs. business emails
    if 'Email' in df.columns:
        personal_email_count = 0
        business_email_count = 0
        common_personal_domains = {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com'}
        
        for email in df['Email'].dropna():
            if '@' in email:
                domain = email.split('@')[1].lower()
                if domain in common_personal_domains:
                    personal_email_count += 1
                else:
                    business_email_count += 1
        
        if personal_email_count > 0:
            report['recommendations'].append(
                f"File contains {personal_email_count} personal email addresses. "
                f"Consider if this is necessary for your purposes."
            )
    
    return report

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CSV Privacy and GDPR Compliance Tools")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Anonymize command
    anon_parser = subparsers.add_parser("anonymize", help="Anonymize PII in a CSV file")
    anon_parser.add_argument("input", help="Input CSV file path")
    anon_parser.add_argument("output", help="Output CSV file path")
    
    # Pseudonymize command
    pseudo_parser = subparsers.add_parser("pseudonymize", help="Pseudonymize PII in a CSV file")
    pseudo_parser.add_argument("input", help="Input CSV file path")
    pseudo_parser.add_argument("output", help="Output CSV file path")
    pseudo_parser.add_argument("--salt", help="Salt for pseudonymization")
    
    # GDPR compliance command
    gdpr_parser = subparsers.add_parser("gdpr", help="Create GDPR-compliant CSV")
    gdpr_parser.add_argument("input", help="Input CSV file path")
    gdpr_parser.add_argument("output", help="Output CSV file path")
    
    # Check compliance command
    check_parser = subparsers.add_parser("check", help="Check GDPR compliance")
    check_parser.add_argument("input", help="Input CSV file path")
    
    # Retention policy command
    retention_parser = subparsers.add_parser("retention", help="Apply data retention policy")
    retention_parser.add_argument("directory", help="Directory to scan")
    retention_parser.add_argument("--days", type=int, default=30, help="Maximum age in days")
    
    args = parser.parse_args()
    
    if args.command == "anonymize":
        stats = anonymize_csv(args.input, args.output)
        print(f"Anonymization complete: {stats['pii_items_masked']} PII items masked in {len(stats['columns_anonymized'])} columns")
        
    elif args.command == "pseudonymize":
        stats = pseudonymize_csv(args.input, args.output, args.salt)
        print(f"Pseudonymization complete: {stats['pii_items_replaced']} PII items replaced in {len(stats['columns_pseudonymized'])} columns")
        
    elif args.command == "gdpr":
        stats = create_gdpr_compliant_csv(args.input, args.output)
        print(f"GDPR compliance processing complete: {stats['retained_columns']} columns retained, {stats['removed_columns']} columns removed")
        
    elif args.command == "check":
        report = check_gdpr_compliance(args.input)
        if report['compliant']:
            print("File appears to be GDPR compliant")
        else:
            print("File has GDPR compliance issues:")
            for issue in report['issues']:
                print(f" - {issue}")
        
        if report['recommendations']:
            print("\nRecommendations:")
            for rec in report['recommendations']:
                print(f" - {rec}")
    
    elif args.command == "retention":
        stats = apply_data_retention_policy(args.directory, args.days)
        print(f"Retention policy applied: {stats['files_deleted']} of {stats['files_scanned']} files deleted, {stats['bytes_reclaimed'] / 1024:.2f} KB reclaimed")
    
    else:
        parser.print_help()