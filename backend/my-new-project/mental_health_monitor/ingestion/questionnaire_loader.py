"""Questionnaire loader for character sketch generation."""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import logging
import json

logger = logging.getLogger(__name__)


class QuestionnaireLoader:
    """Load questionnaire data for character sketch generation."""
    
    def __init__(self, questionnaire_path: Optional[str] = None):
        """Initialize questionnaire loader.
        
        Args:
            questionnaire_path: Path to questionnaire.xlsx file.
                               If None, will search in data/raw/ directory
        """
        if questionnaire_path:
            self.questionnaire_path = Path(questionnaire_path)
        else:
            # Search in common locations
            possible_paths = [
                Path("data/raw/questionnaire.xlsx"),
                Path("../questionnaire.xlsx"),
                Path("./questionnaire.xlsx"),
            ]
            
            # Try to find it
            self.questionnaire_path = None
            for path in possible_paths:
                if path.exists():
                    self.questionnaire_path = path
                    break
    
    def load_questionnaire_data(self) -> Dict:
        """Load questionnaire data from Excel file.
        
        Returns:
            Dictionary with questionnaire responses, or empty dict if file not found
        """
        if not self.questionnaire_path or not self.questionnaire_path.exists():
            logger.warning(f"Questionnaire file not found at {self.questionnaire_path}")
            return self._get_default_questionnaire()
        
        try:
            # Load Excel file
            df = pd.read_excel(str(self.questionnaire_path))
            
            # Convert to dictionary format
            questionnaire_data = {}
            
            # Handle different possible formats
            if 'question' in df.columns and 'answer' in df.columns:
                # Q&A format
                for _, row in df.iterrows():
                    questionnaire_data[row['question']] = row['answer']
            elif 'Question' in df.columns and 'Response' in df.columns:
                # Alternative format
                for _, row in df.iterrows():
                    questionnaire_data[row['Question']] = row['Response']
            else:
                # Try to use first two columns
                cols = df.columns.tolist()
                if len(cols) >= 2:
                    for _, row in df.iterrows():
                        questionnaire_data[row[cols[0]]] = row[cols[1]]
                else:
                    # Fallback to first column
                    questionnaire_data = df.iloc[:, 0].to_dict()
            
            logger.info(f"Loaded questionnaire with {len(questionnaire_data)} items")
            return questionnaire_data
        
        except Exception as e:
            logger.error(f"Error loading questionnaire: {e}")
            return self._get_default_questionnaire()
    
    def format_for_llm(self, questionnaire_data: Dict) -> str:
        """Format questionnaire data for LLM processing.
        
        Args:
            questionnaire_data: Raw questionnaire dictionary
        
        Returns:
            Formatted string for LLM
        """
        if not questionnaire_data:
            return "No questionnaire data available."
        
        formatted = "QUESTIONNAIRE RESPONSES:\n\n"
        for question, answer in questionnaire_data.items():
            formatted += f"Q: {question}\nA: {answer}\n\n"
        
        return formatted
    
    def _get_default_questionnaire(self) -> Dict:
        """Return default questionnaire for demo purposes.
        
        Returns:
            Sample questionnaire data
        """
        return {
            "How do you typically respond to stress?": "I try to solve the problem directly and take action",
            "How important is your social connection?": "Very important - I value close relationships highly",
            "What's your typical sleep schedule?": "Consistent 7-8 hours, go to bed around 10 PM",
            "How often do you interact with friends/family?": "Several times per week",
            "What motivates you the most?": "Helping others and maintaining strong relationships",
            "How would you describe your anxiety levels?": "Moderate - manage well with my current coping strategies",
            "What are your main life goals?": "Career growth, maintaining family bonds, personal wellness",
            "How do you handle changes or uncertainty?": "I adapt but need time to process",
            "What activities bring you joy?": "Spending time with loved ones, exercise, creative pursuits",
            "How would others describe you?": "Reliable, caring, sometimes overthinks things"
        }
