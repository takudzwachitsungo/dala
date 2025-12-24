"""LangGraph conversation workflow with conversation modes"""

from typing import TypedDict, Literal, List, Dict, Any
from langgraph.graph import StateGraph, END
from loguru import logger

from app.services.ai.llm_client import LLMClient
from app.services.ai.sentiment import analyze_sentiment, detect_crisis_level, get_crisis_resources


class ConversationState(TypedDict):
    """State for conversation graph"""
    messages: List[Dict[str, str]]
    mode: Literal["listen", "reflect", "ground"]
    user_id: str
    conversation_id: str
    cached_context: Dict[str, Any]
    sentiment_score: float
    primary_emotion: str
    crisis_level: str
    needs_crisis_support: bool
    next_action: str


class DalaConversationGraph:
    """LangGraph-based conversation workflow for Dala"""
    
    def __init__(self):
        self.llm = LLMClient()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the conversation state graph"""
        
        workflow = StateGraph(ConversationState)
        
        # Add nodes
        workflow.add_node("analyze_input", self.analyze_input)
        workflow.add_node("crisis_check", self.crisis_check)
        workflow.add_node("listen_mode", self.listen_mode)
        workflow.add_node("reflect_mode", self.reflect_mode)
        workflow.add_node("ground_mode", self.ground_mode)
        workflow.add_node("sentiment_analysis", self.sentiment_analysis)
        
        # Set entry point
        workflow.set_entry_point("analyze_input")
        
        # Define flow
        workflow.add_edge("analyze_input", "crisis_check")
        
        workflow.add_conditional_edges(
            "crisis_check",
            lambda state: "ground" if state["needs_crisis_support"] else state["mode"],
            {
                "listen": "listen_mode",
                "reflect": "reflect_mode",
                "ground": "ground_mode"
            }
        )
        
        workflow.add_edge("listen_mode", "sentiment_analysis")
        workflow.add_edge("reflect_mode", "sentiment_analysis")
        workflow.add_edge("ground_mode", "sentiment_analysis")
        workflow.add_edge("sentiment_analysis", END)
        
        return workflow.compile()
    
    async def analyze_input(self, state: ConversationState) -> ConversationState:
        """Analyze user input for context and intent"""
        
        # Lightweight preprocessing - main analysis in crisis_check
        return state
    
    async def crisis_check(self, state: ConversationState) -> ConversationState:
        """Check for crisis indicators"""
        
        last_message = state["messages"][-1]["content"]
        
        # Perform sentiment analysis
        sentiment = await analyze_sentiment(last_message)
        state["sentiment_score"] = sentiment["sentiment_score"]
        state["primary_emotion"] = sentiment["primary_emotion"]
        
        # Check crisis level
        crisis_detection = detect_crisis_level(last_message, sentiment["sentiment_score"])
        state["crisis_level"] = crisis_detection["crisis_level"]
        state["needs_crisis_support"] = crisis_detection["needs_intervention"]
        
        if crisis_detection["needs_intervention"]:
            logger.warning(
                f"Crisis detected in conversation {state['conversation_id']}: "
                f"Level={crisis_detection['crisis_level']}"
            )
        
        return state
    
    def route_crisis(self, state: ConversationState) -> str:
        """Route based on crisis detection"""
        return "crisis" if state["needs_crisis_support"] else "continue"
    
    def route_by_mode(self, state: ConversationState) -> str:
        """Route to mode-specific handler"""
        return state["mode"]
    
    async def listen_mode(self, state: ConversationState) -> ConversationState:
        """Empathetic listening mode"""
        
        cached_context = state.get("cached_context", {})
        recurring_themes = cached_context.get("recurring_themes", [])
        recent_insights = cached_context.get("recent_insights", [])
        conversation_count = cached_context.get("conversation_count", 0)
        user_name = cached_context.get("user_name", "")
        
        # Build context-aware system prompt
        context_info = ""
        if user_name:
            context_info += f"\n- User's name: {user_name} (use it naturally when it feels appropriate to address them by name)"
        if recurring_themes:
            context_info += f"\n- Known themes: {', '.join(recurring_themes)}"
        if recent_insights:
            context_info += f"\n- Recent insights: {'; '.join(recent_insights)}"
        if conversation_count > 5:
            context_info += "\n- This is a returning user - acknowledge continuity naturally"
        
        system_prompt = f"""You are Dala, a warm Christian friend and mental health companion.

