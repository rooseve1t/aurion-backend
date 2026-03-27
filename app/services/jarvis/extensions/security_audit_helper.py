"""
Generated Extension: security_audit_helper
Purpose: Scans session logs for suspicious patterns.
"""
import logging

logger = logging.getLogger("jarvis-extension-security")

async def run(*args, **kwargs):
    logger.info("🛡️ Running Security Audit Helper extension...")
    
    session_logs = kwargs.get("logs", [])
    threats_detected = 0
    
    for log in session_logs:
        if "unauthorized" in log.lower() or "failed login" in log.lower():
            threats_detected += 1
            
    return {
        "status": "completed",
        "threats_found": threats_detected,
        "recommendation": "Enable 2FA for all mesh nodes." if threats_detected > 0 else "All systems secure."
    }
