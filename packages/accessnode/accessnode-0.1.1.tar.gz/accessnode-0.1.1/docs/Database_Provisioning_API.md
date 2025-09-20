# Database Provisioning API Documentation

This document provides comprehensive frontend integration guidelines for the AccessNode Database Provisioning API.

## Overview

The Database Provisioning API allows users to automatically create and manage database instances directly through the AccessNode platform. It supports SQLite, PostgreSQL, MySQL, and MongoDB with automatic setup and configuration.

## Base URL

All provisioning endpoints are prefixed with `/provision`

```
Base URL: https://your-api-domain.com/provision
```

## Authentication

All endpoints require Bearer token authentication:

```javascript
headers: {
  'Authorization': `Bearer ${userToken}`,
  'Content-Type': 'application/json'
}
```

## API Endpoints

### 1. Get Supported Database Types

**GET** `/provision/supported`

Returns all supported database types and their requirements.

**Request:**
```javascript
const response = await fetch('/provision/supported', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

**Response:**
```json
{
  "supported_types": [
    {
      "type": "sqlite",
      "name": "SQLite",
      "description": "File-based database, instant setup, perfect for development",
      "requirements": "None",
      "provisioning_time": "< 1 second"
    },
    {
      "type": "postgresql",
      "name": "PostgreSQL",
      "description": "Advanced open-source relational database",
      "requirements": "Docker",
      "provisioning_time": "10-30 seconds"
    },
    {
      "type": "mysql",
      "name": "MySQL",
      "description": "Popular open-source relational database",
      "requirements": "Docker",
      "provisioning_time": "15-45 seconds"
    },
    {
      "type": "mongodb",
      "name": "MongoDB",
      "description": "Document-oriented NoSQL database",
      "requirements": "Docker",
      "provisioning_time": "10-30 seconds"
    }
  ],
  "docker_required_for": ["postgresql", "mysql", "mongodb"],
  "instant_provisioning": ["sqlite"]
}
```

### 2. Provision New Database

**POST** `/provision`

Creates a new database instance and returns connection details.

**Request Body:**
```typescript
interface DatabaseProvisionRequest {
  db_type: 'sqlite' | 'postgresql' | 'mysql' | 'mongodb';
  db_name: string; // 1-50 characters
  description?: string; // Optional description
}
```

**Example Request:**
```javascript
const provisionDatabase = async (dbType, dbName, description = '') => {
  const response = await fetch('/provision/provision', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      db_type: dbType,
      db_name: dbName,
      description: description
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return response.json();
};
```

**Response:**
```typescript
interface ProvisionedDatabaseResponse {
  id: number;
  db_type: string;
  db_name: string;
  host: string;
  port?: number;
  username?: string;
  password: string; // Always "********" for security
  connection_string: string;
  status: string;
  message: string;
  container_id?: string; // For Docker containers
  database_path?: string; // For SQLite files
}
```

**Example Response:**
```json
{
  "id": 123,
  "db_type": "postgresql",
  "db_name": "my_test_db",
  "host": "localhost",
  "port": 5433,
  "username": "user_a1b2c3d4",
  "password": "********",
  "connection_string": "postgresql://user_a1b2c3d4:password@localhost:5433/my_test_db",
  "status": "success",
  "message": "PostgreSQL database provisioned successfully",
  "container_id": "postgres_my_test_db_123"
}
```

### 3. Deprovision Database

**DELETE** `/provision/provision/{database_id}`

Removes a provisioned database and cleans up all resources.

**Example Request:**
```javascript
const deprovisionDatabase = async (databaseId) => {
  const response = await fetch(`/provision/provision/${databaseId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return response.json();
};
```

**Response:**
```json
{
  "message": "Database 'my_test_db' has been successfully deprovisioned",
  "db_name": "my_test_db",
  "db_type": "postgresql"
}
```

### 4. Get Quick Start Examples

**GET** `/provision/quick-examples`

Returns code examples for connecting to provisioned databases.

**Response:** Code examples for Python, connection strings, etc.

## Frontend Implementation Guide

### React Component Example

```typescript
import React, { useState, useEffect } from 'react';

interface DatabaseType {
  type: string;
  name: string;
  description: string;
  requirements: string;
  provisioning_time: string;
}

interface ProvisionedDatabase {
  id: number;
  db_type: string;
  db_name: string;
  host: string;
  port?: number;
  username?: string;
  connection_string: string;
  status: string;
  message: string;
}

const DatabaseProvisioningComponent: React.FC = () => {
  const [supportedTypes, setSupportedTypes] = useState<DatabaseType[]>([]);
  const [isProvisioning, setIsProvisioning] = useState(false);
  const [provisionedDbs, setProvisionedDbs] = useState<ProvisionedDatabase[]>([]);

  // Load supported database types
  useEffect(() => {
    const loadSupportedTypes = async () => {
      try {
        const response = await fetch('/provision/supported', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setSupportedTypes(data.supported_types);
      } catch (error) {
        console.error('Failed to load supported types:', error);
      }
    };

    loadSupportedTypes();
  }, []);

  // Provision new database
  const handleProvision = async (dbType: string, dbName: string) => {
    setIsProvisioning(true);

    try {
      const response = await fetch('/provision/provision', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          db_type: dbType,
          db_name: dbName
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
      }

      const newDb = await response.json();
      setProvisionedDbs([...provisionedDbs, newDb]);

      // Show success message
      alert(`Database "${dbName}" provisioned successfully!`);

    } catch (error) {
      alert(`Failed to provision database: ${error.message}`);
    } finally {
      setIsProvisioning(false);
    }
  };

  // Deprovision database
  const handleDeprovision = async (databaseId: number, dbName: string) => {
    if (!confirm(`Are you sure you want to delete "${dbName}"? This cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch(`/provision/provision/${databaseId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
      }

      // Remove from state
      setProvisionedDbs(provisionedDbs.filter(db => db.id !== databaseId));
      alert(`Database "${dbName}" has been deprovisioned.`);

    } catch (error) {
      alert(`Failed to deprovision database: ${error.message}`);
    }
  };

  return (
    <div className="database-provisioning">
      <h2>Database Provisioning</h2>

      {/* Database Type Selection */}
      <div className="provision-form">
        <h3>Create New Database</h3>
        {supportedTypes.map(type => (
          <div key={type.type} className="db-type-card">
            <h4>{type.name}</h4>
            <p>{type.description}</p>
            <p><strong>Requirements:</strong> {type.requirements}</p>
            <p><strong>Setup Time:</strong> {type.provisioning_time}</p>
            <button
              onClick={() => {
                const dbName = prompt(`Enter name for ${type.name} database:`);
                if (dbName) {
                  handleProvision(type.type, dbName);
                }
              }}
              disabled={isProvisioning}
            >
              {isProvisioning ? 'Provisioning...' : `Create ${type.name}`}
            </button>
          </div>
        ))}
      </div>

      {/* Provisioned Databases List */}
      <div className="provisioned-databases">
        <h3>Your Provisioned Databases</h3>
        {provisionedDbs.map(db => (
          <div key={db.id} className="db-card">
            <h4>{db.db_name} ({db.db_type})</h4>
            <p><strong>Host:</strong> {db.host}</p>
            {db.port && <p><strong>Port:</strong> {db.port}</p>}
            {db.username && <p><strong>Username:</strong> {db.username}</p>}
            <p><strong>Status:</strong> {db.status}</p>
            <details>
              <summary>Connection Details</summary>
              <code>{db.connection_string}</code>
            </details>
            <button
              onClick={() => handleDeprovision(db.id, db.db_name)}
              className="danger-button"
            >
              Delete Database
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DatabaseProvisioningComponent;
```

## Error Handling

### Common Error Responses

```typescript
interface ApiError {
  detail: string;
  status_code: number;
}
```

**400 Bad Request:**
- Database name already exists
- Invalid database type
- Docker not available (for containerized databases)

**401 Unauthorized:**
- Invalid or expired token

**500 Internal Server Error:**
- Provisioning service failure
- Docker container creation failed

### Error Handling Best Practices

```javascript
const handleApiError = (error) => {
  if (error.status === 400) {
    // Show user-friendly validation message
    showUserMessage(error.detail);
  } else if (error.status === 401) {
    // Redirect to login
    redirectToLogin();
  } else {
    // Show generic error
    showUserMessage('An unexpected error occurred. Please try again.');
  }
};
```

## UI/UX Recommendations

### Database Type Cards
Display each database type with:
- Icon for the database type
- Name and description
- Requirements (Docker/None)
- Estimated provisioning time
- "Create" button

### Provisioning Status
- Show loading spinner during provisioning
- Display progress messages for Docker-based databases
- Show success/error notifications

### Database Management
- List view of provisioned databases
- Connection details (collapsible)
- Quick actions: Connect, Delete, View Schema
- Status indicators (Running, Stopped, Error)

### Form Validation
```javascript
const validateDatabaseName = (name) => {
  if (!name || name.length < 1) {
    return 'Database name is required';
  }
  if (name.length > 50) {
    return 'Database name must be 50 characters or less';
  }
  if (!/^[a-zA-Z0-9_-]+$/.test(name)) {
    return 'Database name can only contain letters, numbers, hyphens, and underscores';
  }
  return null;
};
```

## Integration with Existing Database List

The provisioned databases will automatically appear in the main database list endpoint (`/user/databases`). You can distinguish provisioned databases by checking if they have certain patterns:

- **Host**: `localhost` for provisioned databases
- **Generated usernames**: Follow pattern `user_xxxxxxxx`
- **Port ranges**: PostgreSQL (5432+), MySQL (3306+), MongoDB (27017+)

## Security Considerations

1. **Password Security**: Real passwords are never returned in API responses
2. **Access Control**: Users can only manage their own provisioned databases
3. **Resource Limits**: Consider implementing quotas for database provisioning
4. **Cleanup**: Ensure proper cleanup of resources when deprovisioning

## Testing

### Mock Responses for Development

```javascript
const mockSupportedTypes = {
  supported_types: [
    {
      type: "sqlite",
      name: "SQLite",
      description: "File-based database, instant setup",
      requirements: "None",
      provisioning_time: "< 1 second"
    }
    // ... other types
  ]
};

const mockProvisionResponse = {
  id: 123,
  db_type: "sqlite",
  db_name: "test_db",
  host: "localhost",
  connection_string: "sqlite:///path/to/test_db.db",
  status: "success",
  message: "SQLite database provisioned successfully",
  database_path: "/path/to/test_db.db"
};
```

This documentation provides everything needed to implement the database provisioning feature in your frontend application.