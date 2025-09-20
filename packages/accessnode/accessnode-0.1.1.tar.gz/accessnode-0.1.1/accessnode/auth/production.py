# production.py - Production environment security configuration
import os
import secrets
from typing import List, Dict, Any
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware


class ProductionSecurityConfig:
    """Production security configuration and middleware"""

    @staticmethod
    def validate_environment() -> Dict[str, Any]:
        """Validate production environment configuration"""
        issues = []
        warnings = []
        config_status = {}

        # Critical security checks
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            issues.append("SECRET_KEY environment variable not set")
        elif len(secret_key) < 32:
            issues.append("SECRET_KEY too short (minimum 32 characters)")
        elif secret_key in ["keykey", "secret", "dev-key"]:
            issues.append("SECRET_KEY is using default/weak value")

        refresh_secret = os.getenv("REFRESH_SECRET_KEY")
        if not refresh_secret:
            warnings.append("REFRESH_SECRET_KEY not set, will use generated key")
        elif refresh_secret == secret_key:
            issues.append("REFRESH_SECRET_KEY should be different from SECRET_KEY")

        # Database security
        postgres_password = os.getenv("POSTGRES_PASSWORD")
        if not postgres_password:
            issues.append("POSTGRES_PASSWORD not set")
        elif len(postgres_password) < 12:
            warnings.append("POSTGRES_PASSWORD is short (recommend 12+ characters)")

        # SSL/TLS configuration
        ssl_enabled = os.getenv("SSL_ENABLED", "false").lower() == "true"
        if not ssl_enabled:
            warnings.append("SSL not enabled - required for production")

        # CORS configuration
        allowed_origins = os.getenv("ALLOWED_ORIGINS")
        if not allowed_origins:
            issues.append("ALLOWED_ORIGINS not configured")
        elif "*" in allowed_origins:
            issues.append("CORS allows all origins (*) - security risk")

        # Session configuration
        session_timeout = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
        if session_timeout > 480:  # 8 hours
            warnings.append("Session timeout is very long (> 8 hours)")

        config_status = {
            "secret_key_configured": bool(secret_key and len(secret_key) >= 32),
            "database_password_set": bool(postgres_password),
            "ssl_enabled": ssl_enabled,
            "cors_properly_configured": bool(allowed_origins and "*" not in allowed_origins),
            "session_timeout_reasonable": session_timeout <= 480
        }

        return {
            "issues": issues,
            "warnings": warnings,
            "config_status": config_status,
            "is_production_ready": len(issues) == 0
        }

    @staticmethod
    def generate_secure_keys() -> Dict[str, str]:
        """Generate secure keys for production use"""
        return {
            "SECRET_KEY": secrets.token_urlsafe(32),
            "REFRESH_SECRET_KEY": secrets.token_urlsafe(32),
            "ENCRYPTION_KEY": secrets.token_urlsafe(32)
        }

    @staticmethod
    def get_production_cors_config() -> Dict[str, Any]:
        """Get production CORS configuration"""
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
        allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

        if not allowed_origins:
            raise ValueError("ALLOWED_ORIGINS must be configured for production")

        return {
            "allow_origins": allowed_origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Requested-With",
                "X-CSRF-Token"
            ],
            "expose_headers": ["X-Total-Count"],
            "max_age": 86400  # 24 hours
        }

    @staticmethod
    def get_trusted_hosts() -> List[str]:
        """Get list of trusted hosts"""
        hosts = os.getenv("TRUSTED_HOSTS", "").split(",")
        hosts = [host.strip() for host in hosts if host.strip()]

        if not hosts:
            # Default to localhost for development
            hosts = ["localhost", "127.0.0.1"]

        return hosts

    @staticmethod
    def configure_security_middleware(app: FastAPI) -> None:
        """Configure production security middleware"""

        # Trusted Host Middleware - must be first
        trusted_hosts = ProductionSecurityConfig.get_trusted_hosts()
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=trusted_hosts
        )

        # CORS Middleware
        cors_config = ProductionSecurityConfig.get_production_cors_config()
        app.add_middleware(CORSMiddleware, **cors_config)

        # GZip Middleware for performance
        app.add_middleware(GZipMiddleware, minimum_size=1000)

        # Custom Security Headers Middleware
        @app.middleware("http")
        async def add_security_headers(request, call_next):
            response = await call_next(request)

            # Security headers
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Permissions-Policy": (
                    "camera=(), microphone=(), geolocation=(), "
                    "payment=(), usb=(), magnetometer=(), accelerometer=(), "
                    "gyroscope=(), speaker=(), vibrate=(), fullscreen=(self)"
                ),
                "Content-Security-Policy": (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data: https:; "
                    "connect-src 'self'; "
                    "font-src 'self'; "
                    "object-src 'none'; "
                    "media-src 'self'; "
                    "frame-src 'none';"
                )
            }

            # Add HSTS only if HTTPS is enabled
            if os.getenv("SSL_ENABLED", "false").lower() == "true":
                security_headers["Strict-Transport-Security"] = (
                    "max-age=31536000; includeSubDomains; preload"
                )

            # Apply headers
            for header_name, header_value in security_headers.items():
                response.headers[header_name] = header_value

            return response

        # Rate limiting middleware (placeholder for production rate limiter)
        @app.middleware("http")
        async def rate_limiting_middleware(request, call_next):
            # In production, implement with Redis-based rate limiting
            # For now, just pass through
            response = await call_next(request)
            return response


class EnvironmentValidator:
    """Validate environment for different deployment scenarios"""

    @staticmethod
    def create_env_template() -> str:
        """Create template .env file for production"""
        template = """# Production Environment Configuration

# Database Configuration
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_HOST=your_database_host
POSTGRES_PORT=5432
POSTGRES_DB=accessnode_main

# Security Keys (Generate new ones for production!)
SECRET_KEY=your_32_character_secret_key_here
REFRESH_SECRET_KEY=your_different_32_character_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Application Configuration
ENVIRONMENT=production
SSL_ENABLED=true
DEBUG=false

# CORS Configuration (specify your frontend domains)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Trusted hosts
TRUSTED_HOSTS=yourdomain.com,www.yourdomain.com

# Session Configuration
SESSION_TIMEOUT_MINUTES=60
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
LOGIN_ATTEMPTS_LIMIT=5
LOGIN_LOCKOUT_DURATION_MINUTES=15

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/accessnode/security.log

# Redis Configuration (for session storage and rate limiting)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Email Configuration (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Monitoring and Alerting
SENTRY_DSN=your_sentry_dsn_here
ALERT_EMAIL=admin@yourdomain.com

# Backup Configuration
BACKUP_ENCRYPTION_KEY=your_backup_encryption_key
BACKUP_S3_BUCKET=your-backup-bucket
"""
        return template

    @staticmethod
    def validate_deployment_readiness() -> Dict[str, Any]:
        """Comprehensive deployment readiness check"""
        checks = {}

        # Environment configuration
        config_check = ProductionSecurityConfig.validate_environment()
        checks["environment_config"] = config_check

        # File permissions and paths
        checks["file_permissions"] = EnvironmentValidator._check_file_permissions()

        # Network security
        checks["network_security"] = EnvironmentValidator._check_network_security()

        # Dependencies
        checks["dependencies"] = EnvironmentValidator._check_dependencies()

        # Overall readiness
        checks["deployment_ready"] = all([
            config_check["is_production_ready"],
            checks["file_permissions"]["secure"],
            checks["network_security"]["secure"],
            checks["dependencies"]["all_installed"]
        ])

        return checks

    @staticmethod
    def _check_file_permissions() -> Dict[str, Any]:
        """Check file and directory permissions"""
        checks = {
            "secure": True,
            "issues": []
        }

        # Check if .env file has proper permissions
        env_file = Path(".env")
        if env_file.exists():
            stat = env_file.stat()
            # Check if readable by others (should be 600 or 640)
            if stat.st_mode & 0o044:  # Others can read
                checks["secure"] = False
                checks["issues"].append(".env file is readable by others")

        # Check log directory permissions
        log_dir = Path("/var/log/accessnode")
        if log_dir.exists():
            stat = log_dir.stat()
            if stat.st_mode & 0o022:  # Others can write
                checks["secure"] = False
                checks["issues"].append("Log directory is writable by others")

        return checks

    @staticmethod
    def _check_network_security() -> Dict[str, Any]:
        """Check network security configuration"""
        return {
            "secure": True,
            "ssl_enabled": os.getenv("SSL_ENABLED", "false").lower() == "true",
            "firewall_configured": "unknown",  # Would check with system commands
            "reverse_proxy": "unknown"  # Would detect nginx/apache
        }

    @staticmethod
    def _check_dependencies() -> Dict[str, Any]:
        """Check required dependencies"""
        required_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "asyncpg",
            "python-jose",
            "passlib",
            "bcrypt",
            "cryptography"
        ]

        installed = []
        missing = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                installed.append(package)
            except ImportError:
                missing.append(package)

        return {
            "all_installed": len(missing) == 0,
            "installed": installed,
            "missing": missing
        }


def create_production_env_file():
    """Create a production environment file template"""
    env_content = EnvironmentValidator.create_env_template()

    # Generate secure keys
    keys = ProductionSecurityConfig.generate_secure_keys()

    # Replace placeholders
    for key, value in keys.items():
        env_content = env_content.replace(f"your_{key.lower()}_here", value)

    # Write to .env.production template
    with open(".env.production.template", "w") as f:
        f.write(env_content)

    print("Production environment template created: .env.production.template")
    print("Please customize the values and rename to .env for production use.")


if __name__ == "__main__":
    # Run deployment readiness check
    readiness = EnvironmentValidator.validate_deployment_readiness()
    print("Deployment Readiness Check:")
    print(f"Ready for deployment: {readiness['deployment_ready']}")

    if not readiness['deployment_ready']:
        print("\nIssues found:")
        for check_name, check_result in readiness.items():
            if isinstance(check_result, dict) and "issues" in check_result:
                for issue in check_result["issues"]:
                    print(f"  - {issue}")

    # Create production env template
    create_production_env_file()