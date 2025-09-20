# routers/user.py
from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_setup import get_db
from database.db_utilities import get_user_databases, check_db_connection

from database.schemas import UserCreate, UserOut, UserDatabaseOut, UserDatabaseCreate, QueryRequest
from database.models import User, UserDatabase
from accessnode.auth.security import get_current_user_secure
from utils.utils import get_password_hash
from utils.crypto import encrypt_password, decrypt_password

from typing import List

from accessnode import AccessNode

router = APIRouter(prefix="/user")

async def get_existing_user(username: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_existing_user(user.username, db):
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(username=user.username, hashed_password=get_password_hash(user.password))
    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to register user") from e

    return UserOut(
        id=new_user.id,
        username=new_user.username,
        databases=[]
    )


@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user_secure), db: AsyncSession = Depends(get_db)):
    query = select(User).options(selectinload(User.databases)).where(User.id == current_user.id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/databases", response_model=List[UserDatabaseOut])
async def get_user_databases_route(
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    try:
        query = select(UserDatabase).where(UserDatabase.owner_id == current_user.id)
        result = await db.execute(query)
        databases = result.scalars().all()
        return databases
    except Exception as e:
        print(f"Error fetching databases: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch databases")

@router.post("/databases/setup", response_model=UserDatabaseOut)
async def setup_database(
    database_info: UserDatabaseCreate,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    user_databases = await get_user_databases(db, current_user.id)
    if any(db.db_name == database_info.db_name for db in user_databases):
        raise HTTPException(status_code=400, detail="Database with this name already exists")

    try:
        encrypted_password = encrypt_password(database_info.password)
        if isinstance(encrypted_password, bytes):
            encrypted_password = encrypted_password.decode('utf-8')

        new_database = UserDatabase(
            owner_id=current_user.id,
            db_name=database_info.db_name,
            db_type=database_info.db_type,
            host=database_info.host,
            port=database_info.port,
            username=database_info.username,
            password=encrypted_password,
        )

        db.add(new_database)
        await db.commit()
        await db.refresh(new_database)

        return UserDatabaseOut(
            id=new_database.id,
            db_name=new_database.db_name,
            db_type=new_database.db_type,
            host=new_database.host,
            port=new_database.port,
            username=new_database.username,
            password="********"
        )
    except Exception as e:
        await db.rollback()
        print(f"Database setup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to setup database connection")

@router.post("/databases/connect", response_model=UserDatabaseOut)
async def connect_database(
    db_info: UserDatabaseCreate,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Check if database with same name already exists
        existing_db = await db.execute(
            select(UserDatabase).where(
                UserDatabase.owner_id == current_user.id,
                UserDatabase.db_name == db_info.db_name
            )
        )
        if existing_db.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Database with this name already exists")

        # Check database connection
        connection_success = await check_db_connection(db_info)
        if not connection_success:
            raise HTTPException(
                status_code=400,
                detail="Failed to connect to the database with the provided credentials"
            )

        # Encrypt the password
        encrypted_password = encrypt_password(db_info.password)
        if isinstance(encrypted_password, bytes):
            encrypted_password = encrypted_password.decode('utf-8')

        # Create new database record
        new_database = UserDatabase(
            owner_id=current_user.id,
            db_name=db_info.db_name,
            db_type=db_info.db_type,
            host=db_info.host,
            port=db_info.port,
            username=db_info.username,
            password=encrypted_password
        )

        db.add(new_database)
        await db.commit()
        await db.refresh(new_database)

        return UserDatabaseOut(
            id=new_database.id,
            db_name=new_database.db_name,
            db_type=new_database.db_type,
            host=new_database.host,
            port=new_database.port,
            username=new_database.username,
            password="********"
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error connecting to database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to database: {str(e)}")

@router.get("/databases/{db_id}", response_model=UserDatabaseOut)
async def get_database_connection(
    db_id: int,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    query = select(UserDatabase).where(UserDatabase.id == db_id, UserDatabase.owner_id == current_user.id)
    result = await db.execute(query)
    database = result.scalar_one_or_none()
    
    if not database:
        raise HTTPException(status_code=404, detail="Database not found")
    
    decrypted_password = decrypt_password(database.password)
    
    return UserDatabaseOut(
        id=database.id,
        db_name=database.db_name,
        db_type=database.db_type,
        host=database.host,
        port=database.port,
        username=database.username,
        password=decrypted_password
    )

@router.post("/database/{db_id}/query")
async def execute_query(
    db_id: int,
    query_request: QueryRequest,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(UserDatabase)
            .where(UserDatabase.id == db_id, UserDatabase.owner_id == current_user.id)
        )
        user_db = result.scalar_one_or_none()

        if not user_db:
            raise HTTPException(status_code=404, detail="Database not found")

        decrypted_password = decrypt_password(user_db.password)

        access_node = AccessNode(
            db_type=user_db.db_type,
            database_name=user_db.db_name,
            host=user_db.host,
            port=user_db.port,
            username=user_db.username,
            password=decrypted_password,
            auto_sync=False
        )

        try:
            await access_node.initialize()
            result = await access_node.raw_query(query_request.query)
            return {"result": result}
        finally:
            await access_node.close()

    except Exception as e:
        print(f"Error executing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute query: {str(e)}")

@router.get("/databases/{db_id}/schema")
async def get_database_schema(
    db_id: int,
    table_name: str = Query(None, description="Specific table name to get schema for"),
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(UserDatabase)
            .where(UserDatabase.id == db_id, UserDatabase.owner_id == current_user.id)
        )
        user_db = result.scalar_one_or_none()

        if not user_db:
            raise HTTPException(status_code=404, detail="Database not found")

        decrypted_password = decrypt_password(user_db.password)

        access_node = AccessNode(
            db_type=user_db.db_type,
            database_name=user_db.db_name,
            host=user_db.host,
            port=user_db.port,
            username=user_db.username,
            password=decrypted_password,
            auto_sync=False
        )

        try:
            await access_node.initialize()
            schema_info = await access_node.get_table_schema(table_name)
            return {"schema": schema_info}
        finally:
            await access_node.close()

    except Exception as e:
        print(f"Error getting schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch schema information: {str(e)}")

@router.delete("/databases/{db_id}")
async def delete_database_connection(
    db_id: int,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a database connection from the user's account.

    This only removes the connection details from AccessNode,
    it does not delete the actual database.
    """
    try:
        # Find the database connection
        result = await db.execute(
            select(UserDatabase)
            .where(UserDatabase.id == db_id, UserDatabase.owner_id == current_user.id)
        )
        user_db = result.scalar_one_or_none()

        if not user_db:
            raise HTTPException(status_code=404, detail="Database connection not found")

        # Store details for response
        db_name = user_db.db_name
        db_type = user_db.db_type

        # Delete the database connection
        await db.delete(user_db)
        await db.commit()

        return {
            "message": f"Database connection '{db_name}' has been removed successfully",
            "db_name": db_name,
            "db_type": db_type,
            "id": db_id
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error deleting database connection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete database connection: {str(e)}")

@router.get("/databases/{db_id}/schemas")
async def get_database_schemas_plural(
    db_id: int,
    table_name: str = Query(None, description="Specific table name to get schema for"),
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """Get schema information for all tables or a specific table (plural endpoint for frontend compatibility)."""
    try:
        result = await db.execute(
            select(UserDatabase)
            .where(UserDatabase.id == db_id, UserDatabase.owner_id == current_user.id)
        )
        user_db = result.scalar_one_or_none()

        if not user_db:
            raise HTTPException(status_code=404, detail="Database not found")

        decrypted_password = decrypt_password(user_db.password)

        access_node = AccessNode(
            db_type=user_db.db_type,
            database_name=user_db.db_name,
            host=user_db.host,
            port=user_db.port,
            username=user_db.username,
            password=decrypted_password,
            auto_sync=False
        )

        try:
            await access_node.initialize()
            print(f"Getting schema for table_name: {table_name}")
            schema_info = await access_node.get_table_schema(table_name)
            print(f"Schema info returned: {schema_info}")
            return {"schema": schema_info}
        finally:
            await access_node.close()

    except Exception as e:
        print(f"Error getting schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch schema information: {str(e)}")

@router.post("/databases/{db_id}/schemas")
async def create_or_update_schema_plural(
    db_id: int,
    schema_request: dict,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """Create or update database schema (tables) - plural endpoint for frontend compatibility."""
    try:
        result = await db.execute(
            select(UserDatabase)
            .where(UserDatabase.id == db_id, UserDatabase.owner_id == current_user.id)
        )
        user_db = result.scalar_one_or_none()

        if not user_db:
            raise HTTPException(status_code=404, detail="Database not found")

        decrypted_password = decrypt_password(user_db.password)

        access_node = AccessNode(
            db_type=user_db.db_type,
            database_name=user_db.db_name,
            host=user_db.host,
            port=user_db.port,
            username=user_db.username,
            password=decrypted_password,
            auto_sync=False
        )

        try:
            await access_node.initialize()

            # Debug: Log the incoming request
            print(f"Schema request received: {schema_request}")

            # If schema_request contains a SQL DDL statement, execute it
            if "sql" in schema_request:
                result = await access_node.raw_query(schema_request["sql"])
                return {"message": "Schema updated successfully", "result": result}

            # If schema_request contains table definition, create table
            elif ("table_name" in schema_request and "columns" in schema_request) or ("name" in schema_request and "fields" in schema_request):
                # Handle both formats: {"table_name": "X", "columns": [...]} and {"name": "X", "fields": [...]}
                table_name = schema_request.get("table_name") or schema_request.get("name")
                columns = schema_request.get("columns") or schema_request.get("fields")

                # Validate table name
                if not table_name or table_name.strip() == "":
                    raise HTTPException(status_code=400, detail="Table name is required and cannot be empty")

                # Validate columns
                if not columns or len(columns) == 0:
                    raise HTTPException(status_code=400, detail="At least one column/field is required")

                # Build CREATE TABLE statement based on database type
                if user_db.db_type.lower() in ["postgresql", "mysql"]:
                    column_defs = []
                    for col in columns:
                        # Map frontend field types to SQL types
                        sql_type = col['type']
                        if sql_type == 'string':
                            sql_type = 'VARCHAR(255)'
                        elif sql_type == 'integer':
                            sql_type = 'INT'
                        elif sql_type == 'boolean':
                            sql_type = 'BOOLEAN'

                        col_def = f"{col['name']} {sql_type}"

                        # Handle different field formats
                        is_primary_key = col.get('primary_key') or col.get('unique')
                        is_required = col.get('required') or not col.get('nullable', True)

                        if is_primary_key:
                            col_def += " PRIMARY KEY"
                        elif is_required:
                            col_def += " NOT NULL"

                        if col.get('default'):
                            col_def += f" DEFAULT {col['default']}"
                        column_defs.append(col_def)

                    create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
                    result = await access_node.raw_query(create_sql)
                    return {"message": f"Table '{table_name}' created successfully (or already exists)", "result": result}

                else:
                    return {"message": "Schema creation not yet implemented for this database type"}

            else:
                raise HTTPException(status_code=400, detail="Invalid schema request format")

        finally:
            await access_node.close()

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating/updating schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create/update schema: {str(e)}")



# from RestrictedPython import compile_restricted, safe_globals, utility_builtins

# @router.post("/execute-python")
# async def execute_python(user_code: str):
#     try:
#         # Compile the code with restrictions
#         compiled_code = compile_restricted(user_code, "<string>", "exec")

#         # Define a restricted environment
#         exec_globals = {
#             "__builtins__": safe_globals,
#         }
#         exec_locals = {}

#         # Execute the compiled code
#         exec(compiled_code, exec_globals, exec_locals)

#         # Return the execution result
#         return {"result": exec_locals}
#     except Exception as e:
#         return {"error": str(e)}
