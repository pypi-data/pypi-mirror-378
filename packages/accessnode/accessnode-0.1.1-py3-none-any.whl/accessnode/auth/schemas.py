# schemas.py - Request/Response models for auth endpoints
from pydantic import BaseModel, Field
from typing import Optional


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh"""
    refresh_token: str = Field(..., description="Refresh token to exchange for new access token")


class ChangePasswordRequest(BaseModel):
    """Request model for password change"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")