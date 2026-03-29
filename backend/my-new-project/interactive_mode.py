"""Interactive chat interface - run this in a separate terminal.

This script provides a real-time conversational interface where you can chat
with the support agent while the simulation runs in another terminal.

To use:
    Terminal 1: python simulator.py     (collects weekly indicators)
    Terminal 2: python interactive_mode.py  (chat interface)

Both terminals share the same database, so chat updates in real-time as the
simulator processes each week's analysis.
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
from mental_health_monitor.chat import InteractiveChat


def display_menu():
    """Display the interactive chat menu."""
    print("\n" + "="*60)
    print("MENTAL HEALTH CONVERSATIONAL SUPPORT")
    print("="*60)
    print("\nOptions:")
    print("  [1] Chat with support agent")
    print("  [2] View system state")
    print("  [3] View conversation history")
    print("  [4] View weekly reports")
    print("  [5] Exit")
    print("="*60)


def display_system_state(chat: InteractiveChat):
    """Display current system state."""
    state_info = chat.display_current_state()
    print(f"\n{state_info}")


def view_conversation_history(chat: InteractiveChat):
    """Display conversation history."""
    history = chat.get_conversation_history()
    if not history:
        print("\nNo conversation history yet.")
        return
    
    print("\n" + "="*60)
    print("CONVERSATION HISTORY")
    print("="*60)
    for msg in history:
        role = "You" if msg["role"] == "user" else "Support Agent"
        print(f"\n[{role}] ({msg['timestamp']})")
        print(f"{msg['content']}\n")


def view_weekly_reports():
    """Display available weekly reports."""
    from pathlib import Path
    from mental_health_monitor.reports import ReportGenerator
    
    report_dir = ReportGenerator.REPORT_DIR
    
    if not report_dir.exists():
        print("\nNo reports generated yet. Run the simulator to generate reports.")
        return
    
    reports = sorted(report_dir.glob("week_*.md"))
    
    if not reports:
        print("\nNo weekly reports found.")
        return
    
    print("\n" + "="*60)
    print("WEEKLY REPORTS")
    print("="*60)
    print(f"\nFound {len(reports)} report(s):\n")
    
    for i, report_file in enumerate(reports, 1):
        print(f"[{i}] {report_file.name}")
    
    print("\n[0] Back to menu")
    choice = input("\nSelect report to view (number): ").strip()
    
    try:
        choice_idx = int(choice)
        if choice_idx == 0:
            return
        
        if 1 <= choice_idx <= len(reports):
            report_file = reports[choice_idx - 1]
            
            print("\n" + "="*60)
            with open(report_file, 'r', encoding='utf-8') as f:
                print(f.read())
            print("\n" + "="*60)
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")


def interactive_chat_loop(chat: InteractiveChat):
    """Run interactive chat loop."""
    print("\n" + "="*60)
    print("CHAT MODE - Type 'exit' to return to menu")
    print("="*60)
    
    while True:
        try:
            print("\n\nHow are you feeling right now?")
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'back']:
                print("\nReturning to menu...")
                break
            
            if not user_input:
                print("Please enter a message.")
                continue
            
            print("\nSupport Agent is thinking...")
            response = chat.chat(user_input)
            
            print(f"\nSupport Agent: {response}")
        
        except KeyboardInterrupt:
            print("\n\nReturning to menu...")
            break
        except Exception as e:
            logger.error(f"Error in chat loop: {e}", exc_info=True)
            print("An error occurred. Please try again.")


def main():
    """Main interactive chat interface."""
    logger.info("="*60)
    logger.info("MENTAL HEALTH CONVERSATIONAL SUPPORT - INTERACTIVE MODE")
    logger.info("="*60)
    logger.info("Initializing chat interface...")
    
    try:
        # Validate configuration
        validate_configuration()
        logger.info("Configuration validated")
        
        # Initialize database
        init_database()
        logger.info("Database initialized")
        
        # Initialize chat interface
        logger.info("Initializing conversational agent...")
        chat = InteractiveChat()
        logger.info("Chat interface ready!")
        
        # Display startup info
        print("\n" + "="*60)
        print("MENTAL HEALTH MONITORING SYSTEM")
        print("INTERACTIVE CHAT MODE")
        print("="*60)
        print("\nChat is ready! You can start talking anytime.")
        print("The chat interface will receive updates from the simulator")
        print("running in another terminal.\n")
        
        # Main menu loop
        while True:
            display_menu()
            choice = input("\nEnter option (1-5): ").strip()
            
            if choice == '1':
                interactive_chat_loop(chat)
            elif choice == '2':
                display_system_state(chat)
            elif choice == '3':
                view_conversation_history(chat)
            elif choice == '4':
                view_weekly_reports()
            elif choice == '5':
                print("\nThank you for using the Mental Health Support System.")
                print("Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
