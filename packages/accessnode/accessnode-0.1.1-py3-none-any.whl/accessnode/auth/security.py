# security.py - Production-ready authentication and authorization
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from enum import Enum

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
import re

from database.db_setup import get_db
from database.models import User
from database.db_utilities import get_user_by_username
import os


class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    USER = "user"
    READ_ONLY = "read_only"


class TokenType(str, Enum):
    """Token types"""
    ACCESS = "access"
    REFRESH = "refresh"


class SecurityConfig:
    """Centralized security configuration"""

    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Short-lived access tokens
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # Longer-lived refresh tokens

    # Password Configuration
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SYMBOLS: bool = True

    # Rate Limiting
    LOGIN_ATTEMPTS_LIMIT: int = 5
    LOGIN_LOCKOUT_DURATION_MINUTES: int = 15

    # Security Headers
    SECURE_COOKIES: bool = True
    COOKIE_SAMESITE: str = "strict"
    COOKIE_HTTPONLY: bool = True

    @classmethod
    def validate_production_config(cls) -> bool:
        """Validate that production configuration is secure"""
        issues = []

        if cls.SECRET_KEY == "keykey" or len(cls.SECRET_KEY) < 32:
            issues.append("SECRET_KEY is not secure")

        if cls.REFRESH_SECRET_KEY == cls.SECRET_KEY:
            issues.append("REFRESH_SECRET_KEY should be different from SECRET_KEY")

        if cls.ACCESS_TOKEN_EXPIRE_MINUTES > 60:
            issues.append("ACCESS_TOKEN_EXPIRE_MINUTES should be <= 60 for security")

        if issues:
            raise ValueError(f"Security configuration issues: {', '.join(issues)}")

        return True


# Initialize security configuration
config = SecurityConfig()

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class PasswordValidator:
    """Comprehensive password validation"""

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, list[str]]:
        """Validate password meets security requirements"""
        errors = []

        if len(password) < config.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {config.PASSWORD_MIN_LENGTH} characters")

        if config.PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")

        if config.PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")

        if config.PASSWORD_REQUIRE_DIGITS and not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")

        if config.PASSWORD_REQUIRE_SYMBOLS and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one symbol")

        # Check for common weak passwords
        weak_passwords = {"password", "123456", "qwerty", "admin", "letmein"}
        if password.lower() in weak_passwords:
            errors.append("Password is too common")

        return len(errors) == 0, errors


class UsernameValidator:
    """Username validation"""

    @staticmethod
    def validate_username(username: str) -> tuple[bool, list[str]]:
        """Validate username meets requirements"""
        errors = []

        if len(username) < 3:
            errors.append("Username must be at least 3 characters")

        if len(username) > 50:
            errors.append("Username must be less than 50 characters")

        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            errors.append("Username can only contain letters, numbers, underscores, and hyphens")

        if username.lower() in {"admin", "root", "system", "null", "undefined"}:
            errors.append("Username is reserved")

        return len(errors) == 0, errors


class SecureTokenManager:
    """Secure JWT token management"""

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": TokenType.ACCESS,
            "jti": secrets.token_urlsafe(16)  # JWT ID for token revocation
        })

        return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create refresh token"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": TokenType.REFRESH,
            "jti": secrets.token_urlsafe(16)
        })

        return jwt.encode(to_encode, config.REFRESH_SECRET_KEY, algorithm=config.ALGORITHM)

    @staticmethod
    def verify_token(token: str, token_type: TokenType = TokenType.ACCESS) -> dict:
        """Verify and decode token"""
        try:
            secret_key = config.SECRET_KEY if token_type == TokenType.ACCESS else config.REFRESH_SECRET_KEY
            payload = jwt.decode(token, secret_key, algorithms=[config.ALGORITHM])

            # Verify token type
            if payload.get("type") != token_type:
                raise JWTError("Invalid token type")

            return payload

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


