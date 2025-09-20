# schemas.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str

class UserDatabaseBase(BaseModel):
    db_name: str
    db_type: str
    host: str
    port: Optional[int]
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)

class UserDatabaseCreate(UserDatabaseBase):
    pass

class UserDatabaseOut(BaseModel):
    id: int
    db_name: str
    db_type: str
    host: str
    port: int
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)

class UserOut(BaseModel):
    id: int
    username: str
    databases: List[UserDatabaseOut] = []

    model_config = ConfigDict(from_attributes=True)

class QueryRequest(BaseModel):
    query: str
