"""Main orchestration script for mental health monitoring system."""

import logging
import sys
import json
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mental_health_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

from mental_health_monitor import (
    init_database,
    validate_configuration,
)
from mental_health_monitor.ingestion import ExcelDataLoader, BaselineEngine
from mental_health_monitor.scheduler import WeeklySimulator
from mental_health_monitor.database import get_session, UserProfile


def setup_character_sketch():
    """Generate and store character sketch from questionnaire.
    
    Returns:
        Character sketch dictionary
    """
    from mental_health_monitor.llm import LLMFactory, CharacterSketchPrompt
    from mental_health_monitor.ingestion import QuestionnaireLoader
    from langchain_core.messages import HumanMessage, SystemMessage
    import json
    import re
    
    logger.info("Generating character sketch from questionnaire...")
    
    try:
        # Load questionnaire data
        loader = QuestionnaireLoader()
        questionnaire_data = loader.load_questionnaire_data()
        questionnaire_text = loader.format_for_llm(questionnaire_data)
        
        # Get LLM
        llm = LLMFactory.get_llm()
        
        # Get character sketch prompt
        prompt_template = CharacterSketchPrompt.get_prompt()
        
        # Format prompt with questionnaire data
        system_prompt = "You are a psychology expert creating detailed character sketches."
        user_prompt = prompt_template.format(questionnaire_data=questionnaire_text)
        
        # Call LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        response_text = response.content.strip()
        
        # Parse JSON response
        try:
            character_sketch = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                character_sketch = json.loads(json_match.group())
            else:
                logger.warning("Could not parse LLM response, using default")
                character_sketch = {
                    "personality_summary": "Individual with balanced social engagement",
                    "coping_style": "Problem-focused with emotion regulation",
                    "stress_sensitivity": "moderate",
                    "social_dependency": "moderate",
                    "motivational_style": "connection"
                }
        
        # Ensure all required fields
        character_sketch.setdefault("personality_summary", "Unknown")
        character_sketch.setdefault("coping_style", "Unknown")
        character_sketch.setdefault("stress_sensitivity", "moderate")
        character_sketch.setdefault("social_dependency", "moderate")
        character_sketch.setdefault("motivational_style", "Unknown")
        
        logger.info("Character sketch generated successfully")
        return character_sketch
    
    except Exception as e:
        logger.error(f"Error generating character sketch: {e}", exc_info=True)
        # Return default
        return {
            "personality_summary": "Unknown",
            "coping_style": "Unknown",
            "stress_sensitivity": "moderate",
            "social_dependency": "moderate",
            "motivational_style": "Unknown"
        }


def setup_baseline():
    """Compute and store baseline metrics.
    
    Returns:
        Baseline metrics dictionary
    """
    logger.info("Computing baseline metrics (28-03-2013 to 03-04-2013)...")
    
    try:
        # Initialize data loader
        loader = ExcelDataLoader()
        
        # Compute baseline
        baseline_engine = BaselineEngine(loader)
        baseline = baseline_engine.compute_baseline()
        
        # Save to database
        baseline_engine.save_baseline_to_db(baseline)
        
        logger.info(f"Baseline computed with {len(baseline)} metrics")
        for metric, value in baseline.items():
            logger.info(f"  {metric}: {value:.2f}")
        
        return baseline
    
    except Exception as e:
        logger.error(f"Error computing baseline: {e}")
        raise


def run_monitoring_simulation():
    """Run the complete 3-week monitoring simulation.
    
    Returns:
        List of results for each week
    """
    logger.info("Starting 3-week monitoring simulation...")
    
    try:
        simulator = WeeklySimulator()
        results = simulator.run_simulation()
        return results
    
    except Exception as e:
        logger.error(f"Error running simulation: {e}", exc_info=True)
        raise


def print_results(results):
    """Print simulation results.
    
    Args:
        results: List of week results
    """
    print("\n" + "="*80)
    print("MENTAL HEALTH MONITORING SIMULATION RESULTS")
    print("="*80 + "\n")
    
    for result in results:
        week = result.get("week_number", "?")
        state = result.get("overall_state", "unknown")
        success = result.get("success", False)
        
        print(f"Week {week}: {state.upper()} {'✓' if success else '✗'}")
        
        if success:
            message = result.get("support_message", "")
            if message:
                print(f"  Support Message: {message[:100]}...")
        else:
            error = result.get("error", "Unknown error")
            print(f"  Error: {error}")
        
        print()


def main():
    """Main orchestration function."""
    
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        validate_configuration()
        
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        
        # Setup character sketch
        logger.info("Setting up character profile...")
        character_sketch = setup_character_sketch()
        
        # Store in database
        session = get_session()
        try:
            # Clear existing profiles
            session.query(UserProfile).delete()
            session.commit()
            
            # Add new profile
            profile = UserProfile(character_sketch_json=character_sketch)
            session.add(profile)
            session.commit()
            logger.info("Character profile stored in database")
        finally:
            session.close()
        
        # Setup baseline
        logger.info("Setting up baseline metrics...")
        baseline = setup_baseline()
        
        # Run simulation
        logger.info("Running monitoring simulation...")
        results = run_monitoring_simulation()
        
        # Print results
        print_results(results)
        
        # Save results to file
        with open("simulation_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info("Results saved to simulation_results.json")
        
        logger.info("Simulation complete!")
        return 0
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
