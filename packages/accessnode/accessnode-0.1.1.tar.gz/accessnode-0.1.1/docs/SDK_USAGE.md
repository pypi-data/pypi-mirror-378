# AccessNode SDK Usage Guide

This guide demonstrates how to use AccessNode as a Python SDK for direct database integration.

## Installation

```bash
pip install accessnode-db-manager
```

## Basic Usage

### Importing AccessNode

```python
from accessnode import AccessNode
```

### Basic Connection

```python
import asyncio
from accessnode import AccessNode

async def main():
    # Initialize database connection
    db = AccessNode(
        db_type="postgres",
        database_name="myapp",
        host="localhost",
        port=5432,
        username="dbuser",
        password="dbpass"
    )

    # Initialize the connection
    await db.initialize()

    # Your database operations here

    # Clean up
    await db.close()

# Run the async function
asyncio.run(main())
```

## Database Operations

### Raw Query Execution

```python
async def execute_queries():
    db = AccessNode(db_type="postgres", database_name="myapp", ...)
    await db.initialize()

    # Simple SELECT query
    results = await db.raw_query("SELECT * FROM users")
    print(f"Found {len(results)} users")

    # Query with parameters
    user = await db.raw_query(
        "SELECT * FROM users WHERE id = $1",
        [1]
    )

    # INSERT with parameters
    await db.raw_query(
        "INSERT INTO users (name, email) VALUES ($1, $2)",
        ["John Doe", "john@example.com"]
    )

    await db.close()
```

### CRUD Operations

```python
async def crud_operations():
    db = AccessNode(db_type="postgres", database_name="myapp", ...)
    await db.initialize()

    # CREATE - Insert a new record
    user_id = await db.insert("users", {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "age": 28
    })
    print(f"Created user with ID: {user_id}")

    # READ - Get a single record
    user = await db.get("users", {"id": user_id})
    print(f"User: {user}")

    # READ - Get multiple records
    all_users = await db.get_all("users")
    active_users = await db.get_all("users", {"active": True})

    # UPDATE - Update a record
    await db.update("users", {"id": user_id}, {"age": 29})

    # DELETE - Delete a record
    await db.delete("users", {"id": user_id})

    await db.close()
```

## Database-Specific Examples

### PostgreSQL

```python
from accessnode import AccessNode

async def postgres_example():
    db = AccessNode(
        db_type="postgres",
        database_name="myapp",
        host="localhost",
        port=5432,
        username="postgres",
        password="password"
    )

    await db.initialize()

    # PostgreSQL-specific features
    results = await db.raw_query("""
        SELECT u.name, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.id, u.name
        HAVING COUNT(o.id) > 5
    """)

    await db.close()
```

### MySQL

```python
async def mysql_example():
    db = AccessNode(
        db_type="mysql",
        database_name="myapp",
        host="localhost",
        port=3306,
        username="root",
        password="password"
    )

    await db.initialize()

    # MySQL-specific query
    results = await db.raw_query("""
        SELECT * FROM users
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    """)

    await db.close()
```

### MongoDB

```python
async def mongodb_example():
    db = AccessNode(
        db_type="mongodb",
        database_name="myapp",
        host="localhost",
        port=27017,
        username="mongouser",
        password="mongopass"
    )

    await db.initialize()

    # MongoDB operations
    # Insert document
    user_id = await db.insert("users", {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "preferences": {
            "theme": "dark",
            "notifications": True
        },
        "tags": ["developer", "python", "mongodb"]
    })

    # Query with MongoDB-style filters
    developers = await db.get_all("users", {"tags": "developer"})

    await db.close()
```

### SQLite

```python
async def sqlite_example():
    db = AccessNode(
        db_type="sqlite",
        database_name="myapp.db"  # File path for SQLite
    )

    await db.initialize()

    # SQLite operations (same interface as other databases)
    await db.insert("users", {"name": "Bob Wilson", "email": "bob@example.com"})
    users = await db.get_all("users")

    await db.close()
```

## Advanced Features

### Schema Management

```python
async def schema_management():
    # Enable schema enforcement
    db = AccessNode(
        db_type="postgres",
        database_name="myapp",
        enforce_schemas=True,
        auto_sync=True,
        ...
    )

    await db.initialize()

    # Schema will be automatically validated and managed
    # Insert will validate against schema
    await db.insert("users", {
        "name": "Valid User",
        "email": "valid@example.com",
        "age": 25  # Must match schema requirements
    })

    await db.close()
```

### Caching

```python
from accessnode import AccessNode
from accessnode.caching.redis_cache import RedisCache
from accessnode.caching.memory import MemoryCache

async def caching_example():
    # Redis caching
    redis_cache = RedisCache(host="localhost", port=6379)

    # Or memory caching
    memory_cache = MemoryCache(max_size=1000)

    db = AccessNode(
        db_type="postgres",
        database_name="myapp",
        cache=redis_cache,  # or memory_cache
        ...
    )

    await db.initialize()

    # First query hits database
    users = await db.get_all("users")

    # Second identical query hits cache
    users_cached = await db.get_all("users")

    await db.close()
```

### Transaction Management

```python
async def transaction_example():
    db = AccessNode(db_type="postgres", database_name="myapp", ...)
    await db.initialize()

    # Start a transaction
    async with db.transaction():
        # All operations within this block are part of the transaction
        user_id = await db.insert("users", {"name": "Test User", "email": "test@example.com"})
        await db.insert("profiles", {"user_id": user_id, "bio": "Test bio"})

        # If any operation fails, the entire transaction is rolled back
        # If all operations succeed, the transaction is committed

    await db.close()
```

### Connection Pooling

```python
async def pooling_example():
    # Connection pooling is handled automatically
    db = AccessNode(
        db_type="postgres",
        database_name="myapp",
        pool_size=10,  # Maximum connections in pool
        max_overflow=20,  # Additional connections if needed
        ...
    )

    await db.initialize()

    # Multiple concurrent operations will use the connection pool
    import asyncio

    tasks = []
    for i in range(100):
        task = db.get_all("users", {"active": True})
        tasks.append(task)

    # Execute all queries concurrently using the connection pool
    results = await asyncio.gather(*tasks)

    await db.close()
```

## Error Handling

```python
from accessnode import AccessNode
from accessnode.core.exceptions import DatabaseConnectionError, QueryExecutionError

async def error_handling_example():
    try:
        db = AccessNode(
            db_type="postgres",
            database_name="nonexistent",
            host="invalid-host",
            ...
        )
        await db.initialize()

    except DatabaseConnectionError as e:
        print(f"Failed to connect to database: {e}")
        return

    try:
        # Invalid query
        await db.raw_query("INVALID SQL QUERY")

    except QueryExecutionError as e:
        print(f"Query failed: {e}")

    finally:
        await db.close()
```

## Context Manager Usage

```python
async def context_manager_example():
    # Use AccessNode as a context manager for automatic cleanup
    async with AccessNode(
        db_type="postgres",
        database_name="myapp",
        ...
    ) as db:
        # Database is automatically initialized
        users = await db.get_all("users")

        # Process users
        for user in users:
            print(f"User: {user['name']}")

    # Database connection is automatically closed
```

## Best Practices

### 1. Use Connection Pooling for High-Concurrency Applications

```python
# Good for web applications
db = AccessNode(
    db_type="postgres",
    database_name="webapp",
    pool_size=20,
    max_overflow=30,
    ...
)
```

### 2. Enable Caching for Read-Heavy Workloads

```python
from accessnode.caching.redis_cache import RedisCache

cache = RedisCache(host="redis-server", port=6379)
db = AccessNode(..., cache=cache)
```

### 3. Use Schema Enforcement in Production

```python
db = AccessNode(
    ...,
    enforce_schemas=True,
    auto_sync=False  # Manual schema migrations in production
)
```

### 4. Proper Error Handling

```python
async def robust_operation():
    async with AccessNode(...) as db:
        try:
            result = await db.insert("users", user_data)
            return result
        except QueryExecutionError as e:
            # Log error and handle gracefully
            logger.error(f"Failed to insert user: {e}")
            raise
```

### 5. Use Environment Variables for Configuration

```python
import os

db = AccessNode(
    db_type=os.getenv("DB_TYPE", "postgres"),
    database_name=os.getenv("DB_NAME"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
```

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from accessnode import AccessNode
import os

app = FastAPI()

async def get_db():
    db = AccessNode(
        db_type=os.getenv("DB_TYPE"),
        database_name=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    await db.initialize()
    try:
        yield db
    finally:
        await db.close()

@app.get("/users")
async def get_users(db: AccessNode = Depends(get_db)):
    users = await db.get_all("users")
    return {"users": users}
```

### Django Integration

```python
# In your Django views or services
from accessnode import AccessNode
from django.conf import settings

class UserService:
    def __init__(self):
        self.db = AccessNode(
            db_type=settings.ACCESSNODE_DB_TYPE,
            database_name=settings.ACCESSNODE_DB_NAME,
            host=settings.ACCESSNODE_DB_HOST,
            port=settings.ACCESSNODE_DB_PORT,
            username=settings.ACCESSNODE_DB_USER,
            password=settings.ACCESSNODE_DB_PASSWORD
        )

    async def get_users(self):
        await self.db.initialize()
        try:
            return await self.db.get_all("users")
        finally:
            await self.db.close()
```

This comprehensive SDK usage guide covers most common use cases and patterns for integrating AccessNode into your Python applications.