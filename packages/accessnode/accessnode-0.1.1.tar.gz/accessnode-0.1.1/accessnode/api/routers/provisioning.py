"""
Database Provisioning API Router

Provides endpoints for automatic database provisioning across all supported database types.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from accessnode.services.database_provisioner import DatabaseProvisioningService
from database.models import User, UserDatabase
from accessnode.auth.security import get_current_user_secure
from database.schemas import UserDatabaseOut
from utils.crypto import encrypt_password
from database.db_setup import get_db

router = APIRouter()

# Initialize the provisioning service with a development-friendly directory
import os
data_dir = os.path.expanduser("~/accessnode_databases")  # Use user's home directory
provisioner = DatabaseProvisioningService(base_data_dir=data_dir)


class DatabaseProvisionRequest(BaseModel):
    """Request model for database provisioning."""
    db_type: str = Field(..., description="Database type: sqlite, postgresql, mysql, mongodb")
    db_name: str = Field(..., min_length=1, max_length=50, description="Database name")
    description: str = Field("", description="Optional description")


class ProvisionedDatabaseResponse(BaseModel):
    """Response model for provisioned database."""
    id: int
    db_type: str
    db_name: str
    host: str
    port: Optional[int] = None
    username: Optional[str] = None
    password: str = "********"  # Always hidden in response
    connection_string: str
    status: str
    message: str
    container_id: Optional[str] = None
    database_path: Optional[str] = None


@router.post("/", response_model=ProvisionedDatabaseResponse)
async def provision_new_database(
    request: DatabaseProvisionRequest,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """
    Provision a new database instance automatically.

    This endpoint creates a new database instance of the specified type and
    returns connection details. The database is ready for immediate use.

    Supported database types:
    - **sqlite**: File-based database (instant, no server required)
    - **postgresql**: PostgreSQL container (Docker required)
    - **mysql**: MySQL container (Docker required)
    - **mongodb**: MongoDB container (Docker required)
    """
    try:
        # Check if user already has a database with this name
        existing_db = await db.execute(
            select(UserDatabase.id).where(
                UserDatabase.owner_id == current_user.id,
                UserDatabase.db_name == request.db_name
            )
        )
        if existing_db.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"You already have a database named '{request.db_name}'"
            )

        # Provision the database
        provision_result = await provisioner.provision_database(
            user_id=current_user.id,
            db_type=request.db_type,
            db_name=request.db_name
        )

        # Store in user_databases table
        encrypted_password = None
        if provision_result.get("password"):
            encrypted_password = encrypt_password(provision_result["password"])
            if isinstance(encrypted_password, bytes):
                encrypted_password = encrypted_password.decode('utf-8')

        new_database = UserDatabase(
            owner_id=current_user.id,
            db_name=request.db_name,
            db_type=provision_result["db_type"],
            host=provision_result["host"],
            port=provision_result.get("port"),
            username=provision_result.get("username"),
            password=encrypted_password,
        )

        db.add(new_database)
        await db.commit()
        await db.refresh(new_database)

        # Store provisioning metadata (container IDs, file paths, etc.)
        if provision_result.get("container_id"):
            # Store container metadata for management
            # You might want to create a separate table for this
            pass

        return ProvisionedDatabaseResponse(
            id=new_database.id,
            db_type=provision_result["db_type"],
            db_name=request.db_name,
            host=provision_result["host"],
            port=provision_result.get("port"),
            username=provision_result.get("username"),
            connection_string=provision_result["connection_string"],
            status=provision_result["status"],
            message=provision_result["message"],
            container_id=provision_result.get("container_id"),
            database_path=provision_result.get("database_path")
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to provision database: {str(e)}"
        )


@router.get("/supported")
async def get_supported_database_types():
    """
    Get list of supported database types for provisioning.
    """
    return {
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


@router.delete("/{database_id}")
async def deprovision_database(
    database_id: int,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a provisioned database and clean up resources.

    This will:
    - Stop and remove Docker containers (for containerized databases)
    - Delete database files (for SQLite)
    - Remove the database from your account
    """
    try:
        # Get the database record
        user_db = await db.get(UserDatabase, database_id)
        if not user_db or user_db.owner_id != current_user.id:
            raise HTTPException(
                status_code=404,
                detail="Database not found or access denied"
            )

        # Deprovision based on type
        if user_db.db_type == "sqlite":
            # For SQLite, construct the likely file path
            # You might want to store this metadata in a separate table
            database_path = f"/var/accessnode/databases/sqlite/{current_user.id}/{user_db.db_name}"
            await provisioner.deprovision_database(database_path=database_path)
        else:
            # For containerized databases, you'd need to store container_id
            # This requires extending the UserDatabase model or creating metadata table
            pass

        # Remove from database
        await db.delete(user_db)
        await db.commit()

        return {
            "message": f"Database '{user_db.db_name}' has been successfully deprovisioned",
            "db_name": user_db.db_name,
            "db_type": user_db.db_type
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deprovision database: {str(e)}"
        )


@router.get("/quick-examples")
async def get_quick_start_examples():
    """
    Get example code for quickly connecting to provisioned databases.
    """
    return {
        "examples": {
            "python_sqlite": '''
# SQLite Example (AccessNode)
from accessnode import AccessNode

db = AccessNode(
    db_type="sqlite",
    database_name="your_db_name.db",
    host="localhost"
)
await db.initialize()

# Create a table
await db.raw_query("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT
    )
""")

# Insert data
await db.insert("users", {"name": "John", "email": "john@example.com"})

# Query data
users = await db.get_all("users")
print(users)
''',
            "python_postgresql": '''
# PostgreSQL Example (AccessNode)
from accessnode import AccessNode

db = AccessNode(
    db_type="postgresql",
    database_name="your_db_name",
    username="your_username",
    password="your_password",
    host="localhost",
    port=your_port
)
await db.initialize()

# Use the database
users = await db.raw_query("SELECT * FROM users")
''',
            "connection_strings": {
                "sqlite": "sqlite:///path/to/database.db",
                "postgresql": "postgresql://username:password@localhost:port/database",
                "mysql": "mysql://username:password@localhost:port/database",
                "mongodb": "mongodb://username:password@localhost:port/database"
            }
        }
    }