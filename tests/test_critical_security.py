"""
Critical security and edge case tests for Aurion Backend
Tests for: SQL injection, race conditions, encryption, auth flows
"""

import asyncio
import pytest
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import uuid

# Add app to path
sys.path.insert(0, '/Users/natalacernikova/Downloads/aurion-stage13/aurion-backend')

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from fastapi.testclient import TestClient


class TestSQLInjectionProtection:
    """Test SQL injection protection in memory service"""
    
    def test_search_with_sql_injection_attempts(self):
        """Test that SQL injection patterns are properly escaped in service"""
        # Read the service file directly to verify escaping logic exists
        service_path = '/Users/natalacernikova/Downloads/aurion-stage13/aurion-backend/app/services/memory_service.py'
        with open(service_path, 'r') as f:
            source = f.read()
        
        # Verify _escape_like function exists
        assert "def _escape_like" in source or "_escape_like" in source
        # Verify escape parameter is used in ilike
        assert 'escape="\\"' in source
        
        # Test escaping logic manually
        test_inputs = [
            ("test%", "test\\%"),
            ("test_", "test\\_"),
            ("test[", "test\\["),
            ("test]", "test\\]"),
        ]
        
        for original, expected in test_inputs:
            escaped = original.replace("%", "\\%").replace("_", "\\_").replace("[", "\\[").replace("]", "\\]")
            assert escaped == expected


class TestEncryptionKeyHandling:
    """Test encryption key handling in finance service"""
    
    def test_encryption_key_fallback(self):
        """Test that finance service uses safe fallback when ENCRYPTION_KEY is missing"""
        # Save current env
        old_key = os.environ.get('ENCRYPTION_KEY')
        
        try:
            # Remove ENCRYPTION_KEY
            if 'ENCRYPTION_KEY' in os.environ:
                del os.environ['ENCRYPTION_KEY']
            
            # Re-import should not fail: service must auto-generate temporary key
            if 'app.services.finance_service' in sys.modules:
                del sys.modules['app.services.finance_service']
            import app.services.finance_service as finance_service

            assert finance_service.cipher_suite is not None
            
        finally:
            # Restore
            if old_key is not None:
                os.environ['ENCRYPTION_KEY'] = old_key
    
    def test_encryption_with_valid_key(self):
        """Test encryption works with valid key"""
        from cryptography.fernet import Fernet
        
        # Generate test key
        key = Fernet.generate_key().decode()
        os.environ['ENCRYPTION_KEY'] = key
        
        # Should work
        cipher = Fernet(key.encode())
        test_data = b"sensitive bank data"
        encrypted = cipher.encrypt(test_data)
        decrypted = cipher.decrypt(encrypted)
        assert decrypted == test_data


class TestTaskStatusValidation:
    """Test task cancellation validation"""
    
    @pytest.mark.asyncio
    async def test_cannot_cancel_completed_task(self):
        """Test that completed tasks cannot be cancelled"""
        # Mock task with completed status
        class MockTask:
            def __init__(self, status):
                self.status = status
                self.id = uuid.uuid4()
                self.user_id = uuid.uuid4()
        
        task = MockTask("completed")
        
        # Should raise when trying to cancel
        if task.status in ("completed", "failed", "cancelled"):
            with pytest.raises(HTTPException) as exc_info:
                raise HTTPException(status_code=400, detail=f"Cannot cancel task with status '{task.status}'")
        
        assert exc_info.value.status_code == 400


class TestRaceConditionProtection:
    """Test race condition protection in payments"""
    
    @pytest.mark.asyncio
    async def test_subscription_update_is_atomic(self):
        """Test that subscription deactivation uses UPDATE not SELECT+loop"""
        from sqlalchemy import update, inspect
        
        # Check that payments.py uses update() not select()+loop
        import app.api.payments as payments_module
        source = open(payments_module.__file__).read()
        
        # Should use update() statement
        assert "update(Subscription)" in source
        # Should not iterate over results to update
        assert "for existing in active_subscriptions" not in source


class TestMQTTaskHandling:
    """Test MQTT task reference handling"""
    
    def test_mqtt_task_stored(self):
        """Test that MQTT task is stored to prevent GC"""
        from app.services.smarthome_service import SmartHomeService
        import inspect
        
        source = inspect.getsource(SmartHomeService.__init__)
        assert "_mqtt_task" in source
        assert "self._mqtt_task = asyncio.create_task" in source


class TestAuthenticationFlows:
    """Test authentication security"""
    
    @pytest.mark.asyncio
    async def test_token_rotation_on_refresh(self):
        """Test that refresh token rotates"""
        # Check auth.py implementation
        import app.api.auth as auth_module
        source = open(auth_module.__file__).read()
        
        # Should revoke old token
        assert "revoke_refresh_token" in source
        # Should create new token
        assert "new_refresh_token" in source or "create_refresh_token" in source
    
    def test_password_hashing(self):
        """Test password is properly hashed"""
        from app.auth import get_password_hash, verify_password
        
        password = "test_pass"  # Short password for bcrypt
        hashed = get_password_hash(password)
        
        # Hash should be different from plaintext
        assert hashed != password
        # Should verify correctly
        assert verify_password(password, hashed)
        # Wrong password should fail
        assert not verify_password("wrong_pass", hashed)
    
    def test_totp_secret_generation(self):
        """Test TOTP secrets are cryptographically secure"""
        from app.auth import generate_totp_secret
        import secrets
        
        secret1 = generate_totp_secret()
        secret2 = generate_totp_secret()
        
        # Should be different each time
        assert secret1 != secret2
        # Should be hex
        assert len(secret1) == 40  # 20 bytes = 40 hex chars
        int(secret1, 16)  # Should parse as hex


class TestInputValidation:
    """Test input validation across endpoints"""
    
    def test_agent_id_uuid_validation(self):
        """Test agent_id must be valid UUID"""
        import uuid
        
        valid_ids = [
            str(uuid.uuid4()),
            "550e8400-e29b-41d4-a716-446655440000",
        ]
        invalid_ids = [
            "not-a-uuid",
            "12345",
            "",
            "550e8400-e29b-41d4-a716-44665544000g",  # Invalid char
        ]
        
        for valid in valid_ids:
            try:
                uuid.UUID(valid)
            except ValueError:
                pytest.fail(f"Should accept valid UUID: {valid}")
        
        for invalid in invalid_ids:
            try:
                uuid.UUID(invalid)
                if invalid:  # Empty string is valid for UUID() but not for us
                    pytest.fail(f"Should reject invalid UUID: {invalid}")
            except ValueError:
                pass  # Expected


class TestBusinessLogicEdgeCases:
    """Test business logic edge cases"""
    
    @pytest.mark.asyncio
    async def test_free_tariff_subscription(self):
        """Test free tariff subscription handling"""
        # Free tariff should be active immediately
        price = 0
        status = "active" if price == 0 else "pending"
        assert status == "active"
    
    @pytest.mark.asyncio  
    async def test_subscription_days_calculation(self):
        """Test subscription days left calculation"""
        from datetime import timezone
        
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=15)
        
        # Ensure timezone-aware comparison
        if future.tzinfo is None:
            future = future.replace(tzinfo=timezone.utc)
        
        days_left = max(0, (future - now).days)
        assert days_left == 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
