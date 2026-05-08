"""Email Verifier package."""
from .syntax import check_syntax
from .disposable import check_disposable
from .role_based import check_role_based
from .mx_check import check_mx
from .smtp_check import check_smtp
from .bulk_verifier import verify_bulk, verify_single_async
from .email_cleaner import clean_email, is_obviously_invalid, deduplicate_emails

__all__ = [
    "check_syntax", 
    "check_disposable", 
    "check_role_based", 
    "check_mx",
    "check_smtp",
    "verify_bulk",
    "verify_single_async",
    "clean_email",
    "is_obviously_invalid",
    "deduplicate_emails"
]