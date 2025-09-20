# user_secure.py - Updated user router with secure authentication
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.db_setup import get_db
from database.db_utilities import get_user_databases, check_db_connection
from database.schemas import UserDatabaseOut, UserDatabaseCreate, QueryRequest
from database.models import User, UserDatabase

# Import secure authentication components
from accessnode.auth.security import (
    get_current_user_secure,
    UserRole,
    require_role
)
from accessnode.auth.audit import audit_manager, AuditAction
from utils.crypto import encrypt_password, decrypt_password
from accessnode import AccessNode

router = APIRouter(prefix="/user", tags=["User Management"])


@router.get("/databases", response_model=List[UserDatabaseOut])
async def get_user_databases_secure(
    request: Request,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's database connections with security audit logging
    """
    try:
        # Log database access
        await audit_manager.log_audit_event(
            db=db,
            action=AuditAction.DATABASE_ACCESS,
            user_id=current_user.id,
            resource="database",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=True
        )

        # Fetch user databases
        query = select(UserDatabase).where(
            UserDatabase.owner_id == current_user.id,
            UserDatabase.is_active == True
        )
        result = await db.execute(query)
        databases = result.scalars().all()

        # Return databases with masked passwords
        return [
            UserDatabaseOut(
                id=database.id,
                db_name=database.db_name,
                db_type=database.db_type,
                host=database.host,
                port=database.port,
                username=database.username,
                password="********"  # Always mask password in list view
            )
            for database in databases
        ]

    except Exception as e:
        # Log failed access
        await audit_manager.log_audit_event(
            db=db,
            action=AuditAction.DATABASE_ACCESS,
            user_id=current_user.id,
            resource="database",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch databases"
        )


@router.post("/databases/connect", response_model=UserDatabaseOut)
async def connect_database_secure(
    db_info: UserDatabaseCreate,
    request: Request,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """
    Connect to a new database with enhanced security validation
    """
    try:
        # Check if database with same name already exists
        existing_db = await db.execute(
            select(UserDatabase).where(
                UserDatabase.owner_id == current_user.id,
                UserDatabase.db_name == db_info.db_name,
                UserDatabase.is_active == True
            )
        )
        if existing_db.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database with this name already exists"
            )

        # Test database connection before saving
        connection_success = await check_db_connection(db_info)
        if not connection_success:
            await audit_manager.log_audit_event(
                db=db,
                action=AuditAction.DATABASE_CREATE,
                user_id=current_user.id,
                resource="database",
                resource_id=db_info.db_name,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", ""),
                success=False,
                details={"reason": "connection_failed"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
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
            password=encrypted_password,
            is_active=True
        )

        db.add(new_database)
        await db.commit()
        await db.refresh(new_database)

        # Log successful database creation
        await audit_manager.log_audit_event(
            db=db,
            action=AuditAction.DATABASE_CREATE,
            user_id=current_user.id,
            resource="database",
            resource_id=db_info.db_name,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=True,
            details={
                "db_type": db_info.db_type,
                "host": db_info.host,
                "port": db_info.port
            }
        )

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

        # Log failed database creation
        await audit_manager.log_audit_event(
            db=db,
            action=AuditAction.DATABASE_CREATE,
            user_id=current_user.id,
            resource="database",
            resource_id=db_info.db_name,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to database"
        )


@router.get("/databases/{db_id}", response_model=UserDatabaseOut)
async def get_database_connection_secure(
    db_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db),
    include_password: bool = Query(False, description="Include decrypted password")
):
    """
    Get specific database connection details
    """
    try:
        # Fetch database connection
        query = select(UserDatabase).where(
            UserDatabase.id == db_id,
            UserDatabase.owner_id == current_user.id,
            UserDatabase.is_active == True
        )
        result = await db.execute(query)
        database = result.scalar_one_or_none()

        if not database:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database not found"
            )

        # Log database access
        await audit_manager.log_audit_event(
            db=db,
            action=AuditAction.DATABASE_ACCESS,
            user_id=current_user.id,
            resource="database",
            resource_id=str(db_id),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=True,
            details={"include_password": include_password}
        )

        # Decrypt password only if explicitly requested
        password = decrypt_password(database.password) if include_password else "********"

        return UserDatabaseOut(
            id=database.id,
            db_name=database.db_name,
            db_type=database.db_type,
            host=database.host,
            port=database.port,
            username=database.username,
            password=password
        )

    except HTTPException:
        raise
    except Exception as e:
        # Log failed access
        await audit_manager.log_audit_event(
            db=db,
            action=AuditAction.DATABASE_ACCESS,
            user_id=current_user.id,
            resource="database",
            resource_id=str(db_id),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch database details"
        )


@router.delete("/databases/{db_id}")
async def delete_database_connection_secure(
    db_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a database connection (soft delete)
    """
    try:
        # Find the database connection
        result = await db.execute(
            select(UserDatabase).where(
                UserDatabase.id == db_id,
                UserDatabase.owner_id == current_user.id,
                UserDatabase.is_active == True
            )
        )
        user_db = result.scalar_one_or_none()

        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database connection not found"
            )

        # Store details for logging
        db_name = user_db.db_name
        db_type = user_db.db_type

        # Soft delete (mark as inactive)
        user_db.is_active = False
        await db.commit()

        # Log database deletion
        await audit_manager.log_audit_event(
            db=db,
            action=AuditAction.DATABASE_DELETE,
            user_id=current_user.id,
            resource="database",
            resource_id=str(db_id),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=True,
            details={
                "db_name": db_name,
                "db_type": db_type,
                "deletion_type": "soft_delete"
            }
        )

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

        # Log failed deletion
        await audit_manager.log_audit_event(
            db=db,
            action=AuditAction.DATABASE_DELETE,
            user_id=current_user.id,
            resource="database",
            resource_id=str(db_id),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete database connection"
        )


