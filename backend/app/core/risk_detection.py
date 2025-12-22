"""Advanced risk detection for user safety"""

import re
from typing import Dict, List, Tuple
from datetime import datetime


class RiskDetector:
    """Detects mental health crisis indicators in user messages"""
    
    # Risk indicators with severity weights
    CRITICAL_PATTERNS = [
        (r'\b(kill|end|take)\s+(my|myself|my\s+own)\s+life\b', 'suicidal_ideation'),
        (r'\b(suicide|suicidal)\b', 'suicidal_mention'),
        (r'\b(don\'t|dont)\s+want\s+to\s+(live|be\s+alive|exist)', 'life_negation'),
        (r'\b(plan|planning)\s+to\s+(die|kill|end)', 'suicide_plan'),
    ]
    
    HIGH_RISK_PATTERNS = [
        (r'\b(can\'t|cant|cannot)\s+(go\s+on|keep\s+going|do\s+this)', 'despair'),
        (r'\b(hopeless|no\s+hope|pointless)\b', 'hopelessness'),
        (r'\b(hurt|harm)\s+(myself|me)\b', 'self_harm'),
        (r'\b(give\s+up|giving\s+up)\b', 'resignation'),
        (r'\b(better\s+off\s+dead|world.*better.*without\s+me)\b', 'worthlessness'),
    ]
    
    MEDIUM_RISK_PATTERNS = [
        (r'\b(worthless|useless|burden)\b', 'negative_self_worth'),
        (r'\b(exhausted|tired\s+of\s+everything|drained)\b', 'emotional_exhaustion'),
        (r'\b(isolated|alone|lonely)\b', 'isolation'),
        (r'\b(numb|empty|void)\b', 'emotional_numbness'),
    ]
    
    # Protective factors (reduce risk score)
    PROTECTIVE_PATTERNS = [
        (r'\b(help|support|therapy|therapist|counselor)\b', 'seeking_help'),
        (r'\b(friend|family|loved\s+ones)\b', 'social_connection'),
        (r'\b(tomorrow|future|next\s+week|plans)\b', 'future_orientation'),
        (r'\b(better|improving|getting\s+through)\b', 'positive_outlook'),
    ]
    
    @staticmethod
    def analyze_message(content: str, sentiment_score: float = None) -> Dict:
        """
        Analyze message for risk indicators
        
        Returns:
            {
                'risk_score': float (0-1),
                'risk_level': str (low/medium/high/critical),
                'indicators': List[str],
                'requires_escalation': bool
            }
        """
        content_lower = content.lower()
        indicators = []
        risk_score = 0.0
        
        # Check critical patterns (0.8-1.0)
        for pattern, indicator_type in RiskDetector.CRITICAL_PATTERNS:
            if re.search(pattern, content_lower):
                indicators.append(indicator_type)
                risk_score = max(risk_score, 0.9)
        
        # Check high risk patterns (0.6-0.8)
        for pattern, indicator_type in RiskDetector.HIGH_RISK_PATTERNS:
            if re.search(pattern, content_lower):
                indicators.append(indicator_type)
                risk_score = max(risk_score, 0.7)
        
        # Check medium risk patterns (0.3-0.6)
        for pattern, indicator_type in RiskDetector.MEDIUM_RISK_PATTERNS:
            if re.search(pattern, content_lower):
                indicators.append(indicator_type)
                risk_score = max(risk_score, 0.4)
        
        # Factor in sentiment score if available
        if sentiment_score is not None and sentiment_score < 0:
            # Very negative sentiment increases risk
            sentiment_factor = abs(sentiment_score) * 0.3
            risk_score = min(1.0, risk_score + sentiment_factor)
        
        # Check for protective factors (reduce score)
        protective_count = 0
        for pattern, _ in RiskDetector.PROTECTIVE_PATTERNS:
            if re.search(pattern, content_lower):
                protective_count += 1
        
        if protective_count > 0:
            risk_score = max(0.0, risk_score - (protective_count * 0.1))
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = 'critical'
            requires_escalation = True
        elif risk_score >= 0.6:
            risk_level = 'high'
            requires_escalation = True
        elif risk_score >= 0.3:
            risk_level = 'medium'
            requires_escalation = False
        else:
            risk_level = 'low'
            requires_escalation = False
        
        return {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'indicators': list(set(indicators)),  # Remove duplicates
            'requires_escalation': requires_escalation
        }
    
    @staticmethod
    def get_crisis_resources() -> Dict[str, str]:
        """Return crisis hotline information"""
        return {
            'us_crisis_line': '988',
            'us_crisis_text': 'Text HOME to 741741',
            'international': 'https://findahelpline.com',
            'emergency': '911 or local emergency services'
        }
    
    @staticmethod
    def should_update_user_risk_level(
        user_risk_history: List[float],
        current_score: float,
        threshold: float = 0.6
    ) -> Tuple[bool, str]:
        """
        Determine if user's overall risk level should be updated
        
        Args:
            user_risk_history: Recent risk scores for this user
            current_score: Current message risk score
            threshold: Threshold for concern
            
        Returns:
            (should_update, new_risk_level)
        """
        if not user_risk_history:
            user_risk_history = []
        
        # Add current score
        recent_scores = user_risk_history[-5:] + [current_score]
        avg_score = sum(recent_scores) / len(recent_scores)
        
        # Determine user's overall risk level
        if current_score >= 0.8 or avg_score >= 0.7:
            return True, 'critical'
        elif current_score >= 0.6 or avg_score >= 0.5:
            return True, 'high'
        elif avg_score >= 0.3:
            return True, 'medium'
        else:
            return False, 'low'
