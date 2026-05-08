"""MX record checker using DNS lookup."""

import dns.resolver
from typing import Dict


def check_mx(email: str) -> Dict:
    """
    Check if domain has valid MX records.
    
    Returns:
        dict with keys: has_mx (bool), mx_records (list), reason (str)
    """
    if not email or "@" not in email:
        return {
            "has_mx": False,
            "mx_records": [],
            "reason": "Invalid email format"
        }
    
    domain = email.strip().lower().split("@")[-1]
    
    try:
        # DNS MX lookup
        mx_records = dns.resolver.resolve(domain, 'MX')
        
        # Extract MX hostnames and priorities
        mx_list = [
            {"priority": record.preference, "hostname": str(record.exchange)}
            for record in mx_records
        ]
        
        # Sort by priority (lower number = higher priority)
        mx_list.sort(key=lambda x: x["priority"])
        
        return {
            "has_mx": True,
            "mx_records": mx_list,
            "reason": f"Found {len(mx_list)} MX record(s)"
        }
    
    except dns.resolver.NXDOMAIN:
        return {
            "has_mx": False,
            "mx_records": [],
            "reason": "Domain does not exist"
        }
    
    except dns.resolver.NoAnswer:
        return {
            "has_mx": False,
            "mx_records": [],
            "reason": "No MX records found"
        }
    
    except dns.resolver.Timeout:
        return {
            "has_mx": False,
            "mx_records": [],
            "reason": "DNS lookup timeout"
        }
    
    except Exception as e:
        return {
            "has_mx": False,
            "mx_records": [],
            "reason": f"DNS error: {str(e)}"
        }


# Quick test
if __name__ == "__main__":
    test_emails = [
        "test@gmail.com",
        "user@yahoo.com",
        "fake@nonexistent-domain-12345.com",
        "admin@google.com",
    ]
    
    print("MX Record Check Results:")
    print("-" * 70)
    for email in test_emails:
        result = check_mx(email)
        status = "✓" if result["has_mx"] else "✗"
        print(f"{status} {email:40} → {result['reason']}")
        if result["mx_records"]:
            for mx in result["mx_records"][:2]:  # Show first 2 only
                print(f"    Priority {mx['priority']}: {mx['hostname']}")