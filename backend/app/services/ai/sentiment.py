"""Sentiment analysis and crisis detection using HuggingFace transformers"""

from typing import Dict, List
from functools import lru_cache
import asyncio
from transformers import pipeline
from loguru import logger

from app.core.config import settings


@lru_cache(maxsize=1)
def get_sentiment_analyzer():
    """Lazy load sentiment analysis model (cached)"""
    try:
        return pipeline(
            "text-classification",
            model=settings.SENTIMENT_MODEL,
            top_k=None,
            device=-1  # Use CPU
        )
    except Exception as e:
        logger.error(f"Failed to load sentiment model: {e}")
        return None


async def analyze_sentiment(text: str) -> Dict:
    """
    Analyze sentiment and emotions in text
    
    Args:
        text: Text to analyze
        
    Returns:
        Dict with sentiment_score, primary_emotion, emotions, confidence
    """
    analyzer = get_sentiment_analyzer()
    
    if not analyzer:
        # Fallback if model fails to load
        return {
            "sentiment_score": 0.0,
            "primary_emotion": "neutral",
            "emotions": {},
            "confidence": 0.0
        }
    
    try:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, analyzer, text)
        
        # Process results
        emotions = {item["label"]: item["score"] for item in result[0]}
        primary_emotion = max(emotions.items(), key=lambda x: x[1])
        
        # Calculate overall sentiment score (-1 to 1)
        positive_emotions = ["joy", "surprise", "love"]
        negative_emotions = ["sadness", "anger", "fear", "disgust"]
        
        pos_score = sum(emotions.get(e, 0) for e in positive_emotions)
        neg_score = sum(emotions.get(e, 0) for e in negative_emotions)
        
        # Normalize to -1 to 1 range
        sentiment_score = (pos_score - neg_score) / (pos_score + neg_score + 0.001)
        
        return {
            "sentiment_score": round(sentiment_score, 3),
            "primary_emotion": primary_emotion[0],
            "emotions": {k: round(v, 3) for k, v in emotions.items()},
            "confidence": round(primary_emotion[1], 3)
        }
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return {
            "sentiment_score": 0.0,
            "primary_emotion": "neutral",
            "emotions": {},
            "confidence": 0.0
        }


def detect_crisis_level(text: str, sentiment_score: float) -> Dict:
    """
    Detect crisis level based on keywords and sentiment
    
    Args:
        text: Text to analyze
        sentiment_score: Pre-computed sentiment score
        
    Returns:
        Dict with crisis_level, keywords_found, needs_intervention
    """
    text_lower = text.lower()
    
    # Crisis keywords with severity levels
    high_risk_keywords = [
        "suicide", "kill myself", "end it all", "no reason to live",
        "want to die", "better off dead", "can't go on",
        "self harm", "hurt myself", "cut myself", "end my life",
        "planning to die", "going to kill"
    ]
    
    moderate_risk_keywords = [
        "suicidal", "self-harm", "self harm", "want to hurt",
        "no point in living", "wish i was dead"
    ]
    
    # Check for keywords
    high_keywords_found = [kw for kw in high_risk_keywords if kw in text_lower]
    moderate_keywords_found = [kw for kw in moderate_risk_keywords if kw in text_lower]
    
    # Determine crisis level - MUCH more conservative
    if high_keywords_found or (sentiment_score < -0.85 and len(text.split()) > 10):
        crisis_level = "HIGH"
        needs_intervention = True
    elif moderate_keywords_found or (sentiment_score < -0.75 and any(word in text_lower for word in ["suicide", "harm", "die"])):
        crisis_level = "MODERATE"
        needs_intervention = True
    else:
        # Just feeling low/sad/tired is NOT a crisis
        crisis_level = "LOW" if sentiment_score < -0.5 else "NONE"
        needs_intervention = False
    
    return {
        "crisis_level": crisis_level,
        "keywords_found": high_keywords_found + moderate_keywords_found,
        "needs_intervention": needs_intervention,
        "sentiment_threshold_triggered": sentiment_score < -0.4
    }


def get_crisis_resources() -> List[Dict]:
    """Get crisis support resources for Zimbabwe"""
    return [
        {
            "type": "hotline",
            "name": "Childline Zimbabwe",
            "contact": "116 (toll-free)",
            "description": "24/7 crisis support for children and youth"
        },
        {
            "type": "hotline",
            "name": "Befrienders Zimbabwe",
            "contact": "+263 9 65000 / +263 77 220 0040",
            "description": "Emotional support and suicide prevention"
        },
        {
            "type": "medical",
            "name": "Emergency Services",
            "contact": "999 or 112",
            "description": "Police, ambulance, fire services"
        }
    ]
