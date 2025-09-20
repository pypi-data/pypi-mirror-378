# Security Guidelines

This document outlines security best practices for the AccessNode project to prevent accidental exposure of sensitive information.

## 🚨 Never Commit These Files

**Immediately remove and add to `.gitignore`:**

- `token_response*.json` - JWT tokens from API responses
- `*_response.json` - Any response files that might contain tokens
- `*.token` - Token files
- `*.key` - Private keys (except `*.key.example`)
- `.env` files with real credentials
- Database dumps with real data
- Any file containing actual passwords, API keys, or tokens

## ✅ Secure Development Practices

### 1. Test Credentials

**DO NOT** hardcode passwords in test files:
```python
# ❌ NEVER do this
"password": "mypassword123"

# ✅ Use secure test credentials instead
from tests.test_credentials import TestCredentials
creds = TestCredentials.get_test_credentials()
"password": creds["password"]
```

### 2. Environment Variables

Use environment variables for all sensitive configuration:
```python
# ✅ Secure
password = os.getenv('POSTGRES_PASSWORD')

# ❌ Never hardcode
password = "mysecretpassword"
```

### 3. JWT Tokens

**Never commit JWT tokens**, even for testing:
- Use mock tokens in unit tests
- Generate temporary tokens in integration tests
- Store real tokens in environment variables only

### 4. Database Credentials

- Use test databases with non-sensitive credentials
- Never commit connection strings with real passwords
- Encrypt production database credentials

## 🔍 Before Committing

Always run these checks before committing:

```bash
# Check for potential secrets
git diff --cached | grep -i "password\|secret\|key\|token"

# Verify gitignore patterns
git status --ignored

# Run security scan (if available)
safety check
bandit -r accessnode/
```

## 🛠 If You Accidentally Commit Secrets

1. **Immediately remove the files:**
   ```bash
   git rm token_response*.json
   git commit -m "security: remove accidentally committed tokens"
   ```

2. **Add patterns to `.gitignore`:**
   ```bash
   echo "token_response*.json" >> .gitignore
   git add .gitignore
   git commit -m "security: prevent token files in future commits"
   ```

3. **For serious exposures, consider:**
   - Regenerating compromised credentials
   - Using `git filter-branch` to remove from history
   - Rotating API keys and database passwords

## 📋 Security Checklist

- [ ] No hardcoded passwords in source code
- [ ] All sensitive config uses environment variables
- [ ] Test credentials use secure generation
- [ ] `.gitignore` includes security patterns
- [ ] No JWT tokens committed to repository
- [ ] Database credentials are properly encrypted
- [ ] Regular security scans performed

## 🚨 Incident Response

If secrets are detected:

1. **Stop** - Don't continue development
2. **Remove** - Delete exposed credentials immediately
3. **Secure** - Add protection patterns to `.gitignore`
4. **Rotate** - Change any exposed credentials
5. **Review** - Audit recent commits for other exposures

## Tools for Security

Consider integrating these security tools:

- **GitGuardian** - Automatic secret detection
- **pre-commit** - Pre-commit security hooks
- **bandit** - Python security linter
- **safety** - Python dependency vulnerability scanner

---

Remember: **It's easier to prevent security issues than to fix them after exposure.**