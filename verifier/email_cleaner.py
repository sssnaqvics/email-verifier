"""
Email cleaning and normalization.
Handles common data quality issues in CSV files.
"""

import re


def clean_email(email: str) -> str:
    """
    Clean and normalize email address.
    
    Handles:
    - Trailing/leading whitespace
    - Mixed case (converts to lowercase)
    - Quoted emails ("email@domain.com")
    - Common typos
    
    Returns:
        Cleaned email string (or empty if invalid)
    """
    if not email or not isinstance(email, str):
        return ""
    
    # Convert to string and strip
    email = str(email).strip()
    
    # Remove surrounding quotes
    email = email.strip('"').strip("'")
    
    # Lowercase
    email = email.lower()
    
    # Remove internal whitespace (rare but happens)
    email = re.sub(r'\s+', '', email)
    
    # Remove common URL prefixes if pasted
    email = email.replace('mailto:', '')
    
    return email


def is_obviously_invalid(email: str) -> tuple:
    """
    Quick check for obviously invalid emails before expensive checks.
    
    Returns:
        (is_invalid: bool, reason: str)
    """
    if not email:
        return True, "Empty email"
    
    if "@" not in email:
        return True, "No @ symbol"
    
    if email.count("@") > 1:
        return True, "Multiple @ symbols"
    
    parts = email.split("@")
    
    if len(parts) != 2:
        return True, "Invalid format"
    
    local, domain = parts
    
    if not local:
        return True, "Empty local part (before @)"
    
    if not domain:
        return True, "Empty domain (after @)"
    
    if "." not in domain:
        return True, "No TLD in domain"
    
    if domain.startswith(".") or domain.endswith("."):
        return True, "Invalid domain dots"
    
    if len(email) > 254:
        return True, "Email too long (>254 chars)"
    
    if len(local) > 64:
        return True, "Local part too long (>64 chars)"
    
    return False, ""


def deduplicate_emails(emails: list) -> tuple:
    """
    Remove duplicate emails from list.
    
    Returns:
        (unique_emails: list, duplicate_count: int, duplicate_indices: list)
    """
    seen = set()
    unique = []
    duplicates = []
    
    for i, email in enumerate(emails):
        cleaned = clean_email(email)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            unique.append(cleaned)
        else:
            duplicates.append(i)
    
    return unique, len(duplicates), duplicates