class RateLimiter:
    """In-memory rate limiter for login attempts"""

    def __init__(self):
        self._attempts: Dict[str, list] = {}

    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=config.LOGIN_LOCKOUT_DURATION_MINUTES)

        # Clean old attempts
        if identifier in self._attempts:
            self._attempts[identifier] = [
                attempt_time for attempt_time in self._attempts[identifier]
                if attempt_time > cutoff
            ]

        # Check if rate limited
        return len(self._attempts.get(identifier, [])) >= config.LOGIN_ATTEMPTS_LIMIT

    def record_attempt(self, identifier: str):
        """Record a failed login attempt"""
        if identifier not in self._attempts:
            self._attempts[identifier] = []

        self._attempts[identifier].append(datetime.now(timezone.utc))

    def clear_attempts(self, identifier: str):
        """Clear attempts after successful login"""
        if identifier in self._attempts:
            del self._attempts[identifier]


# Global rate limiter instance
rate_limiter = RateLimiter()


class SecurePasswordManager:
    """Secure password operations"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password securely"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            # Log the error but don't expose details
            return False

    @staticmethod
    def generate_secure_password() -> str:
        """Generate a cryptographically secure password"""
        return secrets.token_urlsafe(16)


class SecurityHeaders:
    """Security headers for responses"""

    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()"
        }


# Pydantic models for validation
class UserCreateSecure(BaseModel):
    """Secure user creation model with validation"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @validator('username')
    def validate_username(cls, v):
        is_valid, errors = UsernameValidator.validate_username(v)
        if not is_valid:
            raise ValueError(f"Username validation failed: {', '.join(errors)}")
        return v

    @validator('password')
    def validate_password(cls, v):
        is_valid, errors = PasswordValidator.validate_password_strength(v)
        if not is_valid:
            raise ValueError(f"Password validation failed: {', '.join(errors)}")
        return v


class TokenResponse(BaseModel):
    """Secure token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[UserRole] = None
    jti: Optional[str] = None


async def get_current_user_secure(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Securely get current user from token"""

    try:
        payload = SecureTokenManager.verify_token(token, TokenType.ACCESS)
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        token_data = TokenData(
            username=username,
            user_id=user_id,
            role=UserRole(payload.get("role", UserRole.USER)),
            jti=payload.get("jti")
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = await get_user_by_username(db, username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def require_role(required_role: UserRole):
    """Decorator to require specific role"""
    def role_checker(current_user: User = Depends(get_current_user_secure)):
        # For now, assume all users are USER role since we don't have roles in DB yet
        # This will be enhanced when we add the RBAC system
        user_role = UserRole.USER

        if user_role != required_role and required_role != UserRole.USER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user

    return role_checker


async def authenticate_user_secure(
    db: AsyncSession,
    username: str,
    password: str,
    request: Request
) -> tuple[bool, Optional[User], Optional[str]]:
    """Securely authenticate user with rate limiting"""

    # Get client IP for rate limiting
    client_ip = request.client.host
    identifier = f"{client_ip}:{username}"

    # Check rate limiting
    if rate_limiter.is_rate_limited(identifier):
        return False, None, "Too many failed attempts. Please try again later."

    # Validate input
    username_valid, username_errors = UsernameValidator.validate_username(username)
    if not username_valid:
        rate_limiter.record_attempt(identifier)
        return False, None, f"Invalid username: {', '.join(username_errors)}"

    # Get user
    user = await get_user_by_username(db, username)
    if not user:
        rate_limiter.record_attempt(identifier)
        return False, None, "Invalid credentials"

    # Verify password
    if not SecurePasswordManager.verify_password(password, user.hashed_password):
        rate_limiter.record_attempt(identifier)
        return False, None, "Invalid credentials"

    # Clear rate limiting on successful login
    rate_limiter.clear_attempts(identifier)

    return True, user, None


# Initialize production configuration validation
if os.getenv("ENVIRONMENT") == "production":
    SecurityConfig.validate_production_config()