@router.post("/database/{db_id}/query")
async def execute_query_secure(
    db_id: int,
    query_request: QueryRequest,
    request: Request,
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute database query with comprehensive security logging
    """
    try:
        # Fetch database connection
        result = await db.execute(
            select(UserDatabase).where(
                UserDatabase.id == db_id,
                UserDatabase.owner_id == current_user.id,
                UserDatabase.is_active == True
            )
        )
        user_db = result.scalar_one_or_none()

        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database not found"
            )

        # Basic query validation
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'UPDATE']
        query_upper = query_request.query.upper().strip()

        risk_level = "low"
        if any(keyword in query_upper for keyword in dangerous_keywords):
            risk_level = "high"

        # Decrypt password and create AccessNode connection
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
            query_result = await access_node.raw_query(query_request.query)

            # Log successful query execution
            await audit_manager.log_audit_event(
                db=db,
                action=AuditAction.QUERY_EXECUTE,
                user_id=current_user.id,
                resource="database",
                resource_id=user_db.db_name,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", ""),
                success=True,
                details={
                    "query_type": query_upper.split()[0] if query_upper else "UNKNOWN",
                    "risk_level": risk_level,
                    "result_count": len(query_result) if isinstance(query_result, list) else 0
                }
            )

            return {"result": query_result}

        finally:
            await access_node.close()

    except HTTPException:
        raise
    except Exception as e:
        # Log failed query execution
        await audit_manager.log_audit_event(
            db=db,
            action=AuditAction.QUERY_EXECUTE,
            user_id=current_user.id,
            resource="database",
            resource_id=str(db_id),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            details={
                "error": str(e),
                "query": query_request.query[:100] + "..." if len(query_request.query) > 100 else query_request.query
            }
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute query"
        )


@router.get("/database/{db_id}/schema")
async def get_database_schema_secure(
    db_id: int,
    request: Request,
    table_name: str = Query(None, description="Specific table name to get schema for"),
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """
    Get database schema information with security logging
    """
    try:
        # Fetch database connection
        result = await db.execute(
            select(UserDatabase).where(
                UserDatabase.id == db_id,
                UserDatabase.owner_id == current_user.id,
                UserDatabase.is_active == True
            )
        )
        user_db = result.scalar_one_or_none()

        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database not found"
            )

        # Decrypt password and create AccessNode connection
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

            # Log schema access
            await audit_manager.log_audit_event(
                db=db,
                action=AuditAction.DATABASE_ACCESS,
                user_id=current_user.id,
                resource="database",
                resource_id=user_db.db_name,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", ""),
                success=True,
                details={
                    "operation": "schema_access",
                    "table_name": table_name or "all_tables"
                }
            )

            return {"schema": schema_info}

        finally:
            await access_node.close()

    except HTTPException:
        raise
    except Exception as e:
        # Log failed schema access
        await audit_manager.log_audit_event(
            db=db,
            action=AuditAction.DATABASE_ACCESS,
            user_id=current_user.id,
            resource="database",
            resource_id=str(db_id),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=False,
            details={
                "operation": "schema_access",
                "error": str(e),
                "table_name": table_name
            }
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch schema information"
        )


# Admin endpoints
@router.get("/admin/audit-logs", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def get_audit_logs_admin(
    request: Request,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    user_id: int = Query(None),
    action: str = Query(None),
    current_user: User = Depends(get_current_user_secure),
    db: AsyncSession = Depends(get_db)
):
    """
    Get audit logs (admin only)
    """
    try:
        # Build query
        from database.models import AuditLog
        query = select(AuditLog).order_by(AuditLog.timestamp.desc())

        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)

        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        audit_logs = result.scalars().all()

        # Log admin access to audit logs
        await audit_manager.log_audit_event(
            db=db,
            action=AuditAction.UNAUTHORIZED_ACCESS,  # This will be a new action type
            user_id=current_user.id,
            resource="audit_logs",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=True,
            details={
                "filters": {"user_id": user_id, "action": action},
                "limit": limit,
                "offset": offset
            }
        )

        return {
            "audit_logs": [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "action": log.action,
                    "resource": log.resource,
                    "resource_id": log.resource_id,
                    "ip_address": log.ip_address,
                    "success": log.success,
                    "timestamp": log.timestamp,
                    "details": log.details
                }
                for log in audit_logs
            ],
            "total_count": len(audit_logs),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch audit logs"
        )