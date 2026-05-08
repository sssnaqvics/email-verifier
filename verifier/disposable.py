"""Disposable email detector."""

from pathlib import Path

_DISPOSABLE_DOMAINS = None


def load_disposable_domains() -> set:
    """Load disposable email domains list from file."""
    global _DISPOSABLE_DOMAINS
    
    if _DISPOSABLE_DOMAINS is not None:
        return _DISPOSABLE_DOMAINS
    
    base_dir = Path(__file__).parent.parent
    file_path = base_dir / "data" / "disposable_domains.txt"
    
    if not file_path.exists():
        print(f"Warning: {file_path} not found.")
        _DISPOSABLE_DOMAINS = set()
        return _DISPOSABLE_DOMAINS
    
    with open(file_path, "r", encoding="utf-8") as f:
        domains = {
            line.strip().lower() 
            for line in f 
            if line.strip() and not line.startswith("#")
        }
    
    _DISPOSABLE_DOMAINS = domains
    return domains


def check_disposable(email: str) -> dict:
    """Check if email is from a disposable email provider."""
    if not email or "@" not in email:
        return {"is_disposable": False, "reason": "Invalid", "domain": ""}
    
    domain = email.strip().lower().split("@")[-1]
    disposable_domains = load_disposable_domains()
    
    if domain in disposable_domains:
        return {
            "is_disposable": True,
            "reason": "Disposable provider",
            "domain": domain
        }
    
    return {"is_disposable": False, "reason": "Not disposable", "domain": domain}