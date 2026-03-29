"""LLM factory and configuration for Groq-based agents."""

from langchain_groq import ChatGroq
from typing import Optional
import os

from dotenv import load_dotenv

load_dotenv()


class LLMFactory:
    """Factory for creating LLM instances using Groq."""
    
    _instance: Optional[ChatGroq] = None
    
    @staticmethod
    def get_llm() -> ChatGroq:
        """Get or create LLM instance.
        
        Returns:
            ChatGroq instance
        
        Raises:
            ValueError: If GROQ_API_KEY not set
        """
        if LLMFactory._instance is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable not set")
            
            LLMFactory._instance = ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=0.7,
                api_key=api_key
            )
        
        return LLMFactory._instance
    
    @staticmethod
    def reset():
        """Reset LLM instance (for testing)."""
        LLMFactory._instance = None
