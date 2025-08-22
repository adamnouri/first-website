"""
Background Processing for NBA Predictions
=========================================

Pre-compute predictions to provide instant responses
"""

import threading
import time
import schedule
from datetime import datetime
import logging
from .playoff_predictor import PlayoffPredictor
from .championship_calculator import ChampionshipCalculator
from .s3_prediction_storage import S3PredictionStorage

logger = logging.getLogger(__name__)

class BackgroundProcessor:
    """Background processor for pre-computing predictions"""
    
    def __init__(self, prediction_service, s3_service=None):
        self.prediction_service = prediction_service
        self.s3_service = s3_service
        self.s3_storage = S3PredictionStorage(s3_service)
        self.playoff_predictor = PlayoffPredictor(prediction_service, s3_service)
        self.championship_calculator = ChampionshipCalculator(prediction_service, self.playoff_predictor, s3_service)
        self.is_running = False
        self.thread = None
        
    def start_background_processing(self):
        """Start background processing thread"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Schedule regular updates
        schedule.every(2).hours.do(self._update_conference_standings)
        schedule.every(4).hours.do(self._update_championship_odds)
        schedule.every(6).hours.do(self._update_playoff_bracket)
        
        # Initial population
        self._initial_cache_population()
        
        # Start scheduler thread
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("Background processor started")
    
    def stop_background_processing(self):
        """Stop background processing"""
        self.is_running = False
        schedule.clear()
        logger.info("Background processor stopped")
    
    def _run_scheduler(self):
        """Run the scheduler in background thread"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _initial_cache_population(self):
        """Populate cache with initial predictions"""
        logger.info("Starting initial cache population...")
        
        try:
            # Pre-compute with common parameters
            threading.Thread(target=self._populate_standings_cache, daemon=True).start()
            threading.Thread(target=self._populate_odds_cache, daemon=True).start()
            threading.Thread(target=self._populate_bracket_cache, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error in initial cache population: {e}")
    
    def _populate_standings_cache(self):
        """Pre-compute conference standings"""
        try:
            # Common simulation counts
            for simulations in [1000, 2500, 5000]:
                for conference in ['both', 'eastern', 'western']:
                    logger.info(f"Pre-computing standings: {conference}, {simulations} sims")
                    self.playoff_predictor.simulate_season_standings(simulations=simulations)
                    time.sleep(1)  # Prevent overwhelming the system
        except Exception as e:
            logger.error(f"Error pre-computing standings: {e}")
    
    def _populate_odds_cache(self):
        """Pre-compute championship odds"""
        try:
            # Common simulation counts
            for simulations in [1000, 5000, 10000]:
                logger.info(f"Pre-computing championship odds: {simulations} sims")
                self.championship_calculator.calculate_comprehensive_odds(simulations=simulations)
                time.sleep(2)  # These are more expensive
        except Exception as e:
            logger.error(f"Error pre-computing odds: {e}")
    
    def _populate_bracket_cache(self):
        """Pre-compute playoff brackets"""
        try:
            logger.info("Pre-computing playoff bracket")
            self.playoff_predictor.generate_playoff_bracket()
        except Exception as e:
            logger.error(f"Error pre-computing bracket: {e}")
    
    def _update_conference_standings(self):
        """Scheduled update for conference standings"""
        logger.info("Scheduled update: Conference standings")
        # S3 storage handles expiration automatically
        self._populate_standings_cache()
    
    def _update_championship_odds(self):
        """Scheduled update for championship odds"""
        logger.info("Scheduled update: Championship odds")
        # S3 storage handles expiration automatically
        self._populate_odds_cache()
    
    def _update_playoff_bracket(self):
        """Scheduled update for playoff bracket"""
        logger.info("Scheduled update: Playoff bracket")
        # S3 storage handles expiration automatically
        self._populate_bracket_cache()
    
    def get_processing_status(self) -> dict:
        """Get status of background processing"""
        storage_stats = self.s3_storage.get_storage_stats()
        
        return {
            "is_running": self.is_running,
            "storage_stats": storage_stats,
            "next_run_times": {
                "standings": schedule.next_run('_update_conference_standings'),
                "odds": schedule.next_run('_update_championship_odds'),
                "bracket": schedule.next_run('_update_playoff_bracket')
            },
            "thread_alive": self.thread.is_alive() if self.thread else False
        }

# Global background processor instance
background_processor = None

def initialize_background_processor(prediction_service, s3_service=None):
    """Initialize the global background processor"""
    global background_processor
    background_processor = BackgroundProcessor(prediction_service, s3_service)
    background_processor.start_background_processing()
    return background_processor