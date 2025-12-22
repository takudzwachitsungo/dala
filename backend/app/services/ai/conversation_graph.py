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
        
        system_prompt = f"""You are Dala, a compassionate mental health companion.

LISTEN MODE - Your role:
- Provide empathetic, non-judgmental listening
- Validate feelings without trying to fix them
- Ask gentle, open-ended questions to help the person explore their feelings
- Mirror emotions to show understanding
- Avoid giving advice unless explicitly asked
- Focus on being present and supportive
- When appropriate, address the user by their name to create a personal connection{context_info if context_info else ""}

Keep responses warm, concise (2-3 sentences), and focused on the user's emotional experience.
Use a calm, gentle tone. Reference past themes naturally if relevant, but don't force it."""
        
        messages = [{"role": "system", "content": system_prompt}] + state["messages"][-5:]
        
        try:
            response = await self.llm.generate(messages, temperature=0.7)
            state["messages"].append({"role": "assistant", "content": response})
        except Exception as e:
            logger.error(f"Listen mode generation failed: {e}")
            state["messages"].append({
                "role": "assistant",
                "content": "I'm here to listen. Tell me more about what you're experiencing."
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
        
        system_prompt = f"""You are Dala, a reflective mental health companion.

REFLECT MODE - Your role:
- Help the user identify patterns in their thoughts and behaviors
- Gently challenge cognitive distortions when appropriate
- Ask thought-provoking questions that encourage self-awareness
- Connect current feelings to past experiences when relevant
- Encourage reflection on what might be helpful
{context_section}

Provide gentle insights while remaining supportive. 2-4 sentences.
Be curious and help them see patterns, not prescriptive. If you notice recurring themes from past conversations, gently highlight connections."""
        
        messages = [{"role": "system", "content": system_prompt}] + state["messages"][-5:]
        
        try:
            response = await self.llm.generate(messages, temperature=0.7)
            state["messages"].append({"role": "assistant", "content": response})
        except Exception as e:
            logger.error(f"Reflect mode generation failed: {e}")
            state["messages"].append({
                "role": "assistant",
                "content": "Let's reflect on this together. What patterns do you notice in how you're feeling?"
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
            system_prompt = f"""You are Dala, providing crisis support.{name_context}

CRISIS SUPPORT:
1. Acknowledge their pain with compassion
2. Immediately provide a grounding technique:
   - 5-4-3-2-1 method (5 things you see, 4 things you touch, etc.)
   - Deep breathing (breathe in for 4, hold for 4, out for 4)
   - Progressive muscle relaxation
3. Gently encourage seeking immediate professional help
4. Remind them they're not alone

Be calm, direct, compassionate, and practical.
Focus on immediate safety and coping."""
            
            resources = get_crisis_resources()
            resource_text = "\n\nImmediate support resources:\n" + "\n".join([
                f"• {r['name']}: {r['contact']}" for r in resources[:2]
            ])
        else:
            # Regular grounding mode
            system_prompt = f"""You are Dala, a grounding-focused mental health companion.{name_context}

GROUND MODE - Your role:
- Guide through grounding exercises (5-4-3-2-1, breathing)
- Teach practical coping techniques
- Offer mindfulness practices
- Help reconnect to the present moment
- Provide actionable, step-by-step strategies
- Use the user's name when appropriate to create a calming, personal connection

Be practical and instructive. 3-4 sentences.
Give specific techniques they can try right now."""
            
            resource_text = ""
        
        messages = [{"role": "system", "content": system_prompt}] + state["messages"][-5:]
        
        try:
            response = await self.llm.generate(messages, temperature=0.6)
            state["messages"].append({
                "role": "assistant",
                "content": response + resource_text
            })
        except Exception as e:
            logger.error(f"Ground mode generation failed: {e}")
            fallback = (
                "Let's try a grounding exercise together. Can you name 5 things you can see "
                "around you right now? This can help bring you back to the present moment."
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
