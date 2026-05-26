from pymongo import MongoClient
from contextlib import contextmanager
from dotenv import load_dotenv
import os
from database import AsyncSessionLocal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from models.users_models import UserRole
from apps.users.security import SECRET_KEY, ALGORITHM

# This tells FastAPI where the client should send credentials to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

load_dotenv()

@contextmanager
def get_mongo_connection():
    MONGO_URI = os.getenv("MONGO_DB_URI")
    client = MongoClient(MONGO_URI)
    try:
        yield client
    finally:
        client.close()


async def get_postgres_db_connection():
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user_token_data(token: str = Depends(oauth2_scheme)) -> dict:
    """Validates the JWT token and returns the payload data."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        
        if user_id is None or role is None:
            raise credentials_exception
            
        return {"user_id": int(user_id), "role": role}
        
    except JWTError:
        raise credentials_exception


def require_admin_role(current_user: dict = Depends(get_current_user_token_data)) -> dict:
    """Dependency to check if the current user has ADMIN or SUPER_ADMIN role."""
    user_role = current_user.get("role")
    
    # Check if the role is authorized
    if user_role not in [UserRole.ADMIN.name, UserRole.SUPER_ADMIN.name]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action. Admins only."
        )
    return current_user