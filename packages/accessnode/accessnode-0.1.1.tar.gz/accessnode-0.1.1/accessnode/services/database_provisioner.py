"""
Database Provisioning Service

Handles automatic creation of database instances for users across all supported database types.
"""

import os
import uuid
import sqlite3
import docker
import asyncio
import secrets
import string
from typing import Dict, Any, Optional
from pathlib import Path


class DatabaseProvisioningService:
    """Service to provision new database instances for users."""

    def __init__(self, base_data_dir: str = "/var/accessnode/databases"):
        self.base_data_dir = Path(base_data_dir)
        self.base_data_dir.mkdir(parents=True, exist_ok=True)
        self.docker_client = None
        self._init_docker()

    def _init_docker(self):
        """Initialize Docker client if available."""
        try:
            self.docker_client = docker.from_env()
            # Test connection
            self.docker_client.ping()
        except Exception as e:
            print(f"Docker not available: {e}")
            self.docker_client = None

    def _generate_credentials(self) -> Dict[str, str]:
        """Generate secure random credentials."""
        username = f"user_{secrets.token_hex(4)}"
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
        return {"username": username, "password": password}

    def _get_available_port(self, start_port: int = 5432) -> int:
        """Find an available port starting from start_port."""
        import socket
        for port in range(start_port, start_port + 1000):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', port))
                    return port
                except OSError:
                    continue
        raise Exception("No available ports found")

    async def provision_sqlite(self, user_id: int, db_name: str) -> Dict[str, Any]:
        """
        Provision a new SQLite database.

        Args:
            user_id: User ID requesting the database
            db_name: Desired database name

        Returns:
            Dictionary with connection details
        """
        # Create unique database file
        db_filename = f"user_{user_id}_{db_name}_{uuid.uuid4().hex[:8]}.db"
        user_dir = self.base_data_dir / "sqlite" / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        db_path = user_dir / db_filename

        # Create and initialize database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Create basic tables for quick start
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Insert welcome data
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)",
                      ("Welcome User", "welcome@example.com"))

        conn.commit()
        conn.close()

        return {
            "db_type": "sqlite",
            "db_name": db_name,
            "host": "localhost",
            "port": None,
            "username": None,
            "password": None,
            "database_path": str(db_path),
            "connection_string": f"sqlite:///{db_path}",
            "status": "ready",
            "message": "SQLite database created successfully"
        }

    async def provision_postgresql(self, user_id: int, db_name: str) -> Dict[str, Any]:
        """
        Provision a new PostgreSQL database using Docker.

        Args:
            user_id: User ID requesting the database
            db_name: Desired database name

        Returns:
            Dictionary with connection details
        """
        if not self.docker_client:
            raise Exception("Docker not available for PostgreSQL provisioning")

        # Generate credentials and find available port
        creds = self._generate_credentials()
        port = self._get_available_port(5432)
        container_name = f"accessnode-pg-{user_id}-{uuid.uuid4().hex[:8]}"

        # Create data directory
        data_dir = self.base_data_dir / "postgresql" / str(user_id) / db_name
        data_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Run PostgreSQL container
            container = self.docker_client.containers.run(
                "postgres:15",
                name=container_name,
                environment={
                    "POSTGRES_DB": db_name,
                    "POSTGRES_USER": creds["username"],
                    "POSTGRES_PASSWORD": creds["password"],
                },
                ports={5432: port},
                volumes={str(data_dir): {'bind': '/var/lib/postgresql/data', 'mode': 'rw'}},
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )

            # Wait for container to be ready
            await self._wait_for_database_ready("postgresql", "localhost", port,
                                              creds["username"], creds["password"], db_name)

            return {
                "db_type": "postgresql",
                "db_name": db_name,
                "host": "localhost",
                "port": port,
                "username": creds["username"],
                "password": creds["password"],
                "container_id": container.id,
                "container_name": container_name,
                "connection_string": f"postgresql://{creds['username']}:{creds['password']}@localhost:{port}/{db_name}",
                "status": "ready",
                "message": "PostgreSQL database provisioned successfully"
            }

        except Exception as e:
            # Clean up on failure
            try:
                container = self.docker_client.containers.get(container_name)
                container.remove(force=True)
            except:
                pass
            raise Exception(f"Failed to provision PostgreSQL: {str(e)}")

    async def provision_mysql(self, user_id: int, db_name: str) -> Dict[str, Any]:
        """
        Provision a new MySQL database using Docker.
        """
        if not self.docker_client:
            raise Exception("Docker not available for MySQL provisioning")

        creds = self._generate_credentials()
        port = self._get_available_port(3306)
        container_name = f"accessnode-mysql-{user_id}-{uuid.uuid4().hex[:8]}"

        data_dir = self.base_data_dir / "mysql" / str(user_id) / db_name
        data_dir.mkdir(parents=True, exist_ok=True)

        try:
            container = self.docker_client.containers.run(
                "mysql:8.0",
                name=container_name,
                environment={
                    "MYSQL_DATABASE": db_name,
                    "MYSQL_USER": creds["username"],
                    "MYSQL_PASSWORD": creds["password"],
                    "MYSQL_ROOT_PASSWORD": secrets.token_hex(16),
                },
                ports={3306: port},
                volumes={str(data_dir): {'bind': '/var/lib/mysql', 'mode': 'rw'}},
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )

            await self._wait_for_database_ready("mysql", "localhost", port,
                                              creds["username"], creds["password"], db_name)

            return {
                "db_type": "mysql",
                "db_name": db_name,
                "host": "localhost",
                "port": port,
                "username": creds["username"],
                "password": creds["password"],
                "container_id": container.id,
                "container_name": container_name,
                "connection_string": f"mysql://{creds['username']}:{creds['password']}@localhost:{port}/{db_name}",
                "status": "ready",
                "message": "MySQL database provisioned successfully"
            }

        except Exception as e:
            try:
                container = self.docker_client.containers.get(container_name)
                container.remove(force=True)
            except:
                pass
            raise Exception(f"Failed to provision MySQL: {str(e)}")

    async def provision_mongodb(self, user_id: int, db_name: str) -> Dict[str, Any]:
        """
        Provision a new MongoDB database using Docker.
        """
        if not self.docker_client:
            raise Exception("Docker not available for MongoDB provisioning")

        creds = self._generate_credentials()
        port = self._get_available_port(27017)
        container_name = f"accessnode-mongo-{user_id}-{uuid.uuid4().hex[:8]}"

        data_dir = self.base_data_dir / "mongodb" / str(user_id) / db_name
        data_dir.mkdir(parents=True, exist_ok=True)

        try:
            container = self.docker_client.containers.run(
                "mongo:7",
                name=container_name,
                environment={
                    "MONGO_INITDB_DATABASE": db_name,
                    "MONGO_INITDB_ROOT_USERNAME": creds["username"],
                    "MONGO_INITDB_ROOT_PASSWORD": creds["password"],
                },
                ports={27017: port},
                volumes={str(data_dir): {'bind': '/data/db', 'mode': 'rw'}},
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )

            await self._wait_for_database_ready("mongodb", "localhost", port,
                                              creds["username"], creds["password"], db_name)

            return {
                "db_type": "mongodb",
                "db_name": db_name,
                "host": "localhost",
                "port": port,
                "username": creds["username"],
                "password": creds["password"],
                "container_id": container.id,
                "container_name": container_name,
                "connection_string": f"mongodb://{creds['username']}:{creds['password']}@localhost:{port}/{db_name}",
                "status": "ready",
                "message": "MongoDB database provisioned successfully"
            }

        except Exception as e:
            try:
                container = self.docker_client.containers.get(container_name)
                container.remove(force=True)
            except:
                pass
            raise Exception(f"Failed to provision MongoDB: {str(e)}")

    async def _wait_for_database_ready(self, db_type: str, host: str, port: int,
                                     username: str, password: str, database: str,
                                     max_retries: int = 30):
        """Wait for database to be ready for connections."""
        import asyncio

        for attempt in range(max_retries):
            try:
                if db_type == "postgresql":
                    import asyncpg
                    conn = await asyncpg.connect(
                        host=host, port=port, user=username,
                        password=password, database=database
                    )
                    await conn.close()
                    return

                elif db_type == "mysql":
                    import aiomysql
                    conn = await aiomysql.connect(
                        host=host, port=port, user=username,
                        password=password, db=database
                    )
                    conn.close()
                    return

                elif db_type == "mongodb":
                    import motor.motor_asyncio
                    client = motor.motor_asyncio.AsyncIOMotorClient(
                        f"mongodb://{username}:{password}@{host}:{port}/{database}"
                    )
                    await client.server_info()
                    client.close()
                    return

            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Database failed to become ready: {str(e)}")
                await asyncio.sleep(2)

    async def provision_database(self, user_id: int, db_type: str, db_name: str) -> Dict[str, Any]:
        """
        Main provisioning method that delegates to specific database type handlers.

        Args:
            user_id: User ID requesting the database
            db_type: Type of database (sqlite, postgresql, mysql, mongodb)
            db_name: Desired database name

        Returns:
            Dictionary with connection details and provisioning info
        """
        db_type = db_type.lower()

        if db_type == "sqlite":
            return await self.provision_sqlite(user_id, db_name)
        elif db_type in ["postgresql", "postgres"]:
            return await self.provision_postgresql(user_id, db_name)
        elif db_type == "mysql":
            return await self.provision_mysql(user_id, db_name)
        elif db_type in ["mongodb", "mongo"]:
            return await self.provision_mongodb(user_id, db_name)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    async def deprovision_database(self, container_id: Optional[str] = None,
                                 database_path: Optional[str] = None):
        """
        Remove a provisioned database.

        Args:
            container_id: Docker container ID (for containerized databases)
            database_path: File path (for SQLite databases)
        """
        try:
            if container_id and self.docker_client:
                container = self.docker_client.containers.get(container_id)
                container.stop()
                container.remove()

            if database_path:
                db_path = Path(database_path)
                if db_path.exists():
                    db_path.unlink()

        except Exception as e:
            raise Exception(f"Failed to deprovision database: {str(e)}")