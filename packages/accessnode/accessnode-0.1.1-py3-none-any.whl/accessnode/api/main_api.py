# """Dynamic API registration and routing system for AccessNode."""

# from typing import Dict, Any, List, Optional
# from fastapi import FastAPI, Depends, HTTPException, Request
# from fastapi.routing import APIRouter
# from sqlalchemy.ext.asyncio import AsyncSession
# from ..core.database import get_db
# from ..core.auth import get_current_user
# from ..core.models import User
# from ..schema_manager.schema_creator import SchemaCreator
# from ..schema_manager.schema_updater import SchemaUpdater

# class DynamicAPIManager:
#     """Manages dynamic API endpoint creation and routing."""
    
#     def __init__(self, app: FastAPI, database_pool):
#         self.app = app
#         self.db_pool = database_pool
#         self.schema_creator = SchemaCreator(database_pool)
#         self.schema_updater = SchemaUpdater(database_pool)
#         self.routers: Dict[str, APIRouter] = {}
        
#     async def register_schema_endpoints(self, schema_definition: Dict[str, Any]) -> str:
#         """
#         Register CRUD endpoints for a new schema.
        
#         Args:
#             schema_definition: Schema definition dictionary
            
#         Returns:
#             schema_id: Unique identifier for the created schema
#         """
#         # Create schema in database
#         schema_id = await self.schema_creator.create_schema(schema_definition)
        
#         # Create router for schema
#         router = self._create_schema_router(schema_definition)
        
#         # Register router with FastAPI app
#         self.routers[schema_id] = router
#         self.app.include_router(
#             router,
#             prefix=f"/api/{schema_definition['name'].lower()}",
#             tags=[schema_definition['name']]
#         )
        
#         return schema_id
        
#     def _create_schema_router(self, schema: Dict[str, Any]) -> APIRouter:
#         """Create an APIRouter with CRUD endpoints for a schema."""
#         router = APIRouter()
#         table_name = schema['name'].lower()
        
#         # CREATE endpoint
#         @router.post("/", response_model=Dict[str, Any])
#         async def create_item(
#             item: Dict[str, Any],
#             db: AsyncSession = Depends(get_db),
#             current_user: User = Depends(get_current_user)
#         ):
#             query = f"INSERT INTO {table_name} "
#             columns = list(item.keys())
#             values = list(item.values())
#             placeholders = [f"${i+1}" for i in range(len(values))]
            
#             query += f"({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
#             query += " RETURNING *"
            
#             try:
#                 result = await db.execute(query, values)
#                 await db.commit()
#                 return dict(result.fetchone())
#             except Exception as e:
#                 await db.rollback()
#                 raise HTTPException(status_code=400, detail=str(e))
                
#         # READ endpoints
#         @router.get("/", response_model=List[Dict[str, Any]])
#         async def get_items(
#             skip: int = 0,
#             limit: int = 100,
#             db: AsyncSession = Depends(get_db),
#             current_user: User = Depends(get_current_user)
#         ):
#             query = f"SELECT * FROM {table_name} OFFSET ${1} LIMIT ${2}"
#             result = await db.execute(query, [skip, limit])
#             return [dict(row) for row in result.fetchall()]
            
#         @router.get("/{item_id}", response_model=Dict[str, Any])
#         async def get_item(
#             item_id: str,
#             db: AsyncSession = Depends(get_db),
#             current_user: User = Depends(get_current_user)
#         ):
#             query = f"SELECT * FROM {table_name} WHERE id = ${1}"
#             result = await db.execute(query, [item_id])
#             item = result.fetchone()
            
#             if not item:
#                 raise HTTPException(status_code=404, detail="Item not found")
#             return dict(item)
            
#         # UPDATE endpoint
#         @router.put("/{item_id}", response_model=Dict[str, Any])
#         async def update_item(
#             item_id: str,
#             item: Dict[str, Any],
#             db: AsyncSession = Depends(get_db),
#             current_user: User = Depends(get_current_user)
#         ):
#             set_values = []
#             values = []
#             for i, (key, value) in enumerate(item.items(), start=1):
#                 set_values.append(f"{key} = ${i}")
#                 values.append(value)
                
