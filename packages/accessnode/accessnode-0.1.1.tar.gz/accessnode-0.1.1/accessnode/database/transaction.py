# from typing import Optional, Any
# from contextlib import asynccontextmanager

# class Transaction:
#     """Handles database transactions with savepoints"""
    
#     def __init__(self, connection):
#         self.connection = connection
#         self.savepoints = []
#         self._transaction = None
    
#     @asynccontextmanager
#     async def begin(self, isolation_level: Optional[str] = None):
#         """Begin a new transaction"""
#         if self._transaction is None:
#             self._transaction = await self.connection.begin()
#             if isolation_level:
#                 await self.connection.execute(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")
        
#         try:
#             yield self
#         except Exception:
#             await self.rollback()
#             raise
    
#     async def commit(self) -> None:
#         """Commit the current transaction"""
#         if self._transaction:
#             await self._transaction.commit()
#             self._transaction = None
    
#     async def rollback(self) -> None:
#         """Rollback the current transaction"""
#         if self._transaction:
#             await self._transaction.rollback()
#             self._transaction = None


# transaction.py
from contextlib import asynccontextmanager
from .pool import ConnectionPool

class TransactionManager:
    @staticmethod
    @asynccontextmanager
    async def transaction(db_type: str, **kwargs):
        connection = await ConnectionPool.create_pool(db_type, **kwargs)
        try:
            async with connection.transaction():
                yield connection
        finally:
            await connection.close()
