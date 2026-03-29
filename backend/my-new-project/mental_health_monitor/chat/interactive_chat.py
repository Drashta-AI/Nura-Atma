"""Interactive chat interface for conversational support agent."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage

from ..llm import LLMFactory, ConversationalAgentPrompt
from ..database import get_session, UserProfile, OverallState
from ..logging_utils import get_llm_response_logger

logger = logging.getLogger(__name__)
llm_logger = get_llm_response_logger()


class InteractiveChat:
    """Interactive chat interface for real-time conversation with support agent."""
    
    def __init__(self):
        """Initialize interactive chat."""
        self.llm = LLMFactory.get_llm()
        self.character_sketch = self._get_character_sketch()
        self.latest_orchestrator_state = self._get_latest_orchestrator_state()
        self.conversation_history = []
    
    def _get_character_sketch(self) -> Dict[str, Any]:
        """Get character sketch from database.
        
        Returns:
            Character sketch dictionary
        """
        session = get_session()
        try:
            profile = session.query(UserProfile).order_by(UserProfile.id.desc()).first()
            if profile and profile.character_sketch_json:
                return profile.character_sketch_json
        except Exception as e:
            logger.error(f"Error retrieving character sketch: {e}")
        finally:
            session.close()
        
        return {
            "personality_summary": "Unknown",
            "coping_style": "Unknown",
            "stress_sensitivity": "moderate",
            "social_dependency": "moderate",
            "motivational_style": "Unknown"
        }
    
    def _get_latest_orchestrator_state(self) -> Optional[Dict[str, Any]]:
        """Get latest state from orchestrator agent.
        
        Returns:
            Latest overall state record or None
        """
        session = get_session()
        try:
            latest = session.query(OverallState).order_by(
                OverallState.week_number.desc()
            ).first()
            if latest:
                return {
                    "week_number": latest.week_number,
                    "final_state": latest.final_state,
                    "behavioural_state": latest.behavioural_state,
                    "physiological_state": latest.physiological_state,
                    "context_state": latest.context_state,
                    "language_state": latest.language_state,
                    "reasoning": latest.orchestrator_reasoning,
                    "message": latest.support_message
                }
        except Exception as e:
            logger.error(f"Error retrieving orchestrator state: {e}")
        finally:
            session.close()
        
        return None
    
    def refresh_orchestrator_state(self):
        """Refresh latest orchestrator state from database."""
        self.latest_orchestrator_state = self._get_latest_orchestrator_state()
        if self.latest_orchestrator_state:
            logger.info(f"Chat interface updated with latest state: {self.latest_orchestrator_state.get('final_state')}")
    
    def get_conversation_context(self) -> str:
        """Build context for the conversational agent about current state.
        
        Returns:
            Context string with latest orchestrator information
        """
        context = ""
        if self.latest_orchestrator_state:
            state = self.latest_orchestrator_state
            context = f"""
LATEST SYSTEM ASSESSMENT (Week {state.get('week_number', 'Unknown')}):
Overall State: {state.get('final_state', 'Unknown')}

Agent Assessments:
- Behavioral: {state.get('behavioural_state', 'Unknown')}
- Physiological: {state.get('physiological_state', 'Unknown')}
- Context: {state.get('context_state', 'Unknown')}
- Language: {state.get('language_state', 'Unknown')}

Analysis Summary:
{state.get('reasoning', 'No analysis available')}
"""
        else:
            context = "\nNo system assessment available yet. Simulation may still be starting."
        
        return context
    
    def chat(self, user_message: str) -> str:
        """Process user message and generate conversational response.
        
        Args:
            user_message: Message from user
        
        Returns:
            Response from conversational agent
        """
        # Refresh orchestrator state before each message
        self.refresh_orchestrator_state()
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            # Get system prompt with character context
            system_prompt = ConversationalAgentPrompt.get_system_prompt(
                self.character_sketch
            )
            
            # Add orchestrator context to the system prompt
            context = self.get_conversation_context()
            system_prompt_with_context = f"{system_prompt}\n{context}"
            
            # Prepare messages for LLM
            messages = [
                SystemMessage(content=system_prompt_with_context),
                HumanMessage(content=user_message)
            ]
            
            # Get response from LLM
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            llm_logger.info(f"[interactive_chat] User message: {user_message}")
            llm_logger.info(f"[interactive_chat] LLM response:\n{response_text}")
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Chat response generated successfully")
            return response_text
        
        except Exception as e:
            logger.error(f"Error generating chat response: {e}", exc_info=True)
            error_message = "I'm having trouble responding right now. Please try again in a moment."
            self.conversation_history.append({
                "role": "assistant",
                "content": error_message,
                "timestamp": datetime.now().isoformat()
            })
            return error_message
    
    def get_conversation_history(self) -> list:
        """Get full conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history
    
    def display_current_state(self) -> str:
        """Display current system state for reference in chat.
        
        Returns:
            Formatted string with current state information
        """
        context = self.get_conversation_context()
        return f"=== CURRENT SYSTEM STATE ==={context}\n=== END STATE ===" if self.latest_orchestrator_state else "No system state available yet."
