import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseTaxSaleScraper(ABC):
    """Base class for county tax sale scrapers"""
    
    def __init__(self, county_name: str, base_url: str):
        self.county_name = county_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    @abstractmethod
    def scrape_upcoming_sales(self) -> List[Dict[str, Any]]:
        """Scrape upcoming tax sales - must be implemented by subclass"""
        pass
    
    @abstractmethod
    def parse_property_details(self, property_data: Any) -> Dict[str, Any]:
        """Parse property details from scraped data"""
        pass
    
    def get_page(self, url: str, **kwargs) -> Optional[BeautifulSoup]:
        """Get and parse a web page"""
        try:
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def post_page(self, url: str, data: Dict, **kwargs) -> Optional[BeautifulSoup]:
        """Post data and parse response"""
        try:
            response = self.session.post(url, data=data, **kwargs)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error posting to {url}: {str(e)}")
            return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats"""
        date_formats = [
            '%m/%d/%Y',
            '%Y-%m-%d',
            '%B %d, %Y',
            '%b %d, %Y',
            '%m-%d-%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def parse_currency(self, amount_str: str) -> float:
        """Parse currency string to float"""
        try:
            # Remove currency symbols and commas
            cleaned = amount_str.replace('$', '').replace(',', '').strip()
            return float(cleaned)
        except:
            logger.warning(f"Could not parse amount: {amount_str}")
            return 0.0
    
    def delay(self, seconds: float = 1.0):
        """Add delay between requests to be respectful"""
        time.sleep(seconds)