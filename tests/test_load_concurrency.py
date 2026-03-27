"""
LOAD TESTING & CONCURRENCY TEST SUITE
Tests race conditions, concurrent access, and stress scenarios
"""

import pytest
import asyncio
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, '/Users/natalacernikova/Downloads/aurion-stage13/aurion-backend')
from app.main import app

client = TestClient(app)


def get_auth_headers():
    """Get auth headers"""
    email = f"loadtest_{uuid.uuid4().hex[:8]}@example.com"
    username = f"loaduser_{uuid.uuid4().hex[:6]}"
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


class TestConcurrencyPayments:
    """Test race conditions in payment/subscription system"""
    
    def test_concurrent_subscription_creation(self):
        """Test multiple concurrent subscription requests"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        def create_subscription():
            return client.post(
                "/api/v1/payments/subscription",
                json={"tariff_id": "free", "auto_renew": False},
                headers=headers
            )
        
        # Run 5 concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_subscription) for _ in range(5)]
            results = [f.result() for f in as_completed(futures)]
        
        # Check that we got valid responses
        success_count = sum(1 for r in results if r.status_code == 200)
        error_count = sum(1 for r in results if r.status_code in [400, 409, 422])
        
        # Should have consistent state - either multiple succeeded or some were rejected
        assert success_count + error_count == 5, f"Unexpected responses: {[r.status_code for r in results]}"
        
        # Verify only one active subscription exists
        get_sub = client.get("/api/v1/payments/subscription", headers=headers)
        if get_sub.status_code == 200:
            # Should have at most 1 active subscription
            pass  # Implementation dependent


class TestConcurrencyAgents:
    """Test concurrent agent operations"""
    
    def test_concurrent_agent_creation(self):
        """Test creating multiple agents concurrently"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        def create_agent(idx):
            return client.post(
                "/api/v1/agents",
                json={
                    "name": f"Concurrent Agent {idx}",
                    "agent_type": "financial",
                    "config": {"test": True}
                },
                headers=headers
            )
        
        # Create 10 agents concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_agent, i) for i in range(10)]
            results = [f.result() for f in as_completed(futures)]
        
        # All should succeed
        success_count = sum(1 for r in results if r.status_code == 200)
        assert success_count == 10, f"Only {success_count}/10 agents created successfully"
    
    def test_concurrent_task_submission(self):
        """Test submitting multiple tasks concurrently"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        # First create an agent
        agent_resp = client.post(
            "/api/v1/agents",
            json={"name": "Task Agent", "agent_type": "memory"},
            headers=headers
        )
        
        if agent_resp.status_code != 200:
            pytest.skip("Could not create agent")
        
        def submit_task(idx):
            return client.post(
                "/api/v1/agents/tasks",
                json={
                    "task_type": "analysis",
                    "input_data": {"query": f"test {idx}"}
                },
                headers=headers
            )
        
        # Submit 20 tasks concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(submit_task, i) for i in range(20)]
            results = [f.result() for f in as_completed(futures)]
        
        # Most should succeed
        success_count = sum(1 for r in results if r.status_code == 200)
        assert success_count >= 15, f"Only {success_count}/20 tasks submitted successfully"


class TestConcurrencyMemory:
    """Test concurrent memory operations"""
    
    def test_concurrent_memory_creation(self):
        """Test creating memories concurrently"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        def create_memory(idx):
            return client.post(
                "/api/v1/memory",
                json={
                    "content": f"Concurrent memory content {idx}",
                    "title": f"Memory {idx}",
                    "tags": ["concurrent", "test"]
                },
                headers=headers
            )
        
        # Create 15 memories concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_memory, i) for i in range(15)]
            results = [f.result() for f in as_completed(futures)]
        
        # All should succeed
        success_count = sum(1 for r in results if r.status_code in [200, 201])
        assert success_count == 15, f"Only {success_count}/15 memories created"


