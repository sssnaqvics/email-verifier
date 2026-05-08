"""Syntax checker for emails - RFC 5322 compliant."""

import re
from email_validator import validate_email, EmailNotValidError

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)


def check_syntax(email: str) -> dict:
    """Check if email has valid syntax."""
    if not email or not isinstance(email, str):
        return {"valid": False, "reason": "Empty input", "normalized": ""}
    
    email = email.strip().lower()
    
    if not EMAIL_REGEX.match(email):
        return {"valid": False, "reason": "Invalid format", "normalized": email}
    
    try:
        validated = validate_email(email, check_deliverability=False)
        return {
            "valid": True,
            "reason": "Valid syntax",
            "normalized": validated.normalized
        }
    except EmailNotValidError as e:
        return {"valid": False, "reason": str(e), "normalized": email}