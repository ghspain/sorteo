"""
Utility functions for privacy protection and compliance with data protection regulations.

This module provides functions to:
1. Mask personally identifiable information (PII) in outputs and logs
2. Generate pseudonyms for personal data
3. Support GDPR and other data protection regulations
"""
import re
import hashlib
import logging
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

# PII patterns to identify sensitive information
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN = re.compile(r'\b(?:\+?[0-9]{1,3}[- ]?)?(?:\([0-9]{1,4}\)|[0-9]{1,4})[-. ]?[0-9]{1,4}[-. ]?[0-9]{1,9}\b')
NAME_PATTERN = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b')

def mask_pii(text: str, mask_char: str = '*') -> str:
    """
    Mask personally identifiable information in text.
    
    Args:
        text: Text that might contain PII
        mask_char: Character to use for masking
    
    Returns:
        Text with PII masked
    """
    if not text:
        return text
        
    # Special handling for full email addresses
    if '@' in text and len(text.split('@')) == 2 and not ' ' in text:
        # Direct email handling
        username, domain = text.split('@')
        if len(username) > 1:
            # Keep first and last letter, mask everything in between
            masked = username[0] + mask_char * (len(username) - 2) + username[-1]
            return masked + '@' + domain
        elif len(username) == 1:
            # If username is just one character, keep it
            return username + '@' + domain
        else:
            # Handle empty username
            return mask_char + '@' + domain
    
    # Mask email addresses - keep first and last letter of username, keep domain
    def mask_email(match):
        email = match.group(0)
        parts = email.split('@')
        if len(parts) == 2:
            username = parts[0]
            domain = parts[1]
            
            if len(username) > 1:
                # Keep first and last letter, mask everything in between
                masked = username[0] + mask_char * (len(username) - 2) + username[-1]
            elif len(username) == 1:
                # If username is just one character, keep it
                masked = username
            else:
                # Handle empty username
                masked = mask_char
                
            return masked + '@' + domain
            
        return mask_char * len(email)
    
    # Mask phone numbers - keep last 4 digits
    def mask_phone(match):
        phone = match.group(0)
        if len(phone) > 4:
            return mask_char * (len(phone) - 4) + phone[-4:]
        return mask_char * len(phone)
    
    # Mask names - keep initials
    def mask_name(match):
        name = match.group(0)
        parts = name.split()
        masked_parts = [part[0] + mask_char * (len(part) - 1) for part in parts]
        return ' '.join(masked_parts)
    
    # Apply all masking patterns
    text = EMAIL_PATTERN.sub(mask_email, text)
    text = PHONE_PATTERN.sub(mask_phone, text)
    text = NAME_PATTERN.sub(mask_name, text)
    
    return text

def generate_pseudonym(text: str, salt: str = "raffle-app") -> str:
    """
    Generate a consistent pseudonym for a piece of PII.
    
    Args:
        text: The PII to generate a pseudonym for
        salt: A salt to make the hash more secure
        
    Returns:
        A consistent pseudonym for the PII
    """
    if not text:
        return ""
    
    # Create a hash of the text with the salt
    hash_obj = hashlib.sha256((text + salt).encode())
    hash_hex = hash_obj.hexdigest()
    
    # Use the first 8 characters of the hash as the pseudonym
    return hash_hex[:8]

# Helper functions for regulatory compliance

def is_personal_data(data_type: str) -> bool:
    """
    Check if a data type is considered personal data under data protection regulations.
    
    Args:
        data_type: The type of data to check
        
    Returns:
        True if the data type is personal data, False otherwise
    """
    personal_data_types = {
        'email', 'name', 'fullname', 'firstname', 'lastname', 'full_name', 'first_name', 'last_name',
        'address', 'phone', 'phone_number', 'phonenumber', 'mobile', 'mobile_number', 'mobilenumber',
        'date_of_birth', 'dateofbirth', 'dob', 'birth_date', 'birthdate', 'gender',
        'ip_address', 'ipaddress', 'id', 'user_id', 'userid', 'account_id', 'accountid',
        'ssn', 'social_security', 'socialsecurity', 'passport', 'id_number', 'idnumber',
        'location', 'geo', 'gps', 'coordinates',
        'credit_card', 'creditcard', 'bank_account', 'bankaccount', 'iban'
    }
    
    return data_type.lower().replace('_', '') in personal_data_types

def is_special_category_data(data_type: str) -> bool:
    """
    Check if a data type is considered 'special category' under GDPR.
    
    Special category data requires extra protection under GDPR.
    
    Args:
        data_type: The type of data to check
        
    Returns:
        True if the data type is special category, False otherwise
    """
    special_categories = {
        'race', 'ethnicity', 'political_opinions', 'politicalopinions', 'political',
        'religion', 'religious', 'beliefs', 'philosophical',
        'trade_union', 'tradeunion', 'union_membership', 'unionmembership', 'genetic', 'biometric',
        'health', 'medical', 'sex_life', 'sexlife', 'sexual_orientation', 'sexualorientation',
        'sexual', 'criminal', 'offence', 'conviction'
    }
    
    return data_type.lower().replace('_', '') in special_categories

def is_child_data(age: int) -> bool:
    """
    Check if data belongs to a child under GDPR.
    
    In GDPR, special protections apply to children's data.
    The default age for children under GDPR is under 16,
    but member states can lower this to 13.
    
    Args:
        age: The age to check
        
    Returns:
        True if the age is considered a child under GDPR, False otherwise
    """
    # Using the GDPR default of 16
    return age < 16