# db_utilities.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User, UserDatabase
from .schemas import UserCreate, UserDatabaseOut, UserDatabaseCreate
from utils.utils import get_password_hash
from typing import List
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

async def check_db_connection(db_info: UserDatabaseCreate) -> bool:
    if db_info.db_type == "mysql":
        db_url = f"mysql+aiomysql://{db_info.username}:{db_info.password}@{db_info.host}:{db_info.port}/{db_info.db_name}"
    elif db_info.db_type == "postgresql":
        db_url = f"postgresql+asyncpg://{db_info.username}:{db_info.password}@{db_info.host}:{db_info.port}/{db_info.db_name}"
    elif db_info.db_type == "mongodb":
        pass
    else:
        raise ValueError(f"Unsupported database type: {db_info.db_type}")
    
    engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
    
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            return True
    except SQLAlchemyError as e:
        print(f"Database connection error: {str(e)}")
        return False
    finally:
        await engine.dispose()

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_databases(db: AsyncSession, user_id: int) -> List[UserDatabaseOut]:
    result = await db.execute(select(UserDatabase).where(UserDatabase.owner_id == user_id))
    databases = result.scalars().all()
    return [UserDatabaseOut(
        id=db.id,
        db_name=db.db_name,
        db_type=db.db_type,
        host=db.host,
        port=db.port,
        username=db.username,
        password=db.password if isinstance(db.password, str) else db.password.decode('utf-8')
    ) for db in databases]
