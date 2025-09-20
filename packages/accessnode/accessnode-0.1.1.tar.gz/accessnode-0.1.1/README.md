# AccessNode Database Manager

**A secure and flexible database management system that provides both SDK and API access to multiple database types.**

AccessNode serves as a unified interface for database operations across PostgreSQL, MySQL, MongoDB, and SQLite, offering both direct Python integration and REST API access.

## 🚀 Features

### Core Capabilities
- 🗄️ **Multi-database support**: PostgreSQL, MySQL, MongoDB, SQLite
- 🔐 **Secure authentication**: JWT tokens with encrypted credential storage
- ⚡ **Async operations**: Full async/await support for high performance
- 🎯 **Dual access modes**: Use as Python SDK or REST API service
- 🔄 **Schema management**: Dynamic schema creation, validation, and migration
- 💾 **Smart caching**: Memory and Redis caching strategies
- 🔌 **Plugin architecture**: Extensible for new database types

### Security Features
- Encrypted database credentials at rest
- bcrypt password hashing
- JWT authentication
- CORS protection
- Safe query execution

## 📦 Installation

### For SDK Usage
```bash
pip install accessnode-db-manager
```

### For Development
```bash
# Clone and install with dev dependencies
git clone <repository-url>
cd AccessNode
pip install -e ".[dev]"
```

## 🔧 Quick Start

### SDK Usage (Direct Python Integration)

```python
from accessnode import AccessNode

# Initialize database connection
db = AccessNode(
    db_type="postgres",
    database_name="your_db",
    host="localhost",
    port=5432,
    username="user",
    password="pass"
)

# Initialize the connection
await db.initialize()

# Execute raw queries
results = await db.raw_query("SELECT * FROM your_table")

# Use built-in operations
user_data = await db.get("users", {"id": 1})
new_id = await db.insert("users", {"name": "John", "email": "john@example.com"})
```

### API Service Usage

1. **Start the server:**
```bash
uvicorn main:app --reload
```

2. **Register and authenticate:**
```bash
# Register a user
curl -X POST "http://localhost:8000/user/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Get access token
curl -X POST "http://localhost:8000/user/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"
```

3. **Set up database connection:**
```bash
curl -X POST "http://localhost:8000/user/databases/setup" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_postgres_db",
    "db_type": "postgres",
    "host": "localhost",
    "port": 5432,
    "database_name": "mydb",
    "username": "user",
    "password": "pass"
  }'
```

## 📚 Advanced Usage

### Schema Management
```python
# Enable schema enforcement
db = AccessNode(
    db_type="postgres",
    database_name="mydb",
    enforce_schemas=True,
    auto_sync=True
)

# Schema will be automatically managed
await db.initialize()
```

### Caching
```python
from accessnode.caching.redis_cache import RedisCache

# Initialize with Redis caching
cache = RedisCache(host="localhost", port=6379)
db = AccessNode(
    db_type="postgres",
    database_name="mydb",
    cache=cache
)
```

### Multiple Database Types
```python
# PostgreSQL
pg_db = AccessNode(db_type="postgres", database_name="pg_db", ...)

# MongoDB
mongo_db = AccessNode(db_type="mongodb", database_name="mongo_db", ...)

# MySQL
mysql_db = AccessNode(db_type="mysql", database_name="mysql_db", ...)
```

## 🔌 API Endpoints

### Authentication
- `POST /user/register` - Register a new user
- `POST /user/token` - Login and get access token

### Database Management
- `POST /user/databases/setup` - Configure a new database connection
- `GET /user/databases` - List user's database connections
- `DELETE /user/databases/{db_id}` - Remove a database connection

### Query Operations
- `POST /user/database/{db_id}/query` - Execute database queries
- `GET /user/database/{db_id}/tables` - List tables in database

Visit `/docs` after starting the server for interactive API documentation.

## 🛠️ Development

### Setup
```bash
# Install dependencies
pip install -e ".[dev]"

# Set up environment variables
export POSTGRES_USER=your_user
export POSTGRES_PASSWORD=your_password
export POSTGRES_HOST=localhost
export POSTGRES_DB=accessnode_main
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=accessnode

# Run specific test file
pytest tests/test_accessnode.py -v
```

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Lint code
ruff check .

# Type checking
mypy accessnode/
```

## 🏗️ Architecture

AccessNode follows a modular architecture:

- **Core Layer**: Main AccessNode class and base interfaces
- **Database Layer**: Database-specific handlers and connection pooling
- **Schema Layer**: Dynamic schema management and validation
- **Query Layer**: Cross-database query building and compilation
- **Caching Layer**: Multiple caching strategies and cache-aware operations
- **API Layer**: FastAPI routes and authentication
- **Security Layer**: Encryption, hashing, and secure credential management

## 🔒 Security

- **Encrypted storage**: Database credentials encrypted at rest using AES
- **Password security**: bcrypt hashing for user passwords
- **Token-based auth**: JWT tokens for API authentication
- **Input validation**: Comprehensive input validation and sanitization
- **Connection security**: Secure database connection handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Visit `/docs` endpoint when running the API
- **Issues**: Report bugs and request features via GitHub Issues
- **Community**: Join our discussions for questions and collaboration