#             values.append(item_id)
#             query = f"""
#                 UPDATE {table_name} 
#                 SET {', '.join(set_values)}
#                 WHERE id = ${len(values)}
#                 RETURNING *
#             """
            
#             try:
#                 result = await db.execute(query, values)
#                 await db.commit()
#                 updated_item = result.fetchone()
                
#                 if not updated_item:
#                     raise HTTPException(status_code=404, detail="Item not found")
#                 return dict(updated_item)
#             except Exception as e:
#                 await db.rollback()
#                 raise HTTPException(status_code=400, detail=str(e))
                
#         # DELETE endpoint
#         @router.delete("/{item_id}")
#         async def delete_item(
#             item_id: str,
#             db: AsyncSession = Depends(get_db),
#             current_user: User = Depends(get_current_user)
#         ):
#             query = f"DELETE FROM {table_name} WHERE id = ${1} RETURNING id"
#             result = await db.execute(query, [item_id])
#             deleted_item = result.fetchone()
            
#             if not deleted_item:
#                 raise HTTPException(status_code=404, detail="Item not found")
                
#             await db.commit()
#             return {"message": "Item deleted successfully"}
            
#         # Query endpoint for custom queries
#         @router.post("/query", response_model=List[Dict[str, Any]])
#         async def custom_query(
#             query_data: Dict[str, Any],
#             db: AsyncSession = Depends(get_db),
#             current_user: User = Depends(get_current_user)
#         ):
#             # Validate query to ensure it only affects this table
#             if table_name not in query_data['query'].lower():
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"Query must involve the {table_name} table"
#                 )
                
#             try:
#                 result = await db.execute(
#                     query_data['query'],
#                     query_data.get('parameters', [])
#                 )
                
#                 if query_data['query'].lower().startswith('select'):
#                     return [dict(row) for row in result.fetchall()]
#                 else:
#                     await db.commit()
#                     return [{"affected_rows": result.rowcount}]
#             except Exception as e:
#                 await db.rollback()
#                 raise HTTPException(status_code=400, detail=str(e))
                
#         return router
        
#     async def update_schema_endpoints(
#         self,
#         schema_id: str,
#         updates: Dict[str, Any]
#     ) -> None:
#         """Update endpoints for an existing schema."""
#         # Apply schema updates
#         await self.schema_updater.update_schema(schema_id, updates)
        
#         # Get updated schema definition
#         updated_schema = await self._get_schema_definition(schema_id)
        
#         # Remove old router
#         if schema_id in self.routers:
#             old_router = self.routers[schema_id]
#             self._remove_router(old_router)
            
#         # Create and register new router
#         new_router = self._create_schema_router(updated_schema)
#         self.routers[schema_id] = new_router
#         self.app.include_router(
#             new_router,
#             prefix=f"/api/{updated_schema['name'].lower()}",
#             tags=[updated_schema['name']]
#         )
        
#     async def _get_schema_definition(self, schema_id: str) -> Dict[str, Any]:
#         """Get schema definition from database."""
#         async with self.db_pool.get_connection() as conn:
#             result = await conn.execute(
#                 """
#                 SELECT definition
#                 FROM schema_versions
#                 WHERE schema_id = $1
#                 ORDER BY version DESC
#                 LIMIT 1
#                 """,
#                 [schema_id]
#             )
#             return result['definition']
            
#     def _remove_router(self, router: APIRouter) -> None:
#         """Remove router and its endpoints from the FastAPI app."""
#         routes_to_remove = []
#         for route in self.app.routes:
#             if getattr(route, "router", None) == router:
#                 routes_to_remove.append(route)
                
#         for route in routes_to_remove:
#             self.app.routes.remove(route)
            
# # Initialize API manager in FastAPI app
# def create_app() -> FastAPI:
#     """Create and configure the FastAPI application with dynamic API support."""
#     app = FastAPI(
#         title="AccessNode API",
#         description="Dynamic API endpoints for AccessNode schemas",
#         version="0.1.0"
#     )
    
