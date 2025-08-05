"""
Mock scraper for demonstration purposes
Generates realistic-looking tax sale data
"""
from typing import List, Dict, Any
import random
from datetime import datetime, timedelta
from faker import Faker
import time
import logging

logger = logging.getLogger(__name__)
fake = Faker()

class MockCountyScraper:
    """Mock scraper that generates sample data with progress updates"""
    
    def __init__(self, county_name: str):
        self.county_name = county_name
        self.progress_callback = None
        
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
        
    def update_progress(self, progress: int, message: str, properties_found: int = 0, sales_found: int = 0):
        """Update scraping progress"""
        if self.progress_callback:
            self.progress_callback(progress, message, properties_found, sales_found)
    
    def scrape_upcoming_sales(self) -> List[Dict[str, Any]]:
        """Generate mock tax sale data with progress updates"""
        sales = []
        
        try:
            self.update_progress(10, "Connecting to county website...")
            time.sleep(2)  # Simulate connection time
            
            self.update_progress(20, "Searching for tax sale listings...")
            time.sleep(2)
            
            # Generate 10-20 mock sales
            num_sales = random.randint(10, 20)
            self.update_progress(30, f"Found {num_sales} upcoming sales. Extracting details...")
            
            for i in range(num_sales):
                # Update progress for each property
                progress = 30 + int((i / num_sales) * 60)
                self.update_progress(
                    progress, 
                    f"Processing property {i+1} of {num_sales}...",
                    properties_found=i+1,
                    sales_found=i+1
                )
                
                # Generate sale date in next 30-90 days
                sale_date = datetime.now() + timedelta(days=random.randint(30, 90))
                
                # Generate property details
                property_value = random.randint(50000, 500000)
                tax_rate = 0.025
                years_delinquent = random.randint(1, 4)
                
                taxes_owed = property_value * tax_rate * years_delinquent
                interest_penalties = taxes_owed * 0.18 * years_delinquent
                court_costs = random.uniform(500, 2500)
                attorney_fees = random.uniform(1000, 5000)
                total_judgment = taxes_owed + interest_penalties + court_costs + attorney_fees
                
                sale_data = {
                    'sale_date': sale_date.strftime('%Y-%m-%d'),
                    'sale_time': f"{random.randint(9, 11)}:00 AM",
                    'property': {
                        'parcel_number': f'{self.county_name[:3].upper()}-{fake.random_number(digits=8):08d}',
                        'owner_name': fake.name(),
                        'property_address': fake.street_address(),
                        'city': fake.city(),
                        'state': 'TX',
                        'zip_code': fake.zipcode()[:5],
                        'legal_description': f'Lot {random.randint(1, 100)}, Block {random.randint(1, 20)}, {fake.last_name()} Addition',
                        'property_type': random.choice(['Residential', 'Commercial', 'Vacant Land']),
                        'year_built': random.randint(1950, 2020) if random.random() > 0.3 else None,
                        'square_footage': random.randint(800, 5000) if random.random() > 0.3 else None,
                        'lot_size': random.randint(5000, 43560),
                        'assessed_value': property_value,
                        'market_value': property_value * 1.1,
                    },
                    'tax_info': {
                        'taxes_owed': round(taxes_owed, 2),
                        'interest_penalties': round(interest_penalties, 2),
                        'court_costs': round(court_costs, 2),
                        'attorney_fees': round(attorney_fees, 2),
                        'total_judgment': round(total_judgment, 2),
                        'minimum_bid': round(total_judgment, 2),
                        'years_delinquent': years_delinquent,
                        'tax_years': list(range(datetime.now().year - years_delinquent, datetime.now().year))
                    },
                    'sale_info': {
                        'case_number': f'TX-{sale_date.year}-{fake.random_number(digits=6):06d}',
                        'constable_precinct': str(random.randint(1, 4)),
                        'sale_location': f'{self.county_name} Courthouse, North Steps',
                        'deposit_required': round(total_judgment * 0.1, 2),  # 10% deposit
                    }
                }
                
                sales.append(sale_data)
                time.sleep(0.5)  # Simulate processing time
            
            self.update_progress(90, "Finalizing data extraction...")
            time.sleep(1)
            
            self.update_progress(100, f"Completed! Found {len(sales)} properties with upcoming tax sales.", len(sales), len(sales))
            
        except Exception as e:
            logger.error(f"Error in mock scraper: {str(e)}")
            self.update_progress(0, f"Error: {str(e)}", 0, 0)
            raise
            
        return sales