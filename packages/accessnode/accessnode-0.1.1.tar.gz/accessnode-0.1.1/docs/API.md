# AccessNode API Documentation

This document provides detailed information about the AccessNode REST API endpoints.

## Base URL
```
http://localhost:8000
```

## Authentication

AccessNode uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication Endpoints

#### Register User
```http
POST /user/register
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "id": "integer",
  "username": "string",
  "databases": []
}
```

**Status Codes:**
- `200` - User created successfully
- `400` - Username already registered
- `500` - Failed to register user

#### Login / Get Token
```http
POST /user/token
```

**Request Body (form-data):**
```
username: string
password: string
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200` - Authentication successful
- `401` - Invalid credentials

### Database Management Endpoints

#### Setup Database Connection
```http
POST /user/databases/setup
```

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "string",
  "db_type": "postgres|mysql|mongodb|sqlite",
  "host": "string",
  "port": "integer",
  "database_name": "string",
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "id": "integer",
  "name": "string",
  "db_type": "string",
  "host": "string",
  "port": "integer",
  "database_name": "string",
  "username": "string"
}
```

**Status Codes:**
- `200` - Database connection created successfully
- `400` - Database connection failed or invalid parameters
- `401` - Unauthorized
- `500` - Internal server error

#### List User Databases
```http
GET /user/databases
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "integer",
    "name": "string",
    "db_type": "string",
    "host": "string",
    "port": "integer",
    "database_name": "string",
    "username": "string"
  }
]
```

#### Delete Database Connection
```http
DELETE /user/databases/{db_id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Parameters:**
- `db_id` (path) - Database connection ID

**Status Codes:**
- `200` - Database connection deleted
- `404` - Database connection not found
- `401` - Unauthorized

### Query Execution Endpoints

#### Execute Query
```http
POST /user/database/{db_id}/query
```

**Headers:**
```
Authorization: Bearer <token>
```

**Parameters:**
- `db_id` (path) - Database connection ID

**Request Body:**
```json
{
  "query": "string",
  "parameters": {}
}
```

**Response:**
```json
{
  "results": [
    {
      "column1": "value1",
      "column2": "value2"
    }
  ],
  "row_count": "integer",
  "execution_time": "float"
}
```

**Status Codes:**
- `200` - Query executed successfully
- `400` - Invalid query or parameters
- `401` - Unauthorized
- `404` - Database connection not found
- `500` - Query execution error

#### List Tables
```http
GET /user/database/{db_id}/tables
```

**Headers:**
```
Authorization: Bearer <token>
```

**Parameters:**
- `db_id` (path) - Database connection ID

**Response:**
```json
{
  "tables": [
    {
      "name": "string",
      "schema": "string",
      "type": "table|view"
    }
  ]
}
```

## Error Responses

All error responses follow this format:
```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

- `400 Bad Request` - Invalid request parameters or data
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server-side error

## Rate Limiting

API endpoints may be rate-limited. When rate limits are exceeded, the API returns:
- Status Code: `429 Too Many Requests`
- Headers include rate limit information

## Examples

### Complete Authentication Flow

1. **Register a user:**
```bash
curl -X POST "http://localhost:8000/user/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser", "password": "mypassword"}'
```

2. **Get access token:**
```bash
curl -X POST "http://localhost:8000/user/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=myuser&password=mypassword"
```

3. **Store the token for subsequent requests:**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Database Operations

1. **Setup PostgreSQL connection:**
```bash
curl -X POST "http://localhost:8000/user/databases/setup" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My PostgreSQL DB",
    "db_type": "postgres",
    "host": "localhost",
    "port": 5432,
    "database_name": "myapp",
    "username": "dbuser",
    "password": "dbpass"
  }'
```

2. **Execute a query:**
```bash
curl -X POST "http://localhost:8000/user/database/1/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM users WHERE created_at > $1",
    "parameters": {"1": "2023-01-01"}
  }'
```

3. **List tables:**
```bash
curl -X GET "http://localhost:8000/user/database/1/tables" \
  -H "Authorization: Bearer $TOKEN"
```

## Interactive Documentation

When the server is running, visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

## WebSocket Support

AccessNode may support WebSocket connections for real-time database operations. Check the interactive documentation for WebSocket endpoint details.