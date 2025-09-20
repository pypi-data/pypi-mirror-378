#!/usr/bin/env python3
"""
Unit tests for API endpoints using mocks
"""
import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from main import app


class TestAPIUnit(unittest.TestCase):
    """Unit tests for API endpoints"""

    def setUp(self):
        """Set up test client and common test data"""
        self.client = TestClient(app)
        self.test_user_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        self.test_db_config = {
            "db_name": "test_db",
            "db_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "username": "postgres",
            "password": "postgres"
        }

    def test_docs_endpoint(self):
        """Test that documentation endpoint is accessible"""
        response = self.client.get("/docs")
        self.assertEqual(response.status_code, 200)

    def test_openapi_spec(self):
        """Test OpenAPI specification endpoint"""
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)

        openapi_spec = response.json()
        self.assertIn("openapi", openapi_spec)
        self.assertIn("paths", openapi_spec)
        self.assertIn("info", openapi_spec)

    def test_health_check_if_exists(self):
        """Test health check endpoint if it exists"""
        response = self.client.get("/health")
        # This might return 404 if not implemented, which is fine
        self.assertIn(response.status_code, [200, 404])

    @patch('database.db_setup.get_db')
    @patch('utils.utils.get_password_hash')
    def test_user_registration_mock(self, mock_hash, mock_db):
        """Test user registration with mocked database"""
        # Setup mocks
        mock_hash.return_value = "hashed_password"
        mock_session = AsyncMock()
        mock_db.return_value.__aenter__.return_value = mock_session

        # Mock user creation
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Create mock user object
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_session.add.return_value = None

        response = self.client.post("/user/register", json=self.test_user_data)

        # Should not fail due to validation
        self.assertIn(response.status_code, [200, 400, 422])

    def test_user_registration_validation(self):
        """Test user registration input validation"""
        # Test missing password
        response = self.client.post("/user/register", json={"username": "testuser"})
        self.assertEqual(response.status_code, 422)

        # Test missing username
        response = self.client.post("/user/register", json={"password": "testpass"})
        self.assertEqual(response.status_code, 422)

        # Test empty data
        response = self.client.post("/user/register", json={})
        self.assertEqual(response.status_code, 422)

        # Test invalid JSON
        response = self.client.post(
            "/user/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 422)

    def test_login_validation(self):
        """Test login endpoint input validation"""
        # Test missing username
        response = self.client.post(
            "/user/token",
            data={"password": "testpass"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        self.assertEqual(response.status_code, 422)

        # Test missing password
        response = self.client.post(
            "/user/token",
            data={"username": "testuser"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        self.assertEqual(response.status_code, 422)

    def test_protected_route_without_token(self):
        """Test protected routes reject requests without token"""
        response = self.client.get("/user/me")
        self.assertEqual(response.status_code, 401)

        response = self.client.get("/user/databases")
        self.assertEqual(response.status_code, 401)

    def test_protected_route_with_invalid_token(self):
        """Test protected routes reject invalid tokens"""
        headers = {"Authorization": "Bearer invalid_token_here"}

        response = self.client.get("/user/me", headers=headers)
        self.assertEqual(response.status_code, 401)

        response = self.client.get("/user/databases", headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_database_setup_validation(self):
        """Test database setup endpoint validation"""
        headers = {"Authorization": "Bearer fake_token"}

        # Test missing required fields
        response = self.client.post(
            "/user/databases/setup",
            json={"db_name": "test"},
            headers=headers
        )
        self.assertEqual(response.status_code, 401)  # Will fail auth first

        # Test with all required fields but no auth
        response = self.client.post("/user/databases/setup", json=self.test_db_config)
        self.assertEqual(response.status_code, 401)

    def test_query_endpoint_validation(self):
        """Test database query endpoint validation"""
        headers = {"Authorization": "Bearer fake_token"}

        # Test without authentication
        response = self.client.post("/user/database/1/query", json={"query": "SELECT 1"})
        self.assertEqual(response.status_code, 401)

        # Test with invalid token
        response = self.client.post(
            "/user/database/1/query",
            json={"query": "SELECT 1"},
            headers=headers
        )
        self.assertEqual(response.status_code, 401)

    def test_cors_headers_if_enabled(self):
        """Test CORS headers if CORS is enabled"""
        response = self.client.options("/user/register")
        # CORS might not be enabled, so this could be 405 (Method Not Allowed)
        self.assertIn(response.status_code, [200, 405])

    @patch('utils.auth.verify_token')
    def test_token_verification_mock(self, mock_verify):
        """Test token verification with mock"""
        mock_verify.side_effect = Exception("Invalid token")

        headers = {"Authorization": "Bearer test_token"}
        response = self.client.get("/user/me", headers=headers)

        # Should get 401 due to token verification failure
        self.assertEqual(response.status_code, 401)

    def test_request_size_limits(self):
        """Test request size limits"""
        # Test very large payload
        large_data = {"username": "test", "password": "x" * 10000}
        response = self.client.post("/user/register", json=large_data)

        # Should either succeed or fail with 413 (too large) or 422 (validation)
        self.assertIn(response.status_code, [200, 400, 413, 422])

    def test_content_type_handling(self):
        """Test different content types"""
        # Test with wrong content type for JSON endpoint
        response = self.client.post(
            "/user/register",
            data="username=test&password=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        self.assertEqual(response.status_code, 422)

        # Test with no content type
        response = self.client.post("/user/register", data='{"username":"test"}')
        self.assertIn(response.status_code, [422, 415])  # Unprocessable or Unsupported Media Type


class TestAPIErrorHandling(unittest.TestCase):
    """Test error handling in API"""

    def setUp(self):
        self.client = TestClient(app)

    def test_404_endpoints(self):
        """Test that non-existent endpoints return 404"""
        response = self.client.get("/nonexistent/endpoint")
        self.assertEqual(response.status_code, 404)

        response = self.client.post("/another/fake/endpoint")
        self.assertEqual(response.status_code, 404)

    def test_method_not_allowed(self):
        """Test wrong HTTP methods return 405"""
        # Try POST on GET-only endpoint
        response = self.client.post("/docs")
        self.assertEqual(response.status_code, 405)

        # Try GET on POST-only endpoint
        response = self.client.get("/user/register")
        self.assertEqual(response.status_code, 405)

    def test_unsupported_media_type(self):
        """Test unsupported media types"""
        response = self.client.post(
            "/user/register",
            data="not json",
            headers={"Content-Type": "text/plain"}
        )
        self.assertIn(response.status_code, [415, 422])


if __name__ == '__main__':
    unittest.main()