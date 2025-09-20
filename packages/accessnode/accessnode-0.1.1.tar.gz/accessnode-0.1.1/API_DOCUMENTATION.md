# AccessNode Authentication API Documentation

## 🔐 Frontend Integration Guide

This document provides everything your frontend needs to integrate with AccessNode's secure authentication system.

## 📋 Base URL

```
Development: http://localhost:8000
Production:  https://yourdomain.com
```

## 🔑 Authentication Flow

### 1. Register New User

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one symbol (!@#$%^&*(),.?\":{}|<>)

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "john_doe",
  "databases": []
}
```

**Error Responses:**
```json
// 400 - Username already exists
{
  "detail": "Username already registered"
}

// 422 - Validation error
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "password"],
      "msg": "Value error, Password validation failed: Password must contain at least one symbol",
      "input": "TestPass123"
    }
  ]
}
```

### 2. Login

**Endpoint:** `POST /auth/token`

**Request (form-encoded):**
```
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=SecurePass123!
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Error Responses:**
```json
// 401 - Invalid credentials
{
  "detail": "Invalid credentials"
}

// 401 - Rate limited
{
  "detail": "Too many failed attempts. Please try again later."
}
```

### 3. Refresh Token

**Endpoint:** `POST /auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### 4. Get Current User Info

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "databases": []
}
```

### 5. Change Password

**Endpoint:** `POST /auth/change-password`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewSecurePass456@"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

### 6. Logout

**Endpoint:** `POST /auth/logout`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

### 7. Verify Token

**Endpoint:** `GET /auth/verify-token`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "valid": true,
  "username": "john_doe",
  "user_id": 1
}
```

### 8. Get Security Info

**Endpoint:** `GET /auth/security-info`

**Response (200 OK):**
```json
{
  "password_requirements": {
    "min_length": 8,
    "require_uppercase": true,
    "require_lowercase": true,
    "require_digits": true,
    "require_symbols": true
  },
  "token_config": {
    "access_token_expire_minutes": 15,
    "refresh_token_expire_days": 7
  },
  "rate_limiting": {
    "login_attempts_limit": 5,
    "lockout_duration_minutes": 15
  }
}
```

## 🗄️ Database Management APIs

### 1. Get User Databases

**Endpoint:** `GET /user/databases`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "db_name": "my_postgres_db",
    "db_type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "username": "db_user",
    "password": "********"
  }
]
```

### 2. Connect to Database

**Endpoint:** `POST /user/databases/connect`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "db_name": "my_postgres_db",
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "username": "db_user",
  "password": "db_password"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "db_name": "my_postgres_db",
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "username": "db_user",
  "password": "********"
}
```

### 3. Get Database Details

**Endpoint:** `GET /user/databases/{db_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `include_password=true` (optional) - Include decrypted password

**Response (200 OK):**
```json
{
  "id": 1,
  "db_name": "my_postgres_db",
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "username": "db_user",
  "password": "actual_password_if_requested"
}
```

### 4. Execute Database Query

**Endpoint:** `POST /user/database/{db_id}/query`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "query": "SELECT * FROM users LIMIT 10"
}
```

**Response (200 OK):**
```json
{
  "result": [
    {"id": 1, "name": "John", "email": "john@example.com"},
    {"id": 2, "name": "Jane", "email": "jane@example.com"}
  ]
}
```

### 5. Get Database Schema

**Endpoint:** `GET /user/database/{db_id}/schema`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `table_name=users` (optional) - Get schema for specific table

**Response (200 OK):**
```json
{
  "schema": [
    {
      "table_name": "users",
      "columns": [
        {"name": "id", "type": "integer", "nullable": false},
        {"name": "username", "type": "varchar", "nullable": false},
        {"name": "email", "type": "varchar", "nullable": true}
      ]
    }
  ]
}
```

### 6. Delete Database Connection

**Endpoint:** `DELETE /user/databases/{db_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Database connection 'my_postgres_db' has been removed successfully",
  "db_name": "my_postgres_db",
  "db_type": "postgresql",
  "id": 1
}
```

## 💻 Frontend Implementation Examples

### React/JavaScript Implementation

```javascript
// auth.js - Authentication service

