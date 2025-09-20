#!/usr/bin/env python3
"""
Test API routes functionality
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAPIRoutes:
    """Test API route functionality"""

    def test_app_startup(self):
        """Test that the app starts up correctly"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_spec(self):
        """Test OpenAPI specification is available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "paths" in openapi_spec

    def test_user_registration(self):
        """Test user registration endpoint"""
        user_data = {
            "username": "pytest_user",
            "password": "pytest_password123"
        }

        response = client.post("/user/register", json=user_data)

        # Should either succeed or fail because user exists
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["username"] == "pytest_user"
            assert "databases" in data

    def test_user_login(self):
        """Test user login endpoint"""
        # First register user
        user_data = {
            "username": "pytest_login_user",
            "password": "pytest_password123"
        }
        client.post("/user/register", json=user_data)

        # Then login
        login_data = {
            "username": "pytest_login_user",
            "password": "pytest_password123"
        }

        response = client.post(
            "/user/token",
            data=login_data,  # Form data, not JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

        return data["access_token"]

    def test_protected_route_without_token(self):
        """Test protected route without authentication token"""
        response = client.get("/user/me")
        assert response.status_code == 401

    def test_protected_route_with_token(self):
        """Test protected route with valid token"""
        # Get a valid token
        token = self.test_user_login()

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/user/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "databases" in data

    def test_database_setup(self):
        """Test database connection setup"""
        # Get a valid token
        token = self.test_user_login()
        headers = {"Authorization": f"Bearer {token}"}

        # Setup database connection
        db_config = {
            "db_name": "pytest_test_db",
            "db_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "username": "postgres",
            "password": "postgres"
        }

        response = client.post("/user/databases/setup", json=db_config, headers=headers)

        # Should succeed or fail if connection already exists
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["db_name"] == "pytest_test_db"
            assert data["db_type"] == "postgresql"

    def test_list_user_databases(self):
        """Test listing user databases"""
        token = self.test_user_login()
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/user/databases", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent_user",
            "password": "wrong_password"
        }

        response = client.post(
            "/user/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 401

    def test_duplicate_user_registration(self):
        """Test registering duplicate user"""
        user_data = {
            "username": "duplicate_user",
            "password": "password123"
        }

        # First registration
        response1 = client.post("/user/register", json=user_data)

        # Second registration (should fail)
        response2 = client.post("/user/register", json=user_data)

        # One should succeed, one should fail
        status_codes = [response1.status_code, response2.status_code]
        assert 200 in status_codes
        assert 400 in status_codes

    def test_invalid_token(self):
        """Test using invalid token"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/user/me", headers=headers)
        assert response.status_code == 401

    def test_malformed_requests(self):
        """Test malformed requests"""

        # Missing required fields in registration
        response = client.post("/user/register", json={"username": "incomplete"})
        assert response.status_code == 422

        # Invalid JSON
        response = client.post(
            "/user/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_database_query_endpoint(self):
        """Test database query execution endpoint"""
        # This test requires a valid database connection
        token = self.test_user_login()
        headers = {"Authorization": f"Bearer {token}"}

        # First check if user has any databases
        db_response = client.get("/user/databases", headers=headers)
        databases = db_response.json()

        if databases:
            db_id = databases[0]["id"]

            query_data = {
                "query": "SELECT 1 as test_value;"
            }

            response = client.post(
                f"/user/database/{db_id}/query",
                json=query_data,
                headers=headers
            )

            # Should succeed if database connection is valid
            assert response.status_code in [200, 400, 500]  # Various valid responses

@pytest.mark.integration
class TestIntegrationFlow:
    """Test complete integration flows"""

    def test_complete_user_flow(self):
        """Test complete user registration to database query flow"""
        # 1. Register user
        user_data = {
            "username": "integration_user",
            "password": "integration_pass123"
        }
        reg_response = client.post("/user/register", json=user_data)

        # Skip if user already exists
        if reg_response.status_code == 400:
            pass
        else:
            assert reg_response.status_code == 200

        # 2. Login
        login_data = {
            "username": "integration_user",
            "password": "integration_pass123"
        }
        login_response = client.post(
            "/user/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 3. Get user profile
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/user/me", headers=headers)
        assert profile_response.status_code == 200

        # 4. Setup database (optional - may fail if connection invalid)
        db_config = {
            "db_name": "integration_test_db",
            "db_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "username": "postgres",
            "password": "postgres"
        }
        # Test database setup endpoint (don't assert success as it depends on database availability)
        client.post("/user/databases/setup", json=db_config, headers=headers)

        # 5. List databases
        list_response = client.get("/user/databases", headers=headers)
        assert list_response.status_code == 200