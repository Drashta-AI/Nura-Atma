"""Background simulator - run this in a separate terminal for continuous monitoring.

This script runs the 3-week simulation independently. It can be run in parallel with
the interactive chat interface in another terminal. Both share the same database,
so updates flow to the chat in real-time.

Usage:
    python simulator.py

The conversational agent in interactive_mode.py will automatically receive
updates as each week completes.
"""

import logging
import sys

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

from mental_health_monitor import validate_configuration, init_database
from mental_health_monitor.scheduler import WeeklySimulator


def main():
    """Run the 3-week simulation."""
    logger.info("="*60)
    logger.info("MENTAL HEALTH MONITORING SYSTEM - SIMULATOR")
    logger.info("="*60)
    logger.info("Starting background simulation...")
    logger.info("This collects behavioral, physiological, contextual, and")
    logger.info("language indicators over a 3-week period.")
    logger.info("Updates are saved to the database for the chat interface.")
    print("\n")
    
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        validate_configuration()
        logger.info("✓ Configuration validated")
        
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        logger.info("✓ Database initialized")
        
        # Run simulation
        logger.info("\n" + "="*60)
        logger.info("Starting 3-week simulation...")
        logger.info("="*60)
        logger.info("Week 1: Analyzing behavioral signals...")
        logger.info("Week 2: Analyzing physiological patterns...")
        logger.info("Week 3: Final integrated assessment...")
        logger.info("(Each week takes ~5 minutes)")
        print()
        
        simulator = WeeklySimulator()
        results = simulator.run_simulation()
        
        # Display results
        logger.info("\n" + "="*60)
        logger.info("SIMULATION COMPLETE")
        logger.info("="*60)
        for result in results:
            week = result.get("week_number", "?")
            state = result.get("overall_state", "unknown")
            success = result.get("success", False)
            status = "✓ SUCCESS" if success else "✗ FAILED"
            logger.info(f"Week {week}: {state.upper()} [{status}]")
        
        logger.info("\n" + "="*60)
        logger.info("Weekly reports have been generated in: weekly_reports/")
        logger.info("Start interactive_mode.py in another terminal to:")
        logger.info("  - Chat with the support agent")
        logger.info("  - View weekly reports")
        logger.info("  - See system assessments")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