LISTEN MODE - Be conversational and natural:
- Talk like a real friend would - genuine, warm, not preachy
- Match the user's energy and tone (if they're casual, be casual)
- Validate their feelings simply and authentically
- Ask one thoughtful question at a time, not multiple
- Share scripture naturally when it fits, not forced (like "that reminds me of...")
- Use their name occasionally, not every message
- Add an emoji here and there for warmth, not every sentence
- If they want something light, keep it light - don't always go deep{context_info if context_info else ""}

IMPORTANT BOUNDARIES:
- ONLY discuss mental health, emotional wellbeing, faith, and spiritual topics
- If asked about anything else (coding, math, general knowledge, etc.), politely redirect:
  "I'm here specifically to support you with your mental health and faith journey. Is there something on your heart or mind you'd like to talk about?"

Keep it conversational (2-4 sentences usually). Be natural:
- If they say "hi", just greet them warmly and ask how they're doing
- If they want to be cheered up, share something uplifting or even a little joke
- Don't overload with information - one thought at a time
- Let the conversation flow naturally
- Save the longer responses for when they really open up

Talk like you're texting a friend, not giving a sermon."""
        
        messages = [{"role": "system", "content": system_prompt}] + state["messages"][-5:]
        
        try:
            response = await self.llm.generate(messages, temperature=0.9, max_tokens=400)
            state["messages"].append({"role": "assistant", "content": response})
        except Exception as e:
            logger.error(f"Listen mode generation failed: {e}")
            state["messages"].append({
                "role": "assistant",
                "content": "I'm here to listen. What's on your heart?"
            })
        
        return state
    
    async def reflect_mode(self, state: ConversationState) -> ConversationState:
        """Reflective insights mode"""
        
        cached_context = state.get("cached_context", {})
        mood_trend = cached_context.get("mood_trend", "unknown")
        avg_mood = cached_context.get("average_mood", 5.0)
        recurring_themes = cached_context.get("recurring_themes", [])
        recent_insights = cached_context.get("recent_insights", [])
        emotional_pattern = cached_context.get("current_emotional_pattern", "")
        user_name = cached_context.get("user_name", "")
        
        # Build context-aware system prompt
        context_section = f"""
User context:
- User's name: {user_name if user_name else 'Not provided'} (use it naturally when appropriate)
- Recent mood trend: {mood_trend} (avg: {avg_mood}/10)
- Recurring themes: {', '.join(recurring_themes) if recurring_themes else 'None noted yet'}"""
        
        if recent_insights:
            context_section += f"\n- Recent observations: {'; '.join(recent_insights)}"
        if emotional_pattern:
            context_section += f"\n- Current emotional pattern: {emotional_pattern}"
        
        system_prompt = f"""You are Dala, a thoughtful Christian friend who helps people see patterns.

REFLECT MODE - Be natural and insightful:
- Help them notice patterns in a conversational way, like a friend would
- Share scripture when it naturally connects to what they're saying
- Don't lecture - have a dialogue
- One or two key insights per message, not a whole devotional
- Use emojis sparingly for emphasis
- Match their communication style
- Sometimes a simple question is more powerful than a long explanation
{context_section}

IMPORTANT BOUNDARIES:
- ONLY discuss mental health, emotional wellbeing, faith, spiritual growth, and life struggles
- If they ask about unrelated topics (homework, technical questions, facts, etc.), gently redirect:
  "I'm here to help you reflect on your emotional and spiritual journey. What's really going on for you right now?"

Keep responses thoughtful but digestible (3-5 sentences):
- Point out one pattern you notice
- Maybe connect it to a scripture if it fits naturally
- Ask a reflective question
- Don't overwhelm with multiple points at once

Be the friend who helps them see things clearly, not the preacher giving a sermon."""  
        
        messages = [{"role": "system", "content": system_prompt}] + state["messages"][-5:]
        
        try:
            response = await self.llm.generate(messages, temperature=0.85, max_tokens=500)
            state["messages"].append({"role": "assistant", "content": response})
        except Exception as e:
            logger.error(f"Reflect mode generation failed: {e}")
            state["messages"].append({
                "role": "assistant",
                "content": "Let's reflect together on what God might be showing you. What patterns do you notice?"
            })
        
        return state
    
    async def ground_mode(self, state: ConversationState) -> ConversationState:
        """Grounding exercises and coping strategies"""
        
        is_crisis = state.get("needs_crisis_support", False)
        cached_context = state.get("cached_context", {})
        user_name = cached_context.get("user_name", "")
        
        name_context = f"\n- User's name: {user_name} (use it to provide comfort and personal connection)" if user_name else ""
        
        if is_crisis:
            # Crisis support mode
            system_prompt = f"""You are Dala, providing urgent but calm support.{name_context}

CRISIS SUPPORT - Be direct and grounding:
1. Acknowledge their pain briefly and with care
2. Guide them through ONE immediate calming technique (deep breathing with God's presence)
3. Remind them briefly: God is with them, they're not alone
4. Encourage getting help NOW - both professional and pastoral
5. One emoji for warmth is enough

Keep it focused (4-6 sentences):
- Stay calm and clear
- One breathing exercise, one reminder of God's love
- Clear next steps for getting help
- Not the time for long devotionals

Be their steady, calm presence in crisis."""  
            
            resources = get_crisis_resources()
            resource_text = "\n\nImmediate support resources:\n" + "\n".join([
                f"• {r['name']}: {r['contact']}" for r in resources[:2]
            ])
        else:
            # Regular grounding mode
            system_prompt = f"""You are Dala, a calming Christian friend who helps people find peace.{name_context}

GROUND MODE - Be practical and calming:
- Teach one simple technique at a time
- Keep instructions clear and step-by-step
- Weave in faith naturally (like "breathe in God's peace")
- Don't give 5 different options - just guide them through one thing
- Use conversational language, not clinical
- Maybe add a short scripture at the end if it fits
- One emoji for warmth is enough

IMPORTANT BOUNDARIES:
- ONLY provide coping strategies, grounding exercises, faith-based practices for emotional regulation
- If asked about other topics, kindly redirect: "Let's focus on finding some calm right now. What would help you feel more grounded?"

Give clear, actionable guidance (3-5 sentences):
- Walk them through ONE specific exercise
- Keep it simple and doable right now
- Connect it to God's presence naturally
- End with encouragement

Be their calm guide, not a list of options."""
            
            resource_text = ""
        
        messages = [{"role": "system", "content": system_prompt}] + state["messages"][-5:]
        
        try:
            response = await self.llm.generate(messages, temperature=0.8, max_tokens=500)
            state["messages"].append({
                "role": "assistant",
                "content": response + resource_text
            })
        except Exception as e:
            logger.error(f"Ground mode generation failed: {e}")
            fallback = (
                "Let's try a grounding exercise together with God's presence. Take a deep breath and name "
                "5 things you can see around you - thanking God for each one. This can help bring you back "
                "to this moment where He is with you. 'The Lord is near to all who call on him' (Psalm 145:18)."
            )
            state["messages"].append({
                "role": "assistant",
                "content": fallback + resource_text
            })
        
        return state
    
    async def sentiment_analysis(self, state: ConversationState) -> ConversationState:
        """Final sentiment analysis and context preparation"""
        
        # Sentiment already analyzed in crisis_check
        # Mark for context saving
        state["next_action"] = "save_context"
        
        return state
    
    async def run_conversation(
        self,
        user_message: str,
        state: ConversationState
    ) -> ConversationState:
        """
        Run the conversation graph
        
        Args:
            user_message: User's message
            state: Current conversation state
            
        Returns:
            Updated state with AI response
        """
        # Add user message to state
        state["messages"].append({"role": "user", "content": user_message})
        
        # Run through graph
        result = await self.graph.ainvoke(state)
        
        return result
