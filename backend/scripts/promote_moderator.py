"""Script to promote a user to moderator role"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import sys

from app.core.config import settings
from app.db.models.user import User


async def promote_to_moderator(username: str):
    """Promote user to moderator role"""
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True
    )
    
    # Create session factory
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
            print(f"❌ User '{username}' not found")
            return
        
        # Update role
        user.role = 'moderator'
        user.is_moderator = True
        user.is_peer_supporter = True
        
        await session.commit()
        
        print(f"✅ User '{username}' promoted to moderator!")
        print(f"   - Role: {user.role}")
        print(f"   - Is Moderator: {user.is_moderator}")
        print(f"   - Is Peer Supporter: {user.is_peer_supporter}")
    
    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promote_moderator.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    asyncio.run(promote_to_moderator(username))
