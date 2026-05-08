"""Role-based email detector."""

ROLE_BASED_PREFIXES = {
    "info", "support", "admin", "administrator", "sales", "contact",
    "hello", "help", "service", "office", "inquiry", "inquiries",
    "marketing", "noreply", "no-reply", "donotreply", "do-not-reply",
    "team", "staff", "billing", "accounts", "accounting", "hr",
    "careers", "jobs", "feedback", "general", "mail", "email",
    "webmaster", "postmaster", "abuse", "security", "legal",
    "press", "media", "news", "ceo", "cto", "cfo", "founder",
}


def check_role_based(email: str) -> dict:
    """Check if email is role-based (not a personal email)."""
    if not email or "@" not in email:
        return {"is_role_based": False, "reason": "Invalid", "local_part": ""}
    
    local_part = email.strip().lower().split("@")[0]
    
    if local_part in ROLE_BASED_PREFIXES:
        return {
            "is_role_based": True,
            "reason": f"Role-based: {local_part}",
            "local_part": local_part
        }
    
    for prefix in ROLE_BASED_PREFIXES:
        if local_part.startswith(prefix + ".") or \
           local_part.startswith(prefix + "-") or \
           local_part.startswith(prefix + "_"):
            return {
                "is_role_based": True,
                "reason": f"Role-based: {prefix}",
                "local_part": local_part
            }
    
    return {"is_role_based": False, "reason": "Personal", "local_part": local_part}