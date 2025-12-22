#!/usr/bin/env python3
"""
Script to promote a user to admin role.
Usage: python promote_admin.py <username>
"""

import sys
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, '/app')

from app.core.config import settings
from app.db.models.user import User


async def promote_to_admin(username: str):
    """Promote a user to admin role"""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Find user
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ Error: User '{username}' not found")
            return False
        
        # Update to admin
        user.role = 'admin'
        user.is_admin = True
        user.is_moderator = True  # Admins also have moderator privileges
        user.is_peer_supporter = True  # Admins can act as peer supporters
        
        await session.commit()
        
        print(f"✅ Successfully promoted user '{username}' to admin")
        print(f"   Role: {user.role}")
        print(f"   is_admin: {user.is_admin}")
        print(f"   is_moderator: {user.is_moderator}")
        print(f"   is_peer_supporter: {user.is_peer_supporter}")
        
        return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python promote_admin.py <username>")
        print("\nExample:")
        print("  python promote_admin.py john_doe")
        sys.exit(1)
    
    username = sys.argv[1]
    
    print(f"Promoting user '{username}' to admin...")
    success = asyncio.run(promote_to_admin(username))
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
