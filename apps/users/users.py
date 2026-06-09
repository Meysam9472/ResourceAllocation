from fastapi import APIRouter, Depends, HTTPException, status, Body
from dependencies import get_postgres_db_connection as get_db

from schemas.users_schema import UserCreate, UserResponse, RefreshTokenRequest
from schemas.users_schema import AddCreditRequest, UserResetPassword

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import AsyncSessionLocal
from models.users_models import User

from jose import JWTError, jwt
from .security import create_access_token, REFRESH_SECRET_KEY, ALGORITHM
from .security import verify_password, create_refresh_token, get_password_hash

from models.users_models import UserRole

from dependencies import require_admin_role, get_current_user_token_data
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/users", tags=["Users"])


@router.post('/sing-up', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user.
    """
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user_in.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Hash the password and save the user
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        username=user_in.username,
        hashed_password=hashed_password,
        role=user_in.role
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post('/reset-user-password', status_code=status.HTTP_200_OK)
async def reset_user_password(
    req: UserResetPassword,
    current_user: dict = Depends(get_current_user_token_data),
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Fetch user
        user_data = await db.get(User, req.user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        
        current_user_role = current_user.get("role")
        current_user_id = int(current_user.get("user_id"))
        
        # 2. Check Permissions
        is_admin = current_user_role in [UserRole.ADMIN.name, UserRole.SUPER_ADMIN.name]
        is_owner = user_data.id == current_user_id

        if not is_admin and not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to change this password."
            )

        # 3. Password Verification Logic
        if is_admin:
            # Admin can reset any password without verification
            pass 
        else:
            # Regular users MUST provide and verify current password
            if not req.current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is required for non-admin users."
                )
            
            if not verify_password(req.current_password, user_data.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect."
                )

        # 4. Check if new password is same as old one (Optional but recommended)
        # Note: Admin might not care about this, but let's keep it for owners
        if req.current_password == req.new_password:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password cannot be the same as current password."
            )

        # 5. Update password
        user_data.hashed_password = get_password_hash(req.new_password)
        
        await db.commit()
        
        return {"status": "success", "message": f"Password updated by {'Admin' if is_admin else 'Owner'}."}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while resetting the password."
        )


@router.get("/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                     current_admin: dict = Depends(require_admin_role)):
    """
    Get a list of users.
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db), 
                    current_user: int=Depends(get_current_user_token_data)):
    """
    Get a specific user by ID.
    """
    current_user_role = current_user.get("role")
    current_user_id = int(current_user.get("user_id"))
    
    if current_user_role not in [UserRole.ADMIN.name, UserRole.SUPER_ADMIN.name]:
        if user_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not allowed to perform this action.")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db),
                      current_admin: dict = Depends(require_admin_role)):
    """
    Delete a user by ID.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    return None


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return both access and refresh tokens.
    Uses OAuth2PasswordRequestForm which expects 'username' and 'password' in the form data.
    """
    
    # 1. Query the database to find the user by the provided username
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()

    # 2. Verify if the user exists and the provided password matches the hashed password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Generate both tokens
    # We cast user.id to string because the 'sub' (subject) claim in JWT is typically a string
    # user.role.name assumes your role is defined as an Enum in SQLAlchemy
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.name}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "role": user.role.name}
    )
    
    # 4. Return the tokens to the client
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token(request_data: RefreshTokenRequest):
    """
    Takes a valid refresh token and returns a new access token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the refresh token using the REFRESH_SECRET_KEY
        payload = jwt.decode(request_data.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        
        if user_id is None or role is None:
            raise credentials_exception
            
        # If valid, generate a NEW access token
        new_access_token = create_access_token(data={"sub": str(user_id), "role": role})
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        # If the refresh token is expired or invalid, the user MUST log in again
        raise credentials_exception


@router.post("/change-user-credit", status_code=status.HTTP_200_OK)
async def change_user_credit(req: AddCreditRequest, db: AsyncSession = Depends(get_db),
                    current_admin: dict = Depends(require_admin_role)):
    """
    Add credit for a user. Amount value can be negative for decreasing user's credite.
    """
    try:
        user_data = await db.get(User, req.user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {req.user_id} not found"
            ) 

        new_amount = user_data.credit + req.amount
        if new_amount < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Credit amount must be at least 0. The new amount will make credit lower than 0.")

        user_data.credit = new_amount
        
        await db.commit()
        await db.refresh(user_data)
        
        return {
            "status": "success",
            "user_id": user_data.id,
            "new_credit": user_data.credit
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the user."
        )


@router.get("/get-user-credit/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_credit(user_id: int, db: AsyncSession = Depends(get_db),
                          current_admin: dict = Depends(require_admin_role)):
    """
    Get credit of a user by id.
    """
    try:
        user_data = await db.get(User, user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            ) 
        
        return {"message": f"Credit is {user_data.credit} for user with id={user_data.id}."}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while getting the user."
        )