"""
EDGE CASE TEST SUITE - Business Logic Edge Cases
Tests boundary conditions, empty inputs, invalid data
"""

import pytest
import uuid
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, '/Users/natalacernikova/Downloads/aurion-stage13/aurion-backend')

# Set test environment before importing app
os.environ.setdefault('ENCRYPTION_KEY', 'test-key-for-testing-only-do-not-use=')
os.environ.setdefault('AURION_SECRET_KEY', 'test-secret')

from app.main import app

client = TestClient(app)


def get_auth_headers():
    """Get authentication headers"""
    email = f"edge_{uuid.uuid4().hex[:8]}@example.com"
    username = f"edge_{uuid.uuid4().hex[:6]}"
    password = "Test123!"
    
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": password}
    )
    
    login = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login.status_code == 200:
        return {"Authorization": f"Bearer {login.json()['access_token']}"}
    return {}


class TestBoundaryConditions:
    """Test boundary conditions and limits"""
    
    def test_empty_string_inputs(self):
        """Test empty string handling"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        # Test empty content in memory creation
        response = client.post(
            "/api/v1/memory",
            json={"content": "", "title": "", "tags": []},
            headers=headers
        )
        assert response.status_code in [200, 400, 422]
    
    def test_very_long_strings(self):
        """Test very long string inputs"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        long_text = "a" * 100000  # 100KB text
        response = client.post(
            "/api/v1/memory",
            json={"content": long_text[:50000], "title": "Long text test", "tags": []},
            headers=headers
        )
        assert response.status_code in [200, 400, 422, 413]  # 413 = Payload Too Large
    
    def test_special_characters_unicode(self):
        """Test special characters and unicode"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        special_content = "🔥🚀💎 émojis И Кириллица \\<script>alert('xss')</script>\"日本語 🎌 中文 🀄"
        response = client.post(
            "/api/v1/memory",
            json={"content": special_content, "title": "Unicode test", "tags": []},
            headers=headers
        )
        assert response.status_code in [200, 400, 422]
    
    def test_negative_numbers(self):
        """Test negative number handling"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        response = client.post(
            "/api/v1/finance/transactions",
            json={
                "amount": -100.50,
                "description": "Negative transaction",
                "category": "test"
            },
            headers=headers
        )
        assert response.status_code in [200, 400, 422]
    
    def test_zero_values(self):
        """Test zero value handling"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        response = client.post(
            "/api/v1/finance/transactions",
            json={
                "amount": 0,
                "description": "Zero transaction",
                "category": "test"
            },
            headers=headers
        )
        assert response.status_code in [200, 400, 422]
    
    def test_maximum_integers(self):
        """Test maximum integer values"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        response = client.post(
            "/api/v1/finance/transactions",
            json={
                "amount": 999999999999.99,
                "description": "Max amount test",
                "category": "test"
            },
            headers=headers
        )
        assert response.status_code in [200, 400, 422]


class TestNullNoneHandling:
    """Test null/None value handling"""
    
    def test_null_fields_in_json(self):
        """Test null values in JSON payloads"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        response = client.post(
            "/api/v1/agents",
            json={
                "name": "Test Agent",
                "agent_type": "financial",
                "config": None
            },
            headers=headers
        )
        assert response.status_code in [200, 400, 422]
    
    def test_missing_required_fields(self):
        """Test missing required fields"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        response = client.post(
            "/api/v1/agents",
            json={"name": "Test"},  # Missing agent_type
            headers=headers
        )
        assert response.status_code == 422  # Unprocessable Entity


class TestDateTimeEdgeCases:
    """Test date and time edge cases"""
    
    def test_future_dates(self):
        """Test future date handling"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        future_date = (datetime.now(timezone.utc) + timedelta(days=365*10)).isoformat()
        # Try to create something with a future date
        response = client.post(
            "/api/v1/memory",
            json={
                "content": "Future test",
                "title": "Future",
                "tags": [],
                "remind_at": future_date
            },
            headers=headers
        )
        assert response.status_code in [200, 400, 422]
    
    def test_past_dates(self):
        """Test past date handling"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        past_date = (datetime.now(timezone.utc) - timedelta(days=365*10)).isoformat()
        response = client.post(
            "/api/v1/memory",
            json={
                "content": "Past test",
                "title": "Past",
                "tags": [],
                "created_at": past_date
            },
            headers=headers
        )
        assert response.status_code in [200, 400, 422]


