"""Authentication endpoints"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    Token,
    UserResponse,
    AnonymousSessionCreate
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)


router = APIRouter()


@router.post("/anonymous-session", response_model=Token, status_code=status.HTTP_201_CREATED)
async def create_anonymous_session(
    data: AnonymousSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create anonymous session without registration"""
    
    # Generate anonymous username
    anonymous_id = str(uuid.uuid4())[:8]
    username = f"anonymous_{anonymous_id}"
    
    # Create anonymous user
    user = User(
        username=username,
        is_anonymous=True,
        privacy_consent=data.privacy_consent,
        privacy_consent_date=datetime.utcnow() if data.privacy_consent else None
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register new user account"""
    
    # Check if converting from anonymous
    existing_user = None
    if user_data.anonymous_token:
        payload = decode_access_token(user_data.anonymous_token)
        if payload:
            user_id = payload.get("sub")
            result = await db.execute(select(User).where(User.id == user_id))
            existing_user = result.scalar_one_or_none()
            
            if existing_user and not existing_user.is_anonymous:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already registered"
                )
    
    # Check username uniqueness
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check email uniqueness if provided
    if user_data.email:
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    if existing_user:
        # Convert anonymous user to registered
        existing_user.username = user_data.username
        existing_user.email = user_data.email
        existing_user.hashed_password = get_password_hash(user_data.password) if user_data.password else None
        existing_user.is_anonymous = False
        existing_user.privacy_consent = user_data.privacy_consent
        existing_user.privacy_consent_date = datetime.utcnow()
        
        await db.commit()
        await db.refresh(existing_user)
        user = existing_user
    else:
        # Create new user
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password) if user_data.password else None,
            is_anonymous=False,
            privacy_consent=user_data.privacy_consent,
            privacy_consent_date=datetime.utcnow() if user_data.privacy_consent else None
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login with username/email and password"""
    
    # Find user by username or email
    result = await db.execute(
        select(User).where(
            (User.username == login_data.identifier) | 
            (User.email == login_data.identifier)
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )
    
    if user.is_anonymous:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anonymous users cannot login. Please register first."
        )
    
    # Verify password
    if not user.hashed_password or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
async def logout():
    """Logout (client should discard token)"""
    return {"message": "Successfully logged out"}
