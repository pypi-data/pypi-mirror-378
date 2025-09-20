# AccessNode Production Deployment Guide

## 🚀 Production-Ready Authentication & Authorization System

This guide covers deploying AccessNode with the new secure authentication system that includes:

- ✅ **JWT Authentication** with short-lived access tokens and refresh tokens
- ✅ **Role-Based Access Control (RBAC)** with permissions system
- ✅ **Rate Limiting** and brute force protection
- ✅ **Comprehensive Security Logging** and audit trails
- ✅ **Input Validation** and password strength enforcement
- ✅ **Production Security Configuration** with security headers
- ✅ **Database Migration** support for auth tables

## 📋 Prerequisites

### System Requirements
- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for session storage)
- Nginx (recommended reverse proxy)
- SSL certificate (required for production)

### Dependencies
```bash
pip install -e ".[dev]"
# or
pip install -r requirements.txt
```

## 🔧 Configuration

### 1. Environment Setup

Create a `.env` file based on the template:

```bash
# Generate the template
python accessnode/auth/production.py

# Copy template and customize
cp .env.production.template .env
```

### 2. Critical Security Configuration

**⚠️ MANDATORY for Production:**

```bash
# Generate secure keys (32+ characters)
SECRET_KEY=your_32_character_secret_key_here
REFRESH_SECRET_KEY=your_different_32_character_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Environment
ENVIRONMENT=production
SSL_ENABLED=true
DEBUG=false

# Database (use strong password)
POSTGRES_PASSWORD=your_secure_database_password

# CORS (specify your exact domains)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
TRUSTED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 3. Validate Configuration

```bash
# Check deployment readiness
python accessnode/auth/production.py

# Should show:
# ✅ Ready for deployment: True
```

## 🗄️ Database Setup

### 1. Create Database

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres

# Create database and user
CREATE DATABASE accessnode_main;
CREATE USER accessnode_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE accessnode_main TO accessnode_user;
```

### 2. Run Migrations

```bash
# Quick migration for existing installations
python quick_migration.py

# Full migration (for new installations)
python database/migrations/001_add_auth_tables.py
```

### 3. Initialize Default Roles

The migration automatically creates:
- **admin**: Full system access
- **user**: Standard user permissions
- **read_only**: Read-only access

## 🚀 Deployment Options

### Option 1: Docker Deployment (Recommended)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main_secure:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  accessnode:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - SECRET_KEY=${SECRET_KEY}
      - POSTGRES_HOST=db
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: accessnode_main
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

### Option 2: Direct Deployment

```bash
# Install dependencies
pip install -e ".[dev]"

# Run migrations
python quick_migration.py

# Start with production config
ENVIRONMENT=production uvicorn main_secure:app --host 0.0.0.0 --port 8000
```

### Option 3: Systemd Service

```ini
# /etc/systemd/system/accessnode.service
[Unit]
Description=AccessNode API Server
After=network.target

[Service]
Type=exec
User=accessnode
Group=accessnode
WorkingDirectory=/opt/accessnode
Environment=ENVIRONMENT=production
ExecStart=/opt/accessnode/venv/bin/uvicorn main_secure:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable accessnode
sudo systemctl start accessnode
```

## 🔒 Security Configuration

### 1. Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/accessnode
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Firewall Configuration

```bash
# UFW example
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP (redirect to HTTPS)
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

### 3. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🧪 Testing Deployment

### 1. Health Check

```bash
curl https://yourdomain.com/health
# Expected: {"status":"healthy","version":"2.0.0"}
```

### 2. Authentication Test

```bash
# Run comprehensive security tests
python test_secure_auth.py https://yourdomain.com

# Should show:
# ✅ All security tests passed!
```

### 3. Load Testing (Optional)

```bash
# Install locust
pip install locust

# Create load test
# locustfile.py
from locust import HttpUser, task

class AccessNodeUser(HttpUser):
    @task
    def health_check(self):
        self.client.get("/health")

    @task
    def auth_info(self):
        self.client.get("/auth/security-info")

# Run load test
locust -f locustfile.py --host=https://yourdomain.com
```

## 📊 Monitoring & Logging

### 1. Application Logs

```bash
# View logs
journalctl -u accessnode -f

# Log rotation
sudo logrotate /etc/logrotate.d/accessnode
```

### 2. Security Monitoring

```bash
# Monitor failed login attempts
grep "login_failed" /var/log/accessnode/security.log

# Monitor rate limiting
grep "rate_limit_exceeded" /var/log/accessnode/security.log

# Monitor unauthorized access
grep "unauthorized_access" /var/log/accessnode/security.log
```

### 3. Database Monitoring

```sql
-- Monitor active sessions
SELECT user_id, COUNT(*) as active_sessions
FROM user_sessions
WHERE is_active = true
GROUP BY user_id;

-- Recent audit events
SELECT action, COUNT(*) as count, success
FROM audit_logs
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY action, success;
```

## 🔄 Backup & Recovery

### 1. Database Backup

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U postgres accessnode_main > backup_${DATE}.sql

# Encrypt backup
gpg --symmetric --cipher-algo AES256 backup_${DATE}.sql
rm backup_${DATE}.sql
```

### 2. Configuration Backup

```bash
# Backup environment and configs
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env nginx.conf
```

## 🔧 Maintenance

### 1. Regular Updates

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Run any new migrations
python database/migrations/latest_migration.py

# Restart service
sudo systemctl restart accessnode
```

### 2. Security Audits

```bash
# Monthly security check
python accessnode/auth/production.py

# Review audit logs
python -c "
from database.models import AuditLog
# Query suspicious activities
"
```

### 3. Performance Optimization

```bash
# Database optimization
psql -d accessnode_main -c "VACUUM ANALYZE;"
psql -d accessnode_main -c "REINDEX DATABASE accessnode_main;"

# Clear old audit logs (older than 90 days)
psql -d accessnode_main -c "DELETE FROM audit_logs WHERE timestamp < NOW() - INTERVAL '90 days';"
```

## 🚨 Troubleshooting

### Common Issues

**1. 500 Error on Registration**
```bash
# Check database migrations
python quick_migration.py

# Verify database connection
python -c "from database.db_setup import DATABASE_URL; print(DATABASE_URL)"
```

**2. JWT Token Issues**
```bash
# Verify secret keys are set
python -c "import os; print('SECRET_KEY set:', bool(os.getenv('SECRET_KEY')))"

# Check token expiration
python -c "from accessnode.auth.security import config; print('Token expire:', config.ACCESS_TOKEN_EXPIRE_MINUTES)"
```

**3. Rate Limiting False Positives**
```bash
# Clear rate limiting for IP
python -c "
from accessnode.auth.security import rate_limiter
rate_limiter.clear_attempts('IP_ADDRESS')
"
```

## 📞 Support & Security

### Security Contacts
- **Security Issues**: Report to admin@yourdomain.com
- **Emergency**: Use incident response procedures

### Monitoring Alerts
Set up alerts for:
- Multiple failed login attempts
- Database connection failures
- SSL certificate expiration
- High error rates

## 🎯 Performance Targets

### Expected Performance
- **Response Time**: < 200ms for auth endpoints
- **Throughput**: 1000+ requests/second
- **Availability**: 99.9% uptime
- **Security**: Zero critical vulnerabilities

### Scaling Considerations
- **Horizontal Scaling**: Add load balancer
- **Database**: Read replicas for queries
- **Caching**: Redis for session storage
- **CDN**: Static asset delivery

---

## ✅ Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL certificate installed
- [ ] Database migrations run
- [ ] Security tests passed
- [ ] Firewall configured
- [ ] Monitoring set up
- [ ] Backup procedures tested
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] Documentation updated

**🎉 Congratulations! AccessNode is now secure and production-ready!**