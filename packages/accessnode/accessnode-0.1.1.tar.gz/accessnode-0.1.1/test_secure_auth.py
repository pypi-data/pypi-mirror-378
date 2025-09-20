#!/usr/bin/env python3
# test_secure_auth.py - Comprehensive test for the new secure authentication system
import asyncio
import json
import requests
from typing import Dict, Any
import time


class SecureAuthTester:
    """Comprehensive tester for the secure authentication system"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        # Use timestamp to ensure unique username each run
        import time
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        self.test_user = {
            "username": f"sectest_{timestamp}",
            "password": "SecureP@ssw0rd123!"
        }

    def print_test_header(self, test_name: str):
        """Print formatted test header"""
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print(f"{'='*60}")

    def print_result(self, success: bool, message: str):
        """Print test result"""
        icon = "✅" if success else "❌"
        print(f"{icon} {message}")

    def test_security_info(self) -> bool:
        """Test security configuration endpoint"""
        self.print_test_header("Security Configuration")

        try:
            response = self.session.get(f"{self.base_url}/auth/security-info")

            if response.status_code == 200:
                config = response.json()
                required_keys = ["password_requirements", "token_config", "rate_limiting"]

                for key in required_keys:
                    if key not in config:
                        self.print_result(False, f"Missing configuration key: {key}")
                        return False

                self.print_result(True, "Security configuration endpoint working")
                print(f"Password requirements: {config['password_requirements']}")
                return True
            else:
                self.print_result(False, f"Security info failed: {response.status_code}")
                return False

        except Exception as e:
            self.print_result(False, f"Security info error: {e}")
            return False

    def test_user_registration(self) -> bool:
        """Test user registration with password validation"""
        self.print_test_header("User Registration")

        # Test weak password rejection
        weak_passwords = [
            "123",  # Too short
            "password",  # Too common
            "abc123",  # No uppercase or symbols
            "PASSWORD123"  # No lowercase or symbols
        ]

        for weak_pass in weak_passwords:
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/register",
                    json={
                        "username": f"test_{weak_pass}",
                        "password": weak_pass
                    }
                )

                if response.status_code == 422:  # Validation error expected
                    self.print_result(True, f"Weak password '{weak_pass}' correctly rejected")
                else:
                    self.print_result(False, f"Weak password '{weak_pass}' was accepted")
                    return False

            except Exception as e:
                self.print_result(False, f"Error testing weak password: {e}")
                return False

        # Test successful registration
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=self.test_user
            )

            if response.status_code == 201:
                user_data = response.json()
                self.print_result(True, f"User registered successfully: {user_data['username']}")
                return True
            else:
                self.print_result(False, f"Registration failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.print_result(False, f"Registration error: {e}")
            return False

    def test_login_and_tokens(self) -> bool:
        """Test login and JWT token functionality"""
        self.print_test_header("Login and Token Management")

        # Test failed login
        try:
            response = self.session.post(
                f"{self.base_url}/auth/token",
                data={
                    "username": self.test_user["username"],
                    "password": "wrong_password"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code == 401:
                self.print_result(True, "Invalid credentials correctly rejected")
            else:
                self.print_result(False, f"Invalid login should return 401, got {response.status_code}")
                return False

        except Exception as e:
            self.print_result(False, f"Failed login test error: {e}")
            return False

        # Test successful login
        try:
            response = self.session.post(
                f"{self.base_url}/auth/token",
                data=self.test_user,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code == 200:
                token_data = response.json()
                required_fields = ["access_token", "refresh_token", "token_type", "expires_in"]

                for field in required_fields:
                    if field not in token_data:
                        self.print_result(False, f"Missing token field: {field}")
                        return False

                self.access_token = token_data["access_token"]
                self.refresh_token = token_data["refresh_token"]

                self.print_result(True, "Login successful, tokens received")
                self.print_result(True, f"Token type: {token_data['token_type']}")
                self.print_result(True, f"Expires in: {token_data['expires_in']} seconds")
                return True
            else:
                self.print_result(False, f"Login failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.print_result(False, f"Login error: {e}")
            return False

    def test_protected_endpoints(self) -> bool:
        """Test access to protected endpoints"""
        self.print_test_header("Protected Endpoint Access")

        if not self.access_token:
            self.print_result(False, "No access token available")
            return False

        # Test without token
        try:
            response = self.session.get(f"{self.base_url}/auth/me")
            if response.status_code == 401:
                self.print_result(True, "Unauthorized access correctly blocked")
            else:
                self.print_result(False, f"Should be unauthorized, got {response.status_code}")

        except Exception as e:
            self.print_result(False, f"Unauthorized test error: {e}")

        # Test with valid token
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.session.get(f"{self.base_url}/auth/me", headers=headers)

            if response.status_code == 200:
                user_data = response.json()
                self.print_result(True, f"Authorized access successful: {user_data['username']}")
                return True
            else:
                self.print_result(False, f"Authorized access failed: {response.status_code}")
                return False

        except Exception as e:
            self.print_result(False, f"Authorized access error: {e}")
            return False

    def test_token_refresh(self) -> bool:
        """Test JWT token refresh functionality"""
        self.print_test_header("Token Refresh")

        if not self.refresh_token:
            self.print_result(False, "No refresh token available")
            return False

        try:
            response = self.session.post(
                f"{self.base_url}/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )

            if response.status_code == 200:
                token_data = response.json()
                new_access_token = token_data["access_token"]
                new_refresh_token = token_data["refresh_token"]

                # Verify new tokens are different
                if new_access_token != self.access_token:
                    self.print_result(True, "New access token generated")
                    self.access_token = new_access_token
                    self.refresh_token = new_refresh_token
                    return True
                else:
                    self.print_result(False, "New token should be different from old token")
                    return False
            else:
                self.print_result(False, f"Token refresh failed: {response.status_code}")
                return False

        except Exception as e:
            self.print_result(False, f"Token refresh error: {e}")
            return False

    def test_rate_limiting(self) -> bool:
        """Test rate limiting on authentication attempts"""
        self.print_test_header("Rate Limiting")

        # Create a new user for rate limiting test
        import time
        rate_timestamp = str(int(time.time()))[-4:]  # Last 4 digits for rate test
        rate_test_user = {
            "username": f"ratetest_{rate_timestamp}",
            "password": "RateTest123!"
        }

        # Register user first
        try:
            self.session.post(f"{self.base_url}/auth/register", json=rate_test_user)
        except:
            pass  # User might already exist

        # Attempt multiple failed logins
        failed_attempts = 0
        for i in range(7):  # Try more than the limit (usually 5)
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/token",
                    data={
                        "username": rate_test_user["username"],
                        "password": "wrong_password"
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )

                if response.status_code == 401:
                    failed_attempts += 1
                    if "too many" in response.text.lower() or "rate" in response.text.lower():
                        self.print_result(True, f"Rate limiting activated after {failed_attempts} attempts")
                        return True
                elif response.status_code == 429:  # Too Many Requests
                    self.print_result(True, f"Rate limiting activated with HTTP 429 after {failed_attempts} attempts")
                    return True

                time.sleep(0.1)  # Small delay between attempts

            except Exception as e:
                self.print_result(False, f"Rate limiting test error: {e}")
                return False

        self.print_result(False, "Rate limiting not detected after multiple failed attempts")
        return False

    def test_password_change(self) -> bool:
        """Test password change functionality"""
        self.print_test_header("Password Change")

        if not self.access_token:
            self.print_result(False, "No access token available")
            return False

        new_password = "NewSecureP@ssw0rd456!"

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.session.post(
                f"{self.base_url}/auth/change-password",
                json={
                    "current_password": self.test_user["password"],
                    "new_password": new_password
                },
                headers=headers
            )

            if response.status_code == 200:
                self.print_result(True, "Password changed successfully")

                # Update test user password
                self.test_user["password"] = new_password

                # Test login with new password
                login_response = self.session.post(
                    f"{self.base_url}/auth/token",
                    data=self.test_user,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )

                if login_response.status_code == 200:
                    self.print_result(True, "Login successful with new password")
                    return True
                else:
                    self.print_result(False, "Login failed with new password")
                    return False
            else:
                self.print_result(False, f"Password change failed: {response.status_code}")
                return False

        except Exception as e:
            self.print_result(False, f"Password change error: {e}")
            return False

    def test_logout(self) -> bool:
        """Test logout functionality"""
        self.print_test_header("Logout")

        if not self.access_token:
            self.print_result(False, "No access token available")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.session.post(f"{self.base_url}/auth/logout", headers=headers)

            if response.status_code == 200:
                self.print_result(True, "Logout successful")
                return True
            else:
                self.print_result(False, f"Logout failed: {response.status_code}")
                return False

        except Exception as e:
            self.print_result(False, f"Logout error: {e}")
            return False

    def test_security_headers(self) -> bool:
        """Test security headers in responses"""
        self.print_test_header("Security Headers")

        try:
            response = self.session.get(f"{self.base_url}/health")

            expected_headers = [
                "x-content-type-options",
                "x-frame-options",
                "x-xss-protection",
                "referrer-policy"
            ]

            headers_found = 0
            for header in expected_headers:
                if header in response.headers:
                    headers_found += 1
                    self.print_result(True, f"Security header found: {header}")

            if headers_found >= len(expected_headers) // 2:  # At least half
                self.print_result(True, f"Security headers present ({headers_found}/{len(expected_headers)})")
                return True
            else:
                self.print_result(False, f"Insufficient security headers ({headers_found}/{len(expected_headers)})")
                return False

        except Exception as e:
            self.print_result(False, f"Security headers test error: {e}")
            return False

    def cleanup(self):
        """Clean up test data"""
        self.print_test_header("Cleanup")
        # In a real implementation, you might want to delete the test user
        self.print_result(True, "Test completed (cleanup would remove test users)")

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all security tests"""
        print("🔒 Starting Comprehensive Security Authentication Tests")
        print("="*80)

        tests = [
            ("Security Configuration", self.test_security_info),
            ("User Registration", self.test_user_registration),
            ("Login and Tokens", self.test_login_and_tokens),
            ("Protected Endpoints", self.test_protected_endpoints),
            ("Token Refresh", self.test_token_refresh),
            ("Rate Limiting", self.test_rate_limiting),
            ("Password Change", self.test_password_change),
            ("Logout", self.test_logout),
            ("Security Headers", self.test_security_headers),
        ]

        results = {}
        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results[test_name] = False

        # Summary
        self.print_test_header("Test Summary")
        print(f"Tests passed: {passed}/{total}")
        print(f"Success rate: {(passed/total)*100:.1f}%")

        for test_name, result in results.items():
            icon = "✅" if result else "❌"
            print(f"{icon} {test_name}")

        if passed == total:
            print("\n🎉 All security tests passed! The authentication system is ready for production.")
        else:
            print(f"\n⚠️  {total-passed} tests failed. Please review and fix issues before deployment.")

        self.cleanup()
        return results


def main():
    """Main test runner"""
    import sys

    base_url = "http://127.0.0.1:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"Testing secure authentication system at: {base_url}")

    tester = SecureAuthTester(base_url)
    results = tester.run_all_tests()

    # Exit with error code if any tests failed
    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()