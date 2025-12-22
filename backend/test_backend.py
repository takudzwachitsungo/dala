"""Test script to verify backend setup"""

import asyncio
import httpx
from loguru import logger


BASE_URL = "http://localhost:8000"


async def test_backend():
    """Test backend endpoints"""
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health check
        logger.info("Testing health endpoint...")
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        logger.success(f"✓ Health check passed: {response.json()}")
        
        # Test 2: Create anonymous session
        logger.info("Testing anonymous session creation...")
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/anonymous-session",
            json={"privacy_consent": True}
        )
        assert response.status_code == 201
        data = response.json()
        token = data["access_token"]
        user_id = data["user"]["id"]
        logger.success(f"✓ Anonymous session created: {user_id}")
        
        # Test 3: Log mood entry
        logger.info("Testing mood entry...")
        response = await client.post(
            f"{BASE_URL}/api/v1/mood",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "mood_score": 7,
                "emotions": ["calm", "focused"],
                "notes": "Test mood entry"
            }
        )
        assert response.status_code == 201
        logger.success(f"✓ Mood entry created: {response.json()['id']}")
        
        # Test 4: Get profile
        logger.info("Testing profile retrieval...")
        response = await client.get(
            f"{BASE_URL}/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        profile = response.json()
        logger.success(f"✓ Profile retrieved: {profile['username']}")
        logger.info(f"  Streak: {profile['streak_days']} days")
        logger.info(f"  Milestones: {profile['milestone_count']}")
        
        # Test 5: Create conversation
        logger.info("Testing conversation creation...")
        response = await client.post(
            f"{BASE_URL}/api/v1/conversations",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "mode": "listen",
                "title": "Test Conversation"
            }
        )
        assert response.status_code == 201
        conversation_id = response.json()["id"]
        logger.success(f"✓ Conversation created: {conversation_id}")
        
        # Test 6: Get mood history
        logger.info("Testing mood history...")
        response = await client.get(
            f"{BASE_URL}/api/v1/mood/history?days=7",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        history = response.json()
        logger.success(f"✓ Mood history retrieved: {history['total_entries']} entries")
        logger.info(f"  Average: {history['average_score']}")
        logger.info(f"  Trend: {history['trend']}")
        
        logger.success("\n✓ All tests passed! Backend is working correctly.")
        logger.info(f"\nYou can now test WebSocket chat:")
        logger.info(f"  Conversation ID: {conversation_id}")
        logger.info(f"  Access Token: {token}")


if __name__ == "__main__":
    try:
        asyncio.run(test_backend())
    except Exception as e:
        logger.error(f"✗ Test failed: {e}")
        raise