#     # Initialize database pool
#     from ..core.database import init_db_pool
#     db_pool = init_db_pool()
    
#     # Create API manager
#     api_manager = DynamicAPIManager(app, db_pool)
    
#     # Store API manager in app state
#     app.state.api_manager = api_manager
    
#     # Schema management endpoints
#     @app.post("/schemas/", response_model=Dict[str, str])
#     async def create_schema(
#         schema: Dict[str, Any],
#         current_user: User = Depends(get_current_user)
#     ):
#         """Create a new schema and register its API endpoints."""
#         schema_id = await api_manager.register_schema_endpoints(schema)
#         return {"schema_id": schema_id}
        
#     @app.put("/schemas/{schema_id}")
#     async def update_schema(
#         schema_id: str,
#         updates: Dict[str, Any],
#         current_user: User = Depends(get_current_user)
#     ):
#         """Update an existing schema and its API endpoints."""
#         await api_manager.update_schema_endpoints(schema_id, updates)
#         return {"message": "Schema updated successfully"}
        
#     return app




from fastapi import FastAPI, APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from accessnode.core.auth import get_current_user
from accessnode.api.routers.user import get_existing_user
from accessnode.core.models import User
from accessnode.core.schemas import UserOut, UserCreate
from accessnode.schema_manager.schema_creator import SchemaCreator
from accessnode.schema_manager.schema_updater import SchemaUpdater
from backend.database.db_setup import get_db

class DynamicAPIManager:
    def __init__(self, app: FastAPI, database_pool):
        self.app = app
        self.db_pool = database_pool
        self.schema_creator = SchemaCreator(database_pool)
        self.schema_updater = SchemaUpdater(database_pool)
        self.routers: Dict[str, APIRouter] = {}
        
    async def register_schema_endpoints(self, schema_definition: Dict[str, Any]) -> str:
        """
        Register CRUD endpoints for a new schema.
        
        Args:
            schema_definition: Schema definition dictionary
            
        Returns:
            schema_id: Unique identifier for the created schema
        """
        # Create schema in the database
        schema_id = await self.schema_creator.create_schema(schema_definition)
        
        # Create router for schema
        router = self._create_schema_router(schema_definition)
        
        # Register router with FastAPI app
        self.routers[schema_id] = router
        self.app.include_router(
            router,
            prefix=f"/api/{schema_definition['name'].lower()}",
            tags=[schema_definition['name']]
        )
        
        return schema_id

    def _create_schema_router(self, schema: Dict[str, Any]) -> APIRouter:
        """Create an APIRouter with CRUD endpoints for a schema."""
        router = APIRouter()
        table_name = schema['name'].lower()
        
        # Define endpoints
        @router.post("/", response_model=Dict[str, Any])
        async def create_item(item: Dict[str, Any], db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
            # Example query to insert data into the table
            query = f"INSERT INTO {table_name} ..."
            # Continue with the logic to execute and return a response

        @router.get("/", response_model=List[Dict[str, Any]])
        async def get_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
            # Logic to fetch items
            pass
            
        # Additional CRUD methods (PUT, DELETE, etc.)
        # Modify as needed

        return router
        
    async def register_user_endpoints(self) -> None:
        """Register user-specific API endpoints dynamically."""
        router = APIRouter()

        @router.post("/register", response_model=UserOut)
        async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
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

            return UserOut(id=new_user.id, username=new_user.username)

        @router.post("/token", response_model=Token)
        async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
            # Implement login logic
            pass

        self.app.include_router(router, prefix="/api/users", tags=["Users"])

# Example app initialization
def create_app() -> FastAPI:
    app = FastAPI(
        title="AccessNode API",
        description="Dynamic API endpoints for AccessNode schemas",
        version="0.1.0"
    )
    
    from backend.database.db_setup import init_db_pool
    db_pool = init_db_pool()  # CREATE POOL ON THE database, ALSO USE IT IN THE accessnode.py
    
    api_manager = DynamicAPIManager(app, db_pool)
    
    app.state.api_manager = api_manager
    
    # Register user endpoints
    app.state.api_manager.register_user_endpoints()

    return app
