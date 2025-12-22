"""
Seed script to add Phase 2 sample data (Circles, Paths, Resources)
Run with: docker-compose exec backend python seed_phase2.py
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.models import Circle, Path, PathStep, Resource

async def seed_data():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Add Circles
        circles = [
            Circle(
                name="Anxiety Support",
                topic="anxiety",
                description="A safe harbor for those navigating anxiety. Share your wins, struggles, and coping strategies.",
                icon="🌊",
                member_count=0,
                post_count=0
            ),
            Circle(
                name="Grief & Loss",
                topic="grief",
                description="Processing loss together. You don't have to carry it alone.",
                icon="🕯️",
                member_count=0,
                post_count=0
            ),
            Circle(
                name="Daily Gratitude",
                topic="gratitude",
                description="Finding small sparks of joy in the everyday.",
                icon="✨",
                member_count=0,
                post_count=0
            ),
            Circle(
                name="Work Stress",
                topic="burnout",
                description="Navigating burnout, boundaries, and balance in professional life.",
                icon="🌱",
                member_count=0,
                post_count=0
            ),
        ]
        
        for circle in circles:
            session.add(circle)
        
        # Add Paths
        anxiety_path = Path(
            name="Managing Anxiety",
            description="Gentle techniques to ground yourself when overwhelmed.",
            category="anxiety",
            difficulty="beginner",
            estimated_duration=14,  # days
            step_count=7,
            enrollment_count=0
        )
        session.add(anxiety_path)
        await session.flush()
        
        # Add Path Steps for Anxiety
        anxiety_steps = [
            PathStep(
                path_id=anxiety_path.id,
                title="Understanding Your Anxiety",
                description="Learn to recognize your anxiety triggers",
                content="Learn to recognize your anxiety triggers and physical responses.",
                order_index=0,
                step_type="education",
                estimated_minutes=15,
                prompts={"questions": ["What situations make you feel anxious?", "How does anxiety feel in your body?"]},
                resources={"articles": ["Understanding Anxiety"], "videos": []}
            ),
            PathStep(
                path_id=anxiety_path.id,
                title="Breathing Techniques",
                description="Practice calming breathing exercises",
                content="Practice simple breathing exercises to calm your nervous system.",
                order_index=1,
                step_type="practice",
                estimated_minutes=10,
                prompts={"instructions": ["Try 4-7-8 breathing: Inhale for 4, hold for 7, exhale for 8"]},
                resources={"videos": ["Guided Breathing Exercise"]}
            ),
            PathStep(
                path_id=anxiety_path.id,
                title="Grounding with 5 Senses",
                description="Anchor yourself in the present",
                content="Use the 5-4-3-2-1 technique to anchor yourself in the present.",
                order_index=2,
                step_type="exercise",
                estimated_minutes=5,
                prompts={"instructions": ["Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste"]},
                resources={}
            ),
        ]
        
        for step in anxiety_steps:
            session.add(step)
        
        # Add Grief Path
        grief_path = Path(
            name="Coping with Grief",
            description="A safe space to process loss at your own pace.",
            category="grief",
            difficulty="beginner",
            estimated_duration=28,  # days
            step_count=10,
            enrollment_count=0
        )
        session.add(grief_path)
        await session.flush()
        
        # Add Burnout Path
        burnout_path = Path(
            description="Rediscover your energy and set healthy boundaries.",
            name="Burnout Recovery",
            category="burnout",
            difficulty="intermediate",
            estimated_duration=21,  # days
            step_count=12,
            enrollment_count=0
        )
        session.add(burnout_path)
        
        # Add Resources
        resources = [
            Resource(
                title="Rain Sounds for Anxiety",
                description="30 minutes of gentle rain sounds to help calm an anxious mind",
                resource_type="music",
                category="anxiety",
                url="https://example.com/rain-sounds",
                duration_minutes=30,
                difficulty="easy",
                tags=["calming", "nature", "ambient"],
                view_count=0,
                helpful_count=0
            ),
            Resource(
                title="The Body Keeps the Score",
                description="A groundbreaking book on trauma and healing by Bessel van der Kolk",
                resource_type="reading",
                category="general",
                url="https://example.com/body-keeps-score",
                difficulty="moderate",
                tags=["trauma", "healing", "psychology"],
                view_count=0,
                helpful_count=0
            ),
            Resource(
                title="10-Minute Yoga for Stress",
                description="A gentle yoga flow to release tension and find calm",
                resource_type="exercise",
                category="anxiety",
                url="https://example.com/yoga-stress",
                duration_minutes=10,
                difficulty="easy",
                tags=["yoga", "movement", "stress-relief"],
                view_count=0,
                helpful_count=0
            ),
            Resource(
                title="Understanding Depression",
                description="Educational video explaining the science behind depression",
                resource_type="video",
                category="depression",
                url="https://example.com/depression-video",
                duration_minutes=15,
                difficulty="easy",
                tags=["education", "mental-health", "science"],
                view_count=0,
                helpful_count=0
            ),
            Resource(
                title="Grief Support Article",
                description="A compassionate guide to navigating grief and loss",
                resource_type="article",
                category="grief",
                url="https://example.com/grief-support",
                difficulty="easy",
                tags=["grief", "loss", "support"],
                view_count=0,
                helpful_count=0
            ),
        ]
        
        for resource in resources:
            session.add(resource)
        
        await session.commit()
        print("✅ Phase 2 seed data added successfully!")
        print(f"   - {len(circles)} Circles")
        print(f"   - 3 Paths with {len(anxiety_steps)} Anxiety Path steps")
        print(f"   - {len(resources)} Resources")

if __name__ == "__main__":
    asyncio.run(seed_data())
