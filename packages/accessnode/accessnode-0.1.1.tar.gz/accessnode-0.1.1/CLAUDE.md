# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AccessNode is a secure and flexible database management system built with FastAPI that supports multiple database types (PostgreSQL, MySQL, MongoDB) with user authentication, encrypted credentials, and async operations.

## Development Commands

### Installation
```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or install from requirements.txt
pip install -r requirements.txt
```

### Testing
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_accessnode.py

# Run with coverage
pytest --cov=accessnode
```

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Lint with ruff
ruff check .

# Type checking
mypy accessnode/
```

### Running the Application
```bash
# Start the FastAPI server
uvicorn main:app --reload

# Or run main.py directly
python main.py
```

## Architecture

### Core Components

1. **AccessNode Main Class** (`accessnode/accessnode.py`)
   - Primary interface for database operations
   - Supports multiple database types through pluggable handlers
   - Handles connection pooling, caching, and schema management
   - Can be initialized with or without database credentials for flexibility

2. **Database Layer** (`accessnode/database/`)
   - `base.py`: DatabaseHandler base class defining common interface
   - `databases/`: Specific implementations for PostgreSQL, MySQL, MongoDB, SQLite
   - `pool.py`: Connection pooling management
   - `utils.py`: Database utility functions and handler creation

3. **Schema Management** (`accessnode/schema_manager/`)
   - Dynamic schema creation and validation
   - Schema migration capabilities
   - Schema synchronization between different database types

4. **Query System** (`accessnode/query/`)
   - Query builder for cross-database compatibility
   - Query compilation and optimization
   - Filter and type management

5. **Caching Layer** (`accessnode/caching/`)
   - Multi-strategy caching (memory, Redis)
   - Cache-aware database operations
   - Configurable cache strategies

6. **API Layer** (`accessnode/api/`)
   - FastAPI routers and endpoints
   - User authentication with JWT tokens
   - Database connection management endpoints

### Database Setup

The project uses a dual database setup:

#### 1. **Main Application Database (`accessnode_main`)**
- **Purpose**: Stores application metadata, user accounts, and database connection configurations
- **Tables**:
  - `users`: User authentication and profile data
  - `user_databases`: Encrypted database connection details for user-managed databases
- **Configuration**: Via environment variables in `database/db_setup.py`
- **Environment variables**: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`

#### 2. **Test Database (`test_accessnode`)**
- **Purpose**: Isolated testing environment for unit and integration tests
- **Usage**: Automatically created/destroyed during test runs
- **Contains**: Test tables created by test fixtures (`test_items`, `test_categories`, etc.)

#### 3. **User-Managed Databases**
- **Purpose**: Databases that users connect to through AccessNode for operations
- **Management**: Connection details stored encrypted in `accessnode_main.user_databases`
- **Access**: Through AccessNode class instances configured with user credentials
- **Examples**: Any PostgreSQL, MySQL, MongoDB, or SQLite database a user wants to manage

### Key Features

- **Multi-database support**: PostgreSQL, MySQL, MongoDB, SQLite
- **Security**: Encrypted database credentials, JWT authentication, bcrypt password hashing
- **Async operations**: Full async/await support throughout the codebase
- **Flexible initialization**: AccessNode can be used with or without initial database credentials
- **Plugin system**: Extensible architecture for adding new database types
- **Real-time capabilities**: Change data capture and subscription management

### Testing Strategy

The project now follows Python testing best practices with proper unittest framework and test isolation.

#### Test Structure

**1. Unit Tests** (`tests/unit/`)
- **`test_accessnode_unit.py`**: ✅ Mock-based AccessNode tests with proper isolation
- **`test_api_unit.py`**: ✅ API endpoint validation and error handling tests
- **Features**: Uses `unittest.mock` for database isolation, no external dependencies
- **Run**: `pytest tests/unit/ -v`

**2. Integration Tests** (`tests/integration/`)
- **`test_accessnode_integration.py`**: ✅ Real database operations, concurrent operations, complex queries
- **Features**: Real PostgreSQL database, proper setup/teardown, environment-based skipping
- **Run**: `POSTGRES_PASSWORD=postgres pytest tests/integration/ -v`

**3. Legacy Tests** (Deprecated)
- **`tests/test_async_accessnode.py`**: Old pytest-based tests (working but not best practice)
- **`final_comprehensive_test.py`**: End-to-end validation script (useful for manual testing)

#### Best Practices Implemented

✅ **Proper Test Isolation**: Unit tests use mocks, integration tests have cleanup
✅ **Environment Variables**: Tests use configurable database credentials
✅ **Skip Conditions**: Integration tests skip if database unavailable
✅ **Async Support**: `unittest.IsolatedAsyncioTestCase` for async operations
✅ **Error Handling**: Tests verify both success and failure scenarios
✅ **Concurrent Testing**: Validates thread-safety and concurrent operations

#### Test Database Requirements
- PostgreSQL databases: `test_accessnode` (for integration tests)
- Environment variables: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- Optional: Tests skip gracefully if database unavailable

#### Running Tests
```bash
# Run all unit tests (no database required)
pytest tests/unit/ -v

# Run integration tests (requires PostgreSQL)
POSTGRES_PASSWORD=postgres pytest tests/integration/ -v

# Run all tests
POSTGRES_PASSWORD=postgres pytest tests/ -v --tb=short

# Create test database if needed
PGPASSWORD=postgres psql -h localhost -U postgres -c "CREATE DATABASE test_accessnode;"
```

#### Test Configuration
- **`tests/test_config.py`**: Shared test utilities and configuration
- **Base classes**: `BaseTestCase` and `AsyncBaseTestCase` for common functionality
- **Environment patching**: Automatic test environment setup
- **Skip decorators**: `@skip_if_no_database` for conditional test execution

### Important Notes

- The codebase follows async patterns throughout - always use `await` with database operations
- Schema enforcement can be toggled via the `enforce_schemas` parameter
- Database credentials are encrypted at rest using the crypto utilities in `utils/crypto.py`
- The system supports both strict schema validation and dynamic schema creation
- Connection pooling is handled automatically through the ConnectionPool class