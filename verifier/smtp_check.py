"""
SMTP verification with smart provider detection.
Skips major providers (Gmail, Outlook, Yahoo) that don't verify.
"""

import asyncio
import aiosmtplib
from typing import Dict
import socket


TEST_SENDER = "verify@example.com"
SMTP_TIMEOUT = 10

# Major providers - SMTP verification doesn't work, skip directly
MAJOR_PROVIDERS = {
    # Google
    "gmail.com", "googlemail.com",
    # Microsoft
    "outlook.com", "hotmail.com", "live.com", "msn.com",
    "outlook.co.uk", "hotmail.co.uk", "live.co.uk",
    # Yahoo
    "yahoo.com", "ymail.com", "yahoo.co.uk", "yahoo.in",
    "yahoo.co.in", "rocketmail.com",
    # Apple
    "icloud.com", "me.com", "mac.com",
    # Other major
    "aol.com", "zoho.com", "protonmail.com", "proton.me",
    "pm.me", "tutanota.com", "fastmail.com",
}


def is_major_provider(email: str) -> bool:
    """Check if email belongs to a major provider that blocks SMTP verification."""
    if "@" not in email:
        return False
    domain = email.strip().lower().split("@")[-1]
    return domain in MAJOR_PROVIDERS


async def smtp_verify_async(email: str, mx_host: str) -> Dict:
    """Async SMTP verification - core function."""
    
    # Quick check for major providers - skip SMTP
    if is_major_provider(email):
        return {
            "deliverable": None,
            "reason": "Major provider (catch-all by policy)",
            "code": 0,
            "smtp_response": "Skipped",
            "skipped": True
        }
    
    try:
        client = aiosmtplib.SMTP(
            hostname=mx_host,
            port=25,
            timeout=SMTP_TIMEOUT
        )
        
        await asyncio.wait_for(client.connect(), timeout=SMTP_TIMEOUT)
        await client.ehlo()
        await client.mail(TEST_SENDER)
        code, message = await client.rcpt(email)
        await client.quit()
        
        # Analyze response
        if code == 250:
            return {
                "deliverable": True,
                "reason": "Address accepted",
                "code": code,
                "smtp_response": str(message)[:100],
                "skipped": False
            }
        elif code in [550, 551, 553]:
            return {
                "deliverable": False,
                "reason": "Address rejected (user not found)",
                "code": code,
                "smtp_response": str(message)[:100],
                "skipped": False
            }
        elif code in [450, 451, 452]:
            return {
                "deliverable": None,
                "reason": "Greylisting (temporary)",
                "code": code,
                "smtp_response": str(message)[:100],
                "skipped": False
            }
        else:
            return {
                "deliverable": None,
                "reason": f"Uncertain (code {code})",
                "code": code,
                "smtp_response": str(message)[:100],
                "skipped": False
            }
    
    except aiosmtplib.SMTPException as e:
        error_msg = str(e).lower()
        if "550" in error_msg or "user unknown" in error_msg:
            return {
                "deliverable": False,
                "reason": "Address rejected by server",
                "code": 550,
                "smtp_response": str(e)[:100],
                "skipped": False
            }
        elif "421" in error_msg or "too many" in error_msg:
            return {
                "deliverable": None,
                "reason": "Rate limited",
                "code": 421,
                "smtp_response": str(e)[:100],
                "skipped": False
            }
        else:
            return {
                "deliverable": None,
                "reason": f"SMTP error",
                "code": 0,
                "smtp_response": str(e)[:100],
                "skipped": False
            }
    
    except asyncio.TimeoutError:
        return {
            "deliverable": None,
            "reason": "Timeout",
            "code": 0,
            "smtp_response": "Timeout",
            "skipped": False
        }
    
    except socket.gaierror:
        return {
            "deliverable": False,
            "reason": "Cannot resolve MX",
            "code": 0,
            "smtp_response": "DNS error",
            "skipped": False
        }
    
    except Exception as e:
        return {
            "deliverable": None,
            "reason": "Connection error",
            "code": 0,
            "smtp_response": str(e)[:100],
            "skipped": False
        }


def check_smtp(email: str, mx_records: list) -> Dict:
    """
    Synchronous wrapper for single SMTP verification.
    Used by single email tab.
    """
    if not mx_records:
        return {
            "deliverable": False,
            "reason": "No MX records",
            "code": 0,
            "smtp_response": "N/A",
            "skipped": False
        }
    
    mx_host = mx_records[0]["hostname"].rstrip(".")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(smtp_verify_async(email, mx_host))
        loop.close()
        return result
    except Exception as e:
        return {
            "deliverable": None,
            "reason": "SMTP check failed",
            "code": 0,
            "smtp_response": str(e)[:100],
            "skipped": False
        }