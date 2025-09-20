# audit.py - Security logging and monitoring
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models import User, AuditLog


class AuditAction(str, Enum):
    """Audit action types"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGIN_BLOCKED = "login_blocked"
    LOGOUT = "logout"
    REGISTER = "register"
    PASSWORD_CHANGE = "password_change"
    TOKEN_REFRESH = "token_refresh"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"

    # Database operations
    DATABASE_CREATE = "database_create"
    DATABASE_DELETE = "database_delete"
    DATABASE_ACCESS = "database_access"
    QUERY_EXECUTE = "query_execute"

    # Admin operations
    USER_CREATE = "user_create"
    USER_DELETE = "user_delete"
    ROLE_ASSIGN = "role_assign"
    ROLE_REVOKE = "role_revoke"


class SecurityLogger:
    """Enhanced security logging with structured logging"""

    def __init__(self):
        # Create security logger
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)

        # Create handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_security_event(
        self,
        action: AuditAction,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
        risk_level: str = "low"
    ):
        """Log security event with structured data"""

        log_data = {
            "action": action,
            "user_id": user_id,
            "username": username,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "resource": resource,
            "resource_id": resource_id,
            "success": success,
            "details": details or {},
            "risk_level": risk_level,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Log at appropriate level based on risk
        if risk_level == "critical":
            self.logger.critical(f"CRITICAL_SECURITY_EVENT: {json.dumps(log_data)}")
        elif risk_level == "high":
            self.logger.error(f"HIGH_RISK_EVENT: {json.dumps(log_data)}")
        elif risk_level == "medium":
            self.logger.warning(f"MEDIUM_RISK_EVENT: {json.dumps(log_data)}")
        else:
            self.logger.info(f"SECURITY_EVENT: {json.dumps(log_data)}")

    def log_authentication_attempt(
        self,
        username: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        failure_reason: Optional[str] = None
    ):
        """Log authentication attempts"""
        action = AuditAction.LOGIN_SUCCESS if success else AuditAction.LOGIN_FAILED
        risk_level = "low" if success else "medium"

        details = {}
        if failure_reason:
            details["failure_reason"] = failure_reason

        self.log_security_event(
            action=action,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details,
            risk_level=risk_level
        )

    def log_rate_limit_exceeded(
        self,
        username: str,
        ip_address: str,
        user_agent: str
    ):
        """Log rate limit violations"""
        self.log_security_event(
            action=AuditAction.LOGIN_BLOCKED,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            details={"reason": "rate_limit_exceeded"},
            risk_level="high"
        )

    def log_unauthorized_access(
        self,
        user_id: Optional[int],
        username: Optional[str],
        ip_address: str,
        user_agent: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log unauthorized access attempts"""
        self.log_security_event(
            action=AuditAction.UNAUTHORIZED_ACCESS,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            success=False,
            details=details,
            risk_level="high"
        )


class AuditManager:
    """Database audit logging"""

    def __init__(self):
        self.security_logger = SecurityLogger()

    async def log_audit_event(
        self,
        db: AsyncSession,
        action: AuditAction,
        user_id: Optional[int] = None,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ):
        """Log audit event to database and security log"""

        try:
            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource=resource,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=json.dumps(details) if details else None,
                success=success
            )

            db.add(audit_log)
            await db.commit()

            # Also log to security logger
            username = None
            if user_id:
                user_result = await db.execute(select(User).where(User.id == user_id))
                user = user_result.scalar_one_or_none()
                if user:
                    username = user.username

            # Determine risk level
            risk_level = self._determine_risk_level(action, success)

            self.security_logger.log_security_event(
                action=action,
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                resource=resource,
                resource_id=resource_id,
                success=success,
                details=details,
                risk_level=risk_level
            )

        except Exception as e:
            # Fallback to security logger only
            self.security_logger.log_security_event(
                action=action,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                resource=resource,
                resource_id=resource_id,
                success=success,
                details={"error": str(e), **(details or {})},
                risk_level="medium"
            )

    def _determine_risk_level(self, action: AuditAction, success: bool) -> str:
        """Determine risk level based on action and success"""

        if not success:
            high_risk_actions = {
                AuditAction.LOGIN_FAILED,
                AuditAction.UNAUTHORIZED_ACCESS,
                AuditAction.PERMISSION_DENIED
            }
            if action in high_risk_actions:
                return "high"
            return "medium"

        critical_actions = {
            AuditAction.USER_DELETE,
            AuditAction.DATABASE_DELETE
        }

        high_risk_actions = {
            AuditAction.PASSWORD_CHANGE,
            AuditAction.ROLE_ASSIGN,
            AuditAction.ROLE_REVOKE,
            AuditAction.USER_CREATE
        }

        if action in critical_actions:
            return "critical"
        elif action in high_risk_actions:
            return "high"
        else:
            return "low"

    async def log_login_attempt(
        self,
        db: AsyncSession,
        username: str,
        request: Request,
        success: bool,
        user_id: Optional[int] = None,
        failure_reason: Optional[str] = None
    ):
        """Convenience method for login attempts"""

        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")

        details = {}
        if failure_reason:
            details["failure_reason"] = failure_reason

        action = AuditAction.LOGIN_SUCCESS if success else AuditAction.LOGIN_FAILED

        await self.log_audit_event(
            db=db,
            action=action,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            success=success
        )

    async def log_database_operation(
        self,
        db: AsyncSession,
        action: AuditAction,
        user_id: int,
        database_name: str,
        request: Request,
        query: Optional[str] = None,
        success: bool = True
    ):
        """Log database operations"""

        details = {}
        if query:
            # Log only first 200 chars of query for security
            details["query"] = query[:200] + "..." if len(query) > 200 else query

        await self.log_audit_event(
            db=db,
            action=action,
            user_id=user_id,
            resource="database",
            resource_id=database_name,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            details=details,
            success=success
        )


class SecurityMonitor:
    """Real-time security monitoring and alerting"""

    def __init__(self):
        self.failed_attempts = {}
        self.suspicious_ips = set()

    def check_suspicious_activity(
        self,
        ip_address: str,
        user_agent: str,
        action: AuditAction
    ) -> tuple[bool, str]:
        """Check for suspicious activity patterns"""

        # Check for suspicious user agents
        suspicious_agents = [
            "curl", "wget", "python-requests", "bot", "scanner", "sqlmap"
        ]

        if any(agent in user_agent.lower() for agent in suspicious_agents):
            return True, "Suspicious user agent detected"

        # Check for rapid requests from same IP
        # This would be enhanced with Redis in production

        # Check for known malicious patterns
        if self._is_suspicious_ip(ip_address):
            return True, "IP address flagged as suspicious"

        return False, ""

    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP is in suspicious list"""
        # In production, this would check against:
        # - Known bad IP databases
        # - Geo-location anomalies
        # - VPN/proxy detection
        return ip_address in self.suspicious_ips

    def flag_ip_as_suspicious(self, ip_address: str):
        """Flag an IP as suspicious"""
        self.suspicious_ips.add(ip_address)


# Global instances
audit_manager = AuditManager()
security_monitor = SecurityMonitor()
security_logger = SecurityLogger()