"""Scheduler for running agents on a schedule."""
import schedule
import time
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.broken_link_agent import BrokenLinkAgent
from agents.retraction_agent import RetractionAgent
from agents.source_change_agent import SourceChangeAgent
from core.logger import setup_logger

# Set up logging
logger = setup_logger(__name__, log_file='wiki-verify.log')


class AgentScheduler:
    """Schedules and runs WikiVerify agents."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.broken_link_agent = BrokenLinkAgent()
        self.retraction_agent = RetractionAgent()
        self.source_change_agent = SourceChangeAgent()
        self.setup_schedule()
    
    def setup_schedule(self):
        """Set up the agent schedule."""
        # Broken Link Agent: daily at 3 AM
        schedule.every().day.at("03:00").do(self.run_broken_link_agent)
        
        # Retraction Agent: daily at 4 AM
        schedule.every().day.at("04:00").do(self.run_retraction_agent)
        
        # Source Change Agent: weekly on Sunday at 2 AM
        schedule.every().sunday.at("02:00").do(self.run_source_change_agent)
        
        logger.info("Schedule configured:")
        logger.info("  - Broken Link Agent: Daily at 3:00 AM")
        logger.info("  - Retraction Agent: Daily at 4:00 AM")
        logger.info("  - Source Change Agent: Weekly on Sunday at 2:00 AM")
    
    def run_broken_link_agent(self):
        """Run the broken link agent."""
        logger.info("Starting scheduled run: Broken Link Agent")
        try:
            self.broken_link_agent.run(days=7, limit=1000)
            logger.info("Completed: Broken Link Agent")
        except Exception as e:
            logger.error(f"Error running Broken Link Agent: {e}", exc_info=True)
    
    def run_retraction_agent(self):
        """Run the retraction agent."""
        logger.info("Starting scheduled run: Retraction Agent")
        try:
            self.retraction_agent.run(update_cache=True, use_apis=False)
            logger.info("Completed: Retraction Agent")
        except Exception as e:
            logger.error(f"Error running Retraction Agent: {e}", exc_info=True)
    
    def run_source_change_agent(self):
        """Run the source change agent."""
        logger.info("Starting scheduled run: Source Change Agent")
        try:
            self.source_change_agent.run(limit=500)
            logger.info("Completed: Source Change Agent")
        except Exception as e:
            logger.error(f"Error running Source Change Agent: {e}", exc_info=True)
    
    def run_all_agents_now(self):
        """Run all agents immediately (for testing)."""
        logger.info("Running all agents now...")
        self.run_broken_link_agent()
        self.run_retraction_agent()
        self.run_source_change_agent()
        logger.info("All agents completed")
    
    def start(self):
        """Start the scheduler loop."""
        logger.info("WikiVerify Scheduler started")
        logger.info(f"Current time: {datetime.now()}")
        logger.info("Waiting for scheduled tasks...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}", exc_info=True)


def main():
    """Main entry point for the scheduler."""
    import argparse
    
    parser = argparse.ArgumentParser(description='WikiVerify Agent Scheduler')
    parser.add_argument(
        '--run-now',
        action='store_true',
        help='Run all agents immediately instead of scheduling'
    )
    
    args = parser.parse_args()
    
    scheduler = AgentScheduler()
    
    if args.run_now:
        scheduler.run_all_agents_now()
    else:
        scheduler.start()


if __name__ == "__main__":
    main()
