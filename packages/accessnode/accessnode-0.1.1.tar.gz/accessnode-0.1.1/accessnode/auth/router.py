# router.py - Secure authentication routes
from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.db_setup import get_db
from database.models import User
from database.schemas import UserOut
from .security import (
    SecurityConfig,
    SecurityHeaders,
    SecureTokenManager,
    SecurePasswordManager,
    UserCreateSecure,
    TokenResponse,
    TokenData,
    TokenType,
    UserRole,
    authenticate_user_secure,
    get_current_user_secure,
    require_role,
    config
)
from .schemas import RefreshTokenRequest, ChangePasswordRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreateSecure,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with comprehensive security validation
    """
    # Add security headers
    for header, value in SecurityHeaders.get_security_headers().items():
        response.headers[header] = value

    # Check if user already exists
    existing_user = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    try:
        # Create new user with hashed password
        hashed_password = SecurePasswordManager.hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            hashed_password=hashed_password
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserOut(
            id=new_user.id,
            username=new_user.username,
            databases=[]
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        ) from e


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Secure login endpoint with rate limiting and comprehensive validation
    """
    # Add security headers
    for header, value in SecurityHeaders.get_security_headers().items():
        response.headers[header] = value

    # Authenticate user
    is_authenticated, user, error_message = await authenticate_user_secure(
        db, form_data.username, form_data.password, request
    )

    if not is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message or "Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "role": UserRole.USER  # Default role, will be enhanced with RBAC
    }

    access_token = SecureTokenManager.create_access_token(data=token_data)
    refresh_token = SecureTokenManager.create_refresh_token(data=token_data)

    # Set secure cookie for refresh token (optional)
    if config.SECURE_COOKIES:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            httponly=config.COOKIE_HTTPONLY,
            samesite=config.COOKIE_SAMESITE,
            secure=True  # Requires HTTPS in production
        )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    response: Response,
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        # Verify refresh token
        payload = SecureTokenManager.verify_token(refresh_request.refresh_token, TokenType.REFRESH)
        username = payload.get("sub")
        user_id = payload.get("user_id")

        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Verify user still exists
        user = await db.execute(select(User).where(User.id == user_id))
        user = user.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Create new tokens
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "role": UserRole.USER
        }

        new_access_token = SecureTokenManager.create_access_token(data=token_data)
        new_refresh_token = SecureTokenManager.create_refresh_token(data=token_data)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user_secure)
):
    """
    Logout user (clear cookies)
    """
    # Clear refresh token cookie
    response.delete_cookie(key="refresh_token")

    # In a production system, you would also:
    # 1. Add the JWT to a blacklist/revocation list
    # 2. Clear any server-side sessions
    # 3. Log the logout event

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information
    """
    # Fetch user with databases
    result = await db.execute(
        select(User).where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserOut(
        id=user.id,
        username=user.username,
        databases=[]  # Will be populated when we integrate with user databases
    )


@router.post("/change-password")
async def change_password(
    password_request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password
    """
    # Verify current password
    if not SecurePasswordManager.verify_password(password_request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password
    from .security import PasswordValidator
    is_valid, errors = PasswordValidator.validate_password_strength(password_request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {', '.join(errors)}"
        )

    try:
        # Update password
        current_user.hashed_password = SecurePasswordManager.hash_password(password_request.new_password)
        await db.commit()

        return {"message": "Password changed successfully"}

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.get("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_user_secure)
):
    """
    Verify if token is valid
    """
    return {
        "valid": True,
        "username": current_user.username,
        "user_id": current_user.id
    }


@router.get("/security-info")
async def get_security_info():
    """
    Get security configuration info (non-sensitive)
    """
    return {
        "password_requirements": {
            "min_length": config.PASSWORD_MIN_LENGTH,
            "require_uppercase": config.PASSWORD_REQUIRE_UPPERCASE,
            "require_lowercase": config.PASSWORD_REQUIRE_LOWERCASE,
            "require_digits": config.PASSWORD_REQUIRE_DIGITS,
            "require_symbols": config.PASSWORD_REQUIRE_SYMBOLS
        },
        "token_config": {
            "access_token_expire_minutes": config.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": config.REFRESH_TOKEN_EXPIRE_DAYS
        },
        "rate_limiting": {
            "login_attempts_limit": config.LOGIN_ATTEMPTS_LIMIT,
            "lockout_duration_minutes": config.LOGIN_LOCKOUT_DURATION_MINUTES
        }
    }


# Admin-only endpoints (for future RBAC implementation)
@router.get("/admin/users", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def list_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_secure)
):
    """
    List all users (admin only)
    """
    result = await db.execute(select(User))
    users = result.scalars().all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "created_at": "TBD"  # Add when we add timestamps to User model
        }
        for user in users
    ]


@router.delete("/admin/users/{user_id}", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_secure)
):
    """
    Delete a user (admin only)
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user_to_delete = await db.execute(select(User).where(User.id == user_id))
    user_to_delete = user_to_delete.scalar_one_or_none()

    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    try:
        await db.delete(user_to_delete)
        await db.commit()
        return {"message": f"User {user_to_delete.username} deleted successfully"}

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )