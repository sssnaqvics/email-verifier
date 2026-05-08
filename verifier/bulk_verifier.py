"""
Bulk email verifier with parallel/concurrent processing.
Processes multiple emails simultaneously for 3-5x speed improvement.
"""

import asyncio
from typing import List, Dict, Callable, Optional
from .syntax import check_syntax
from .disposable import check_disposable
from .role_based import check_role_based
from .mx_check import check_mx
from .smtp_check import smtp_verify_async, is_major_provider


# Concurrency settings
MAX_CONCURRENT = 15  # How many emails to process simultaneously
BATCH_SIZE = 50      # Process in batches of 50


async def verify_single_async(email: str) -> dict:
    """Async version of full email verification."""
    result = {
        "email": email,
        "status": "valid",
        "quality": "good",
        "result": "ok",
        "syntax_valid": False,
        "is_disposable": False,
        "is_role_based": False,
        "has_mx": False,
        "smtp_deliverable": None,
        "reason": "",
        "checks_passed": []
    }
    
    # Step 1: Syntax (fast, no network)
    syntax = check_syntax(email)
    result["syntax_valid"] = syntax["valid"]
    
    if not syntax["valid"]:
        result["status"] = "invalid"
        result["quality"] = "bad"
        result["result"] = "invalid"
        result["reason"] = f"Syntax: {syntax['reason']}"
        return result
    
    result["checks_passed"].append("Syntax ✓")
    
    # Step 2: Disposable (fast, no network)
    disposable = check_disposable(email)
    result["is_disposable"] = disposable["is_disposable"]
    
    if disposable["is_disposable"]:
        result["status"] = "invalid"
        result["quality"] = "bad"
        result["result"] = "disposable"
        result["reason"] = "Disposable email provider"
        return result
    
    result["checks_passed"].append("Not disposable ✓")
    
    # Step 3: Major provider check (skip MX/SMTP for Gmail/Yahoo etc)
    if is_major_provider(email):
        # Direct catch_all for major providers
        result["has_mx"] = True  # We know they exist
        result["status"] = "risky"
        result["quality"] = "risky"
        result["result"] = "catch_all"
        result["reason"] = "Major provider (Gmail/Yahoo/Outlook etc)"
        result["checks_passed"].append("Major provider detected")
        
        # Check role-based for major providers too
        role = check_role_based(email)
        result["is_role_based"] = role["is_role_based"]
        return result
    
    # Step 4: MX record check
    mx = check_mx(email)
    result["has_mx"] = mx["has_mx"]
    
    if not mx["has_mx"]:
        result["status"] = "invalid"
        result["quality"] = "bad"
        result["result"] = "invalid"
        result["reason"] = f"MX: {mx['reason']}"
        return result
    
    result["checks_passed"].append("MX exists ✓")
    
    # Step 5: SMTP verification (async)
    mx_host = mx["mx_records"][0]["hostname"].rstrip(".")
    smtp = await smtp_verify_async(email, mx_host)
    
    result["smtp_deliverable"] = smtp["deliverable"]
    result["smtp_reason"] = smtp.get("reason", "")
    
    if smtp["deliverable"] is False:
        result["status"] = "invalid"
        result["quality"] = "bad"
        result["result"] = "invalid"
        result["reason"] = f"SMTP: {smtp['reason']}"
        return result
    elif smtp["deliverable"] is None:
        result["status"] = "risky"
        result["quality"] = "risky"
        result["result"] = "unknown"
        result["reason"] = f"Uncertain: {smtp['reason']}"
        result["checks_passed"].append(f"SMTP: {smtp['reason']}")
    else:
        result["checks_passed"].append("SMTP verified ✓")
    
    # Step 6: Role-based check
    role = check_role_based(email)
    result["is_role_based"] = role["is_role_based"]
    
    if role["is_role_based"]:
        if result["status"] == "valid":
            result["status"] = "risky"
            result["quality"] = "risky"
            result["reason"] = "Role-based email"
        return result
    
    if result["status"] == "valid":
        result["reason"] = "All verifications passed"
    return result


async def verify_batch_async(emails: List[str], max_concurrent: int = MAX_CONCURRENT) -> List[dict]:
    """
    Verify multiple emails concurrently.
    
    Args:
        emails: List of email addresses
        max_concurrent: Maximum simultaneous verifications
    
    Returns:
        List of verification results in same order as input
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def verify_with_semaphore(email):
        async with semaphore:
            try:
                return await verify_single_async(str(email))
            except Exception as e:
                return {
                    "email": str(email),
                    "status": "invalid",
                    "quality": "bad",
                    "result": "invalid",
                    "reason": f"Error: {str(e)[:100]}",
                    "syntax_valid": False,
                    "is_disposable": False,
                    "is_role_based": False,
                    "has_mx": False,
                    "smtp_deliverable": None,
                    "checks_passed": []
                }
    
    tasks = [verify_with_semaphore(email) for email in emails]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    return results


def verify_bulk(
    emails: List[str], 
    progress_callback: Optional[Callable] = None,
    batch_size: int = BATCH_SIZE,
    max_concurrent: int = MAX_CONCURRENT
) -> List[dict]:
    """
    Synchronous wrapper for bulk verification with progress tracking.
    
    Args:
        emails: List of emails to verify
        progress_callback: Function called with (completed, total) after each batch
        batch_size: Process in batches of this size
        max_concurrent: Concurrent verifications per batch
    
    Returns:
        List of verification results
    """
    all_results = []
    total = len(emails)
    
    # Create event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Process in batches
        for i in range(0, total, batch_size):
            batch = emails[i:i + batch_size]
            
            # Run async verification for this batch
            batch_results = loop.run_until_complete(
                verify_batch_async(batch, max_concurrent)
            )
            
            all_results.extend(batch_results)
            
            # Update progress
            if progress_callback:
                progress_callback(len(all_results), total)
    
    finally:
        loop.close()
    
    return all_results