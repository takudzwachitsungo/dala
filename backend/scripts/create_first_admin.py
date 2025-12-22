#!/usr/bin/env python3
"""
Script to create initial admin user for the system.
Run this once during initial setup.
Usage: python create_first_admin.py
"""

import sys
import asyncio
from getpass import getpass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import uuid

# Add parent directory to path
sys.path.insert(0, '/app')

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models.user import User


async def create_admin_user(username: str, email: str, password: str):
    """Create the first admin user"""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.is_admin == True)
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print(f"⚠️  Admin user already exists: {existing_admin.username}")
            print(f"   Use promote_admin.py to promote other users")
            return False
        
        # Check if username exists
        result = await session.execute(
            select(User).where(User.username == username)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"❌ Error: Username '{username}' already exists")
            print(f"   Use: python promote_admin.py {username}")
            return False
        
        # Check if email exists
        if email:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            existing_email = result.scalar_one_or_none()
            
            if existing_email:
                print(f"❌ Error: Email '{email}' already exists")
                return False
        
        # Create admin user
        admin_user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_anonymous=False,
            is_admin=True,
            is_moderator=True,
            is_peer_supporter=True,
            role='admin',
            privacy_consent=True
        )
        
        session.add(admin_user)
        await session.commit()
        
        print(f"✅ Successfully created admin user!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Role: admin")
        print(f"\n🔐 Save these credentials securely:")
        print(f"   Login URL: http://localhost:5173/login")
        print(f"   Username: {username}")
        print(f"   Password: [hidden]")
        
        return True


def main():
    print("=" * 60)
    print("Create First Admin User")
    print("=" * 60)
    print()
    
    # Get user input
    username = input("Admin username: ").strip()
    if not username or len(username) < 3:
        print("❌ Username must be at least 3 characters")
        sys.exit(1)
    
    email = input("Admin email: ").strip()
    if not email or '@' not in email:
        print("❌ Invalid email address")
        sys.exit(1)
    
    password = getpass("Admin password (min 8 chars): ").strip()
    if not password or len(password) < 8:
        print("❌ Password must be at least 8 characters")
        sys.exit(1)
    
    password_confirm = getpass("Confirm password: ").strip()
    if password != password_confirm:
        print("❌ Passwords do not match")
        sys.exit(1)
    
    print()
    print("Creating admin user...")
    
    success = asyncio.run(create_admin_user(username, email, password))
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