class AuthService {
  constructor() {
    this.baseURL = 'http://localhost:8000';
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  // Register new user
  async register(username, password) {
    const response = await fetch(`${this.baseURL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  // Login user
  async login(username, password) {
    const response = await fetch(`${this.baseURL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    const data = await response.json();

    // Store tokens
    this.accessToken = data.access_token;
    this.refreshToken = data.refresh_token;
    localStorage.setItem('access_token', this.accessToken);
    localStorage.setItem('refresh_token', this.refreshToken);

    return data;
  }

  // Get current user
  async getCurrentUser() {
    return await this.authenticatedRequest('/auth/me');
  }

  // Refresh access token
  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch(`${this.baseURL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: this.refreshToken })
    });

    if (!response.ok) {
      // Refresh failed, user needs to login again
      this.logout();
      throw new Error('Session expired. Please login again.');
    }

    const data = await response.json();

    // Update tokens
    this.accessToken = data.access_token;
    this.refreshToken = data.refresh_token;
    localStorage.setItem('access_token', this.accessToken);
    localStorage.setItem('refresh_token', this.refreshToken);

    return data;
  }

  // Change password
  async changePassword(currentPassword, newPassword) {
    return await this.authenticatedRequest('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    });
  }

  // Logout
  async logout() {
    try {
      await this.authenticatedRequest('/auth/logout', { method: 'POST' });
    } catch (error) {
      // Continue with logout even if request fails
    }

    // Clear local storage
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  // Make authenticated request with automatic token refresh
  async authenticatedRequest(endpoint, options = {}) {
    const makeRequest = async (token) => {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          ...options.headers
        }
      });

      return response;
    };

    // Try with current access token
    let response = await makeRequest(this.accessToken);

    // If unauthorized, try to refresh token
    if (response.status === 401) {
      try {
        await this.refreshAccessToken();
        response = await makeRequest(this.accessToken);
      } catch (error) {
        throw new Error('Authentication failed. Please login again.');
      }
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }

    return await response.json();
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.accessToken;
  }
}

// Export singleton instance
export const authService = new AuthService();
```

### Database Service

```javascript
// database.js - Database management service

class DatabaseService {
  constructor(authService) {
    this.authService = authService;
  }

  // Get all user databases
  async getDatabases() {
    return await this.authService.authenticatedRequest('/user/databases');
  }

  // Connect to a new database
  async connectDatabase(dbConfig) {
    return await this.authService.authenticatedRequest('/user/databases/connect', {
      method: 'POST',
      body: JSON.stringify(dbConfig)
    });
  }

  // Get database details
  async getDatabaseDetails(dbId, includePassword = false) {
    const params = includePassword ? '?include_password=true' : '';
    return await this.authService.authenticatedRequest(`/user/databases/${dbId}${params}`);
  }

  // Execute query
  async executeQuery(dbId, query) {
    return await this.authService.authenticatedRequest(`/user/database/${dbId}/query`, {
      method: 'POST',
      body: JSON.stringify({ query })
    });
  }

  // Get database schema
  async getSchema(dbId, tableName = null) {
    const params = tableName ? `?table_name=${tableName}` : '';
    return await this.authService.authenticatedRequest(`/user/database/${dbId}/schema${params}`);
  }

  // Delete database connection
  async deleteDatabase(dbId) {
    return await this.authService.authenticatedRequest(`/user/databases/${dbId}`, {
      method: 'DELETE'
    });
  }
}

export const databaseService = new DatabaseService(authService);
```

### React Hook for Authentication

```javascript
// useAuth.js - React hook for authentication

import { useState, useEffect, useContext, createContext } from 'react';
import { authService } from './auth';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if user is already authenticated
    if (authService.isAuthenticated()) {
      authService.getCurrentUser()
        .then(setUser)
        .catch(() => {
          // Token might be expired, clear it
          authService.logout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    try {
      setError(null);
      setLoading(true);

      await authService.login(username, password);
      const user = await authService.getCurrentUser();
      setUser(user);

      return { success: true };
    } catch (error) {
      setError(error.message);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const register = async (username, password) => {
    try {
      setError(null);
      setLoading(true);

      await authService.register(username, password);
      // Auto-login after registration
      return await login(username, password);
    } catch (error) {
      setError(error.message);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } finally {
      setUser(null);
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      setError(null);
      await authService.changePassword(currentPassword, newPassword);
      return { success: true };
    } catch (error) {
      setError(error.message);
      return { success: false, error: error.message };
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    changePassword,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

### Protected Route Component

```javascript
// ProtectedRoute.js - Component to protect routes

import { useAuth } from './useAuth';
import { Navigate } from 'react-router-dom';

export const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};
```

### Login Component Example

```javascript
// LoginForm.js - Login form component

import { useState } from 'react';
import { useAuth } from './useAuth';
import { useNavigate } from 'react-router-dom';

export const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const result = await login(username, password);
    if (result.success) {
      navigate('/dashboard');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Username:</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>

      <div>
        <label>Password:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>

      {error && <div className="error">{error}</div>}

      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};
```

## 🔒 Security Best Practices

### 1. Token Management

```javascript
// Store tokens securely
// For web apps: localStorage (shown above)
// For mobile apps: Secure storage (Keychain/Keystore)

// Always check token expiration
const isTokenExpired = (token) => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
};
```

### 2. Request Interceptors

```javascript
// Axios interceptor example
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

// Request interceptor to add auth header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try to refresh token
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await fetch('/auth/refresh', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: refreshToken })
        });

        if (response.ok) {
          const data = await response.json();
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);

          // Retry original request
          error.config.headers.Authorization = `Bearer ${data.access_token}`;
          return api.request(error.config);
        }
      } catch {
        // Refresh failed, redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

### 3. Error Handling

```javascript
// Comprehensive error handling
const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;

    switch (status) {
      case 400:
        return `Validation error: ${data.detail}`;
      case 401:
        return 'Please login to continue';
      case 403:
        return 'You do not have permission to perform this action';
      case 404:
        return 'Resource not found';
      case 422:
        return `Validation failed: ${data.detail[0]?.msg || data.detail}`;
      case 429:
        return 'Too many requests. Please try again later';
      case 500:
        return 'Server error. Please try again later';
      default:
        return 'An unexpected error occurred';
    }
  } else if (error.request) {
    // Network error
    return 'Network error. Please check your connection';
  } else {
    // Other error
    return error.message || 'An error occurred';
  }
};
```

## 🚨 Rate Limiting

The API implements rate limiting on authentication endpoints:

- **Login attempts:** 5 attempts per IP per 15 minutes
- **When exceeded:** Account locked for 15 minutes
- **Response:** HTTP 401 with rate limit message

### Frontend Handling

```javascript
const handleRateLimit = (error) => {
  if (error.message.includes('too many') || error.message.includes('rate')) {
    // Show user-friendly message
    showMessage('Too many failed attempts. Please try again in 15 minutes.');

    // Optionally disable login form temporarily
    disableLoginForm(15 * 60 * 1000); // 15 minutes
  }
};
```

## ✅ Health Check

Monitor your authentication system:

```javascript
// Health check endpoint
const checkSystemHealth = async () => {
  const response = await fetch('/health');
  return await response.json();
};

// Security configuration check
const getSecurityConfig = async () => {
  const response = await fetch('/auth/security-info');
  return await response.json();
};
```

This comprehensive API documentation provides everything your frontend needs to integrate with AccessNode's secure authentication system. The implementation examples show best practices for React/JavaScript, but the same patterns apply to other frameworks.

## 🎯 Quick Start Checklist

- [ ] Implement authentication service with token management
- [ ] Add automatic token refresh logic
- [ ] Create protected route components
- [ ] Handle authentication errors properly
- [ ] Implement rate limiting feedback
- [ ] Add password validation on frontend
- [ ] Test all authentication flows
- [ ] Implement logout functionality
- [ ] Add loading states for better UX