"""Scheduler for running WikiVerify cycles on a schedule."""
import schedule
import time
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import setup_logger

# Set up logging
logger = setup_logger(__name__, log_file='wiki-verify.log')


class WikiVerifyScheduler:
    """Schedules and runs WikiVerify cycles (monthly, weekly, daily)."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.setup_schedule()
    
    def setup_schedule(self):
        """Set up the cycle schedule."""
        # Monthly cycle: 1st of each month at 2 AM
        schedule.every().month.do(self.run_monthly_cycle).tag("monthly")
        
        # Weekly cycle: Every Monday at 3 AM
        schedule.every().monday.at("03:00").do(self.run_weekly_cycle)
        
        # Daily cycle: Every day at 6 AM
        schedule.every().day.at("06:00").do(self.run_daily_cycle)
        
        logger.info("Schedule configured:")
        logger.info("  - Monthly cycle: 1st of each month at 2:00 AM")
        logger.info("  - Weekly cycle: Every Monday at 3:00 AM")
        logger.info("  - Daily cycle: Every day at 6:00 AM")
    
    def run_monthly_cycle(self):
        """Run the monthly cycle: download retraction database and precompute embeddings."""
        logger.info("Starting monthly cycle...")
        try:
            # Download retraction database
            logger.info("Downloading retraction database...")
            from scripts.download_retraction_database import main as download_main
            download_main()
            
            # Precompute embeddings
            logger.info("Precomputing embeddings...")
            from scripts.precompute_retraction_embeddings import main as precompute_main
            precompute_main()
            
            logger.info("Monthly cycle completed")
        except ImportError as e:
            logger.warning(f"Monthly cycle scripts not yet implemented: {e}")
        except Exception as e:
            logger.error(f"Error in monthly cycle: {e}", exc_info=True)
    
    def run_weekly_cycle(self):
        """Run the weekly cycle: import new/changed citations from Wikipedia."""
        logger.info("Starting weekly cycle...")
        try:
            from scripts.initial_import import main as import_main
            import_main()
            logger.info("Weekly cycle completed")
        except Exception as e:
            logger.error(f"Error in weekly cycle: {e}", exc_info=True)
    
    def run_daily_cycle(self):
        """Run the daily cycle: synthesizer agent checks citations for retractions."""
        logger.info("Starting daily cycle (Synthesizer Agent)...")
        try:
            from agents.synthesizer_agent import SynthesizerAgent
            agent = SynthesizerAgent()
            agent.run()
            logger.info("Daily cycle completed")
        except ImportError as e:
            logger.warning(f"Synthesizer Agent not yet implemented: {e}")
        except Exception as e:
            logger.error(f"Error in daily cycle: {e}", exc_info=True)
    
    def run_all_cycles_now(self):
        """Run all cycles immediately (for testing)."""
        logger.info("Running all cycles now...")
        self.run_monthly_cycle()
        self.run_weekly_cycle()
        self.run_daily_cycle()
        logger.info("All cycles completed")
    
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
    
    parser = argparse.ArgumentParser(description='WikiVerify Scheduler')
    parser.add_argument(
        '--run-now',
        action='store_true',
        help='Run all cycles immediately instead of scheduling'
    )
    
    args = parser.parse_args()
    
    scheduler = WikiVerifyScheduler()
    
    if args.run_now:
        scheduler.run_all_cycles_now()
    else:
        scheduler.start()


if __name__ == "__main__":
    main()