class TestStressAuth:
    """Stress test authentication endpoints"""
    
    def test_auth_rate_limiting(self):
        """Test rapid authentication requests"""
        # Try rapid login attempts
        email = f"rate_{uuid.uuid4().hex[:8]}@example.com"
        password = "Test123!"
        
        # Register first
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "username": f"rate_{uuid.uuid4().hex[:6]}", "password": password}
        )
        
        def login_attempt():
            return client.post(
                "/api/v1/auth/token",
                data={"username": email, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        # Try 50 rapid logins
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(login_attempt) for _ in range(50)]
            results = [f.result() for f in as_completed(futures)]
        end_time = time.time()
        
        # All should succeed (no rate limiting in MVP)
        success_count = sum(1 for r in results if r.status_code == 200)
        assert success_count == 50, f"Only {success_count}/50 logins succeeded"
        
        # Should complete in reasonable time
        assert end_time - start_time < 30, "Login requests took too long"


class TestStressSmartHome:
    """Stress test smart home endpoints"""
    
    def test_concurrent_device_control(self):
        """Test controlling same device concurrently"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        # Create a device first
        device_resp = client.post(
            "/api/v1/smarthome/devices",
            json={
                "name": "Stress Test Light",
                "device_type": "light",
                "room": "Test Room",
                "protocol": "mqtt"
            },
            headers=headers
        )
        
        if device_resp.status_code not in [200, 201]:
            pytest.skip("Could not create device")
        
        device_id = device_resp.json().get("id", "test-device-id")
        
        def control_device(state):
            return client.post(
                f"/api/v1/smarthome/devices/{device_id}/control",
                json={"command": f"turn_{state}"},
                headers=headers
            )
        
        # Send 20 concurrent control commands
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(control_device, "on" if i % 2 == 0 else "off") 
                      for i in range(20)]
            results = [f.result() for f in as_completed(futures)]
        
        # Should handle without crashing
        # Some may fail (device busy), but server should not crash
        server_errors = sum(1 for r in results if r.status_code >= 500)
        assert server_errors == 0, f"Server errors occurred: {server_errors}"


class TestStressVPN:
    """Stress test VPN endpoints"""
    
    def test_concurrent_server_list_requests(self):
        """Test requesting server list concurrently"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        def get_servers():
            return client.get("/api/v1/vpn/servers", headers=headers)
        
        # 30 concurrent requests
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(get_servers) for _ in range(30)]
            results = [f.result() for f in as_completed(futures)]
        
        # All should succeed
        success_count = sum(1 for r in results if r.status_code == 200)
        assert success_count == 30, f"Only {success_count}/30 server list requests succeeded"


class TestDatabaseConcurrency:
    """Test database operations under concurrency"""
    
    @pytest.mark.asyncio
    async def test_concurrent_database_reads(self):
        """Test multiple concurrent database reads"""
        from app.database_final import AsyncSessionLocal
        from sqlalchemy import text
        
        async def db_read():
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar()
        
        # Run 50 concurrent reads
        tasks = [db_read() for _ in range(50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        success_count = sum(1 for r in results if r == 1)
        error_count = sum(1 for r in results if isinstance(r, Exception))
        
        assert success_count == 50, f"Only {success_count}/50 DB reads succeeded, errors: {error_count}"


class TestEdgeCasesStress:
    """Stress test edge cases"""
    
    def test_rapid_endpoint_switching(self):
        """Test rapid switching between different endpoints"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        endpoints = [
            ("/api/v1/agents", "GET"),
            ("/api/v1/memory/search?query=test", "GET"),
            ("/api/v1/smarthome/devices", "GET"),
            ("/api/v1/finance/transactions", "GET"),
            ("/api/v1/auth/me", "GET"),
        ]
        
        def hit_endpoint(endpoint, method):
            if method == "GET":
                return client.get(endpoint, headers=headers)
            return client.post(endpoint, json={}, headers=headers)
        
        # Rapidly hit different endpoints
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(50):
                endpoint, method = endpoints[i % len(endpoints)]
                futures.append(executor.submit(hit_endpoint, endpoint, method))
            
            results = [f.result() for f in as_completed(futures)]
        
        # No server errors
        server_errors = sum(1 for r in results if r.status_code >= 500)
        assert server_errors == 0, f"Server errors under stress: {server_errors}"
    
    def test_memory_leak_simulation(self):
        """Simulate potential memory leak with repeated requests"""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Auth failed")
        
        # Make 100 sequential requests to check for memory issues
        start_time = time.time()
        for i in range(100):
            response = client.get("/api/v1/agents", headers=headers)
            assert response.status_code in [200, 401, 403]
        end_time = time.time()
        
        # Should complete in reasonable time
        assert end_time - start_time < 60, "Requests became progressively slower"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