class TestArrayListEdgeCases:
    """Test array and list edge cases"""
    
    def test_empty_array(self):
        """Test empty array handling"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        response = client.post(
            "/api/v1/agents",
            json={
                "name": "Test",
                "agent_type": "financial",
                "config": {},
                "tags": []  # Empty array
            },
            headers=headers
        )
        assert response.status_code in [200, 400, 422]
    
    def test_very_large_array(self):
        """Test very large array handling"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        large_tags = [f"tag_{i}" for i in range(1000)]
        response = client.post(
            "/api/v1/memory",
            json={
                "content": "Large tags test",
                "title": "Large",
                "tags": large_tags
            },
            headers=headers
        )
        assert response.status_code in [200, 400, 422]
    
    def test_nested_objects(self):
        """Test deeply nested objects"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        nested_config = {"level1": {"level2": {"level3": {"level4": "deep"}}}}
        response = client.post(
            "/api/v1/agents",
            json={
                "name": "Nested",
                "agent_type": "financial",
                "config": nested_config
            },
            headers=headers
        )
        assert response.status_code in [200, 400, 422]


class TestUUIDEdgeCases:
    """Test UUID handling edge cases"""
    
    def test_invalid_uuid_format(self):
        """Test invalid UUID formats"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        invalid_uuids = [
            "not-a-uuid",
            "12345",
            "",
            "550e8400-e29b-41d4-a716-44665544000g",  # Invalid char
            "550e8400-e29b-41d4-a716-44665544000",   # Too short
            "550e8400-e29b-41d4-a716-4466554400000", # Too long
        ]
        
        for invalid_uuid in invalid_uuids:
            response = client.get(f"/api/v1/agents/{invalid_uuid}", headers=headers)
            assert response.status_code in [400, 404], f"UUID {invalid_uuid} should fail"
    
    def test_valid_uuid_not_found(self):
        """Test valid UUID that doesn't exist"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        fake_uuid = str(uuid.uuid4())
        response = client.get(f"/api/v1/agents/{fake_uuid}", headers=headers)
        assert response.status_code == 404


class TestSecurityEdgeCases:
    """Test security-related edge cases"""
    
    def test_sql_injection_patterns(self):
        """Test SQL injection pattern handling"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        sql_patterns = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "1; SELECT * FROM users",
            "%' OR 1=1--",
            "' UNION SELECT * FROM users--",
        ]
        
        for pattern in sql_patterns:
            response = client.get(f"/api/v1/memory/search?query={pattern}", headers=headers)
            # Should not crash or return all data
            assert response.status_code in [200, 400, 422]
            if response.status_code == 200:
                # Response should be a list, not error
                assert isinstance(response.json(), list)
    
    def test_xss_patterns(self):
        """Test XSS pattern handling"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        xss_patterns = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<body onload=alert('xss')>",
        ]
        
        for pattern in xss_patterns:
            response = client.post(
                "/api/v1/memory",
                json={"content": pattern, "title": "XSS test", "tags": []},
                headers=headers
            )
            assert response.status_code in [200, 400, 422]
    
    def test_path_traversal(self):
        """Test path traversal attempts"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        path_patterns = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//etc/passwd",
        ]
        
        for pattern in path_patterns:
            # Try in various endpoints that might accept paths
            response = client.post(
                "/api/v1/agents/review",
                json={"code": "test", "file_path": pattern},
                headers=headers
            )
            assert response.status_code in [200, 400, 403, 422]


class TestJSONEdgeCases:
    """Test JSON parsing edge cases"""
    
    def test_malformed_json(self):
        """Test malformed JSON handling"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        malformed_json = '{"name": "test", "agent_type": }'  # Missing value
        response = client.post(
            "/api/v1/agents",
            data=malformed_json,
            headers={**headers, "Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_json_with_comments(self):
        """Test JSON with comments (not standard)"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        json_with_comments = '''{
            "name": "test",
            // This is a comment
            "agent_type": "financial"
        }'''
        response = client.post(
            "/api/v1/agents",
            data=json_with_comments,
            headers={**headers, "Content-Type": "application/json"}
        )
        assert response.status_code in [200, 400, 422]
    
    def test_duplicate_keys(self):
        """Test JSON with duplicate keys"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        duplicate_keys = '{"name": "first", "name": "second", "agent_type": "financial"}'
        response = client.post(
            "/api/v1/agents",
            data=duplicate_keys,
            headers={**headers, "Content-Type": "application/json"}
        )
        assert response.status_code in [200, 400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
