"""
Scheduled tasks for automated scraping
"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from database import SessionLocal
from services.scraper_service import ScraperService
from models import User

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def daily_scraping_task():
    """Run daily scraping for all counties"""
    logger.info(f"Starting daily scraping task at {datetime.now()}")
    
    db = next(get_db())
    try:
        # Get system user for automated tasks
        system_user = db.query(User).filter(User.email == "system@taxlien.local").first()
        if not system_user:
            system_user = User(
                email="system@taxlien.local",
                username="system",
                is_admin=True,
                is_active=True,
                password_hash="no-login"  # This user cannot login
            )
            db.add(system_user)
            db.commit()
        
        scraper_service = ScraperService(db)
        
        # Scrape all counties
        counties = ['collin', 'dallas-lgbs']
        
        for county in counties:
            try:
                logger.info(f"Scraping {county}...")
                job_id = scraper_service.scrape_county_with_tracking(county, system_user)
                logger.info(f"Started scraping job {job_id} for {county}")
            except Exception as e:
                logger.error(f"Error scraping {county}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error in daily scraping task: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    """Initialize and start the scheduler"""
    # Schedule daily scraping at 3 AM
    scheduler.add_job(
        daily_scraping_task,
        CronTrigger(hour=3, minute=0),
        id='daily_scraping',
        replace_existing=True
    )
    
    # Also run immediately on startup for testing
    scheduler.add_job(
        daily_scraping_task,
        'date',
        run_date=datetime.now(),
        id='startup_scraping'
    )
    
    scheduler.start()
    logger.info("Scheduler started")


def shutdown_scheduler():
    """Shutdown the scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")