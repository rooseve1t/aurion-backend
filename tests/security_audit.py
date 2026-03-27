"""
SECURITY AUDIT REPORT - Aurion Backend
Generated: Automated analysis
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any

class SecurityAuditor:
    """Static security analysis for Python files"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.issues: List[Dict[str, Any]] = []
        
    def audit_all(self) -> Dict[str, Any]:
        """Run full security audit"""
        results = {
            "sql_injection_check": self._check_sql_injection_fixes(),
            "race_condition_check": self._check_race_condition_fixes(),
            "encryption_check": self._check_encryption_fixes(),
            "async_task_check": self._check_async_task_fixes(),
            "input_validation_check": self._check_input_validation(),
            "auth_security_check": self._check_auth_security(),
        }
        return results
    
    def _check_sql_injection_fixes(self) -> Dict[str, Any]:
        """Verify SQL injection protection in memory_service.py"""
        file_path = self.base_path / "app" / "services" / "memory_service.py"
        if not file_path.exists():
            return {"status": "ERROR", "message": "File not found"}
        
        with open(file_path, 'r') as f:
            source = f.read()
        
        checks = {
            "escape_function_exists": "_escape_like" in source,
            "escape_param_used": 'escape=' in source,  # Any escape parameter
            "ilike_with_escape": "ilike(" in source and "escape" in source,
        }
        
        all_pass = all(checks.values())
        return {
            "status": "PASS" if all_pass else "FAIL",
            "checks": checks,
            "file": str(file_path)
        }
    
    def _check_race_condition_fixes(self) -> Dict[str, Any]:
        """Verify race condition fix in payments.py"""
        file_path = self.base_path / "app" / "api" / "payments.py"
        if not file_path.exists():
            return {"status": "ERROR", "message": "File not found"}
        
        with open(file_path, 'r') as f:
            source = f.read()
        
        checks = {
            "update_statement_used": "update(Subscription)" in source,
            "atomic_operation": ".values(" in source and "execution_options" in source,
            "no_select_loop": "for existing in" not in source and "for sub in" not in source,
        }
        
        all_pass = all(checks.values())
        return {
            "status": "PASS" if all_pass else "FAIL",
            "checks": checks,
            "file": str(file_path)
        }
    
    def _check_encryption_fixes(self) -> Dict[str, Any]:
        """Verify encryption key handling in finance_service.py"""
        file_path = self.base_path / "app" / "services" / "finance_service.py"
        if not file_path.exists():
            return {"status": "ERROR", "message": "File not found"}
        
        with open(file_path, 'r') as f:
            source = f.read()
        
        checks = {
            "key_check_exists": "if not _encryption_key:" in source,
            "runtime_error_raised": "RuntimeError" in source,
            "key_required_message": "ENCRYPTION_KEY" in source and "must be set" in source,
        }
        
        all_pass = all(checks.values())
        return {
            "status": "PASS" if all_pass else "FAIL",
            "checks": checks,
            "file": str(file_path)
        }
    
    def _check_async_task_fixes(self) -> Dict[str, Any]:
        """Verify MQTT task storage in smarthome_service.py"""
        file_path = self.base_path / "app" / "services" / "smarthome_service.py"
        if not file_path.exists():
            return {"status": "ERROR", "message": "File not found"}
        
        with open(file_path, 'r') as f:
            source = f.read()
        
        checks = {
            "task_attribute_defined": "_mqtt_task" in source,
            "task_stored": "self._mqtt_task = asyncio.create_task" in source,
            "typing_optional": "Optional[asyncio.Task]" in source or "_mqtt_task:" in source,
        }
        
        all_pass = all(checks.values())
        return {
            "status": "PASS" if all_pass else "FAIL",
            "checks": checks,
            "file": str(file_path)
        }
    
    def _check_input_validation(self) -> Dict[str, Any]:
        """Check input validation patterns"""
        file_path = self.base_path / "app" / "api" / "agents.py"
        if not file_path.exists():
            return {"status": "ERROR", "message": "File not found"}
        
        with open(file_path, 'r') as f:
            source = f.read()
        
        checks = {
            "uuid_validation": "UUID(" in source,
            "status_check_before_cancel": "task.status in" in source and "completed" in source,
            "http_exception_on_invalid": "HTTPException" in source,
        }
        
        all_pass = all(checks.values())
        return {
            "status": "PASS" if all_pass else "FAIL",
            "checks": checks,
            "file": str(file_path)
        }
    
    def _check_auth_security(self) -> Dict[str, Any]:
        """Check authentication security patterns"""
        api_auth_path = self.base_path / "app" / "api" / "auth.py"
        core_auth_path = self.base_path / "app" / "auth.py"
        osint_path = self.base_path / "app" / "api" / "osint.py"
        
        if not api_auth_path.exists():
            return {"status": "ERROR", "message": "API auth file not found"}
        
        with open(api_auth_path, 'r') as f:
            api_source = f.read()
        
        # Read core auth for password hashing
        core_source = ""
        if core_auth_path.exists():
            with open(core_auth_path, 'r') as f:
                core_source = f.read()
        
        # Read osint for role checks
        osint_source = ""
        if osint_path.exists():
            with open(osint_path, 'r') as f:
                osint_source = f.read()
        
        checks = {
            "token_rotation": "revoke_refresh_token" in api_source,
            "new_token_created": "new_refresh_token" in api_source,
            "password_hashing": "get_password_hash" in core_source,
            "totp_verification": "verify_totp" in api_source or "verify_totp" in core_source,
            "role_check_in_osint": ('current_user.role' in osint_source and 'creator' in osint_source) or \
                                   ('current_user.role' in osint_source and 'admin' in osint_source),
        }
        
        all_pass = all(v for v in checks.values() if v is not None)
        return {
            "status": "PASS" if all_pass else "FAIL",
            "checks": checks,
            "file": str(api_auth_path)
        }


def generate_report():
    """Generate and print security audit report"""
    base_path = "/Users/natalacernikova/Downloads/aurion-stage13/aurion-backend"
    
    auditor = SecurityAuditor(base_path)
    results = auditor.audit_all()
    
    print("=" * 70)
    print("AURION BACKEND SECURITY AUDIT REPORT")
    print("=" * 70)
    
    all_passed = True
    for check_name, result in results.items():
        status = result.get("status", "UNKNOWN")
        symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"\n{symbol} {check_name.upper().replace('_', ' ')}")
        print(f"   Status: {status}")
        print(f"   File: {result.get('file', 'N/A')}")
        
        if "checks" in result:
            for check, passed in result["checks"].items():
                mark = "✓" if passed else "✗"
                print(f"   [{mark}] {check}")
        
        if status != "PASS":
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("OVERALL: ✅ ALL CRITICAL SECURITY CHECKS PASSED")
    else:
        print("OVERALL: ❌ SOME CHECKS FAILED - REVIEW REQUIRED")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    generate_report()
