from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from services.scrapers.collin_county_scraper import CollinCountyScraper
from services.scrapers.dallas_county_scraper import DallasCountyScraper
from services.scrapers.lgbs_dallas_scraper import LGBSDallasScraper
from services.property_enrichment_service import PropertyEnrichmentService
from models import County, Property, TaxSale, Alert
from models.user import User
from models.property_enrichment import PropertyEnrichment
from models.scraping_job import ScrapingJob
import uuid

logger = logging.getLogger(__name__)

class ScraperService:
    """Service to manage tax sale data scraping"""
    
    def __init__(self, db: Session):
        self.db = db
        self.scrapers = {
            'collin': CollinCountyScraper(),
            'dallas': DallasCountyScraper(),
            'dallas-lgbs': LGBSDallasScraper(),
        }
        self.enrichment_service = PropertyEnrichmentService()
        
    def scrape_all_counties(self, user: Optional[User] = None) -> Dict[str, Any]:
        """Scrape tax sales from all configured counties"""
        results = {
            'success': True,
            'counties_scraped': [],
            'total_sales': 0,
            'total_properties': 0,
            'errors': []
        }
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit scraping tasks
            future_to_county = {
                executor.submit(self._scrape_county, county_code, scraper): county_code
                for county_code, scraper in self.scrapers.items()
            }
            
            # Process results as they complete
            for future in as_completed(future_to_county):
                county_code = future_to_county[future]
                try:
                    county_result = future.result()
                    results['counties_scraped'].append(county_code)
                    results['total_sales'] += county_result['sales_count']
                    results['total_properties'] += county_result['properties_count']
                    
                    if county_result.get('errors'):
                        results['errors'].extend(county_result['errors'])
                        
                except Exception as e:
                    logger.error(f"Error scraping {county_code}: {str(e)}")
                    results['errors'].append(f"{county_code}: {str(e)}")
                    results['success'] = False
        
        # Create alert for admin if there were errors
        if results['errors'] and user:
            self._create_scraping_alert(user, results['errors'])
        
        return results
    
    def _scrape_county(self, county_code: str, scraper) -> Dict[str, Any]:
        """Scrape a single county"""
        result = {
            'county': county_code,
            'sales_count': 0,
            'properties_count': 0,
            'errors': []
        }
        
        try:
            # Get or create county record
            county = self._get_or_create_county(county_code, scraper.county_name)
            
            # Scrape upcoming sales
            sales_data = scraper.scrape_upcoming_sales()
            
            for sale_info in sales_data:
                try:
                    # Process each sale
                    properties_imported = self._process_sale_data(sale_info, county)
                    result['sales_count'] += 1
                    result['properties_count'] += properties_imported
                    
                except Exception as e:
                    error_msg = f"Error processing sale on {sale_info.get('sale_date')}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    
        except Exception as e:
            error_msg = f"Error scraping {county_code}: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            
        return result
    
    def _get_or_create_county(self, county_code: str, county_name: str) -> County:
        """Get or create county record"""
        county = self.db.query(County).filter(
            County.name == county_name
        ).first()
        
        if not county:
            county = County(
                name=county_name,
                state='TX',
                auction_location=f"{county_name} Courthouse" if 'collin' in county_code.lower() else 'Online',
                auction_type='in_person' if 'collin' in county_code.lower() else 'online',
                auction_schedule='First Tuesday of each month',
                website_url='https://www.collincountytx.gov' if 'collin' in county_code.lower() else 'https://www.realauction.com',
                contact_info='',
                special_procedures=''
            )
            self.db.add(county)
            self.db.commit()
            
        return county
    
    def _process_sale_data(self, sale_info: Dict, county: County) -> int:
        """Process scraped sale data and save to database"""
        properties_imported = 0
        sale_date = sale_info['sale_date']
        
        for prop_data in sale_info.get('properties', []):
            try:
                # Get or create property
                property = self._get_or_create_property(prop_data, county)
                
                # Check if tax sale already exists
                existing_sale = self.db.query(TaxSale).filter(
                    TaxSale.property_id == property.id,
                    TaxSale.sale_date == sale_date
                ).first()
                
                if not existing_sale:
                    # Create new tax sale
                    tax_sale = TaxSale(
                        property_id=property.id,
                        county_id=county.id,
                        sale_date=sale_date,
                        minimum_bid=prop_data.get('minimum_bid', 0),
                        taxes_owed=prop_data.get('taxes_owed', prop_data.get('minimum_bid', 0)),
                        interest_penalties=prop_data.get('interest_penalties', 0),
                        court_costs=prop_data.get('court_costs', 0),
                        attorney_fees=prop_data.get('attorney_fees', 0),
                        total_judgment=prop_data.get('total_judgment', prop_data.get('minimum_bid', 0)),
                        sale_status='scheduled',
                        case_number=prop_data.get('case_number', ''),
                        constable_precinct=prop_data.get('constable_precinct', '')
                    )
                    self.db.add(tax_sale)
                    properties_imported += 1
                else:
                    # Update existing sale if needed
                    if existing_sale.minimum_bid != prop_data.get('minimum_bid', 0):
                        existing_sale.minimum_bid = prop_data.get('minimum_bid', 0)
                        existing_sale.updated_at = datetime.now()
                        
            except Exception as e:
                logger.error(f"Error processing property {prop_data.get('parcel_number')}: {str(e)}")
                raise
                
        self.db.commit()
        return properties_imported
    
    def _get_or_create_property(self, prop_data: Dict, county: County) -> Property:
        """Get or create property record"""
        parcel_number = prop_data.get('parcel_number', '')
        
        property = self.db.query(Property).filter(
            Property.parcel_number == parcel_number,
            Property.county_id == county.id
        ).first()
        
        if not property:
            property = Property(
                parcel_number=parcel_number,
                owner_name=prop_data.get('owner_name', 'Unknown'),
                property_address=prop_data.get('property_address', ''),
                county_id=county.id,
                property_type=prop_data.get('property_type', 'residential'),
                legal_description=prop_data.get('legal_description', ''),
                city=self._extract_city(prop_data.get('property_address', '')),
                zip_code=self._extract_zip(prop_data.get('property_address', '')),
                state='TX',
                homestead_exemption=False,  # Would need to verify
                agricultural_exemption=False,
                senior_exemption=False
            )
            self.db.add(property)
            self.db.flush()  # Get ID without committing
            
        return property
    
    def _extract_city(self, address: str) -> str:
        """Extract city from address string"""
        # Simple extraction - would need more robust parsing
        parts = address.split(',')
        if len(parts) >= 2:
            return parts[-2].strip()
        return ''
    
    def _extract_zip(self, address: str) -> str:
        """Extract ZIP code from address string"""
        import re
        zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
        match = re.search(zip_pattern, address)
        return match.group(0) if match else ''
    
    def _create_scraping_alert(self, user: User, errors: List[str]):
        """Create alert for scraping errors"""
        alert = Alert(
            user_id=user.id,
            alert_type='system',
            title='Tax Sale Scraping Errors',
            message=f"Encountered {len(errors)} errors during scraping:\n" + "\n".join(errors[:5]),
            alert_date=datetime.now() + timedelta(hours=1),
            is_urgent=True
        )
        self.db.add(alert)
        self.db.commit()
    
    def scrape_county(self, county_code: str, user: Optional[User] = None) -> Dict[str, Any]:
        """Scrape a specific county"""
        if county_code not in self.scrapers:
            return {
                'success': False,
                'error': f'No scraper configured for county: {county_code}'
            }
        
        scraper = self.scrapers[county_code]
        result = self._scrape_county(county_code, scraper)
        
        return {
            'success': len(result['errors']) == 0,
            'county': result['county'],
            'sales_imported': result['sales_count'],
            'properties_imported': result['properties_count'],
            'errors': result['errors']
        }
    
    def scrape_county_with_tracking(self, county_code: str, user: Optional[User] = None) -> str:
        """Scrape a county with job tracking"""
        # Create scraping job
        job_id = str(uuid.uuid4())
        job = ScrapingJob(
            job_id=job_id,
            county=county_code,
            status='pending',
            created_by=user.email if user else 'system',
            progress=0
        )
        self.db.add(job)
        self.db.commit()
        
        # Set up progress callback
        def update_progress(progress: int, message: str, properties_found: int = 0, sales_found: int = 0):
            job.progress = progress
            job.details = {'message': message}
            job.properties_found = properties_found
            job.sales_found = sales_found
            job.status = 'running' if progress < 100 else 'completed'
            self.db.commit()
        
        # Get scraper and set progress callback
        if county_code not in self.scrapers:
            job.status = 'failed'
            job.errors = f'No scraper configured for county: {county_code}'
            self.db.commit()
            return job_id
        
        scraper = self.scrapers[county_code]
        scraper.set_progress_callback(update_progress)
        
        try:
            # Run scraping
            job.status = 'running'
            self.db.commit()
            
            result = self._scrape_county(county_code, scraper)
            
            # Update job with results
            job.properties_found = result['properties_count']
            job.sales_found = result['sales_count']
            job.completed_at = datetime.utcnow()
            
            if result['errors']:
                job.errors = '\n'.join(result['errors'])
                job.status = 'completed_with_errors'
            else:
                job.status = 'completed'
            
            self.db.commit()
            
            # Enrich properties if successful
            if result['properties_count'] > 0:
                self._enrich_recent_properties(county_code)
            
        except Exception as e:
            job.status = 'failed'
            job.errors = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            logger.error(f"Scraping job {job_id} failed: {str(e)}")
        
        return job_id
    
    def get_scraping_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a scraping job"""
        job = self.db.query(ScrapingJob).filter(ScrapingJob.job_id == job_id).first()
        
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'county': job.county,
            'status': job.status,
            'progress': job.progress,
            'message': job.details.get('message', '') if job.details else '',
            'properties_found': job.properties_found,
            'sales_found': job.sales_found,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'errors': job.errors
        }
    
    def _enrich_recent_properties(self, county_code: str):
        """Enrich recently scraped properties with external data"""
        try:
            # Get properties without enrichment data
            recent_properties = self.db.query(Property).join(
                County
            ).filter(
                County.name.ilike(f'%{county_code}%'),
                Property.created_at >= datetime.utcnow() - timedelta(hours=1)
            ).limit(50).all()
            
            for property in recent_properties:
                try:
                    # Check if already enriched
                    existing = self.db.query(PropertyEnrichment).filter(
                        PropertyEnrichment.property_id == property.id
                    ).first()
                    
                    if not existing:
                        # Enrich property data
                        property_dict = {
                            'parcel_number': property.parcel_number,
                            'property_address': property.property_address,
                            'city': property.city,
                            'state': property.state,
                            'zip_code': property.zip_code,
                            'latitude': float(property.latitude) if property.latitude else None,
                            'longitude': float(property.longitude) if property.longitude else None,
                            'assessed_value': float(property.assessed_value) if property.assessed_value else 0,
                            'year_built': property.year_built,
                            'building_sqft': property.square_footage,
                            'lot_size': float(property.lot_size) if property.lot_size else None
                        }
                        
                        enriched_data = self.enrichment_service.enrich_property(property_dict)
                        
                        # Save enrichment data
                        enrichment = PropertyEnrichment(
                            property_id=property.id,
                            zillow_estimated_value=enriched_data.get('zillow_data', {}).get('estimated_value'),
                            zillow_rent_estimate=enriched_data.get('zillow_data', {}).get('rent_estimate'),
                            zestimate=enriched_data.get('zillow_data', {}).get('zestimate'),
                            formatted_address=enriched_data.get('formatted_address'),
                            place_id=enriched_data.get('place_id'),
                            neighborhood_data=enriched_data.get('neighborhood_data'),
                            investment_score=enriched_data.get('investment_metrics', {}).get('investment_score'),
                            roi_percentage=enriched_data.get('investment_metrics', {}).get('roi_percentage'),
                            cap_rate=enriched_data.get('investment_metrics', {}).get('cap_rate'),
                            monthly_rent_estimate=enriched_data.get('investment_metrics', {}).get('monthly_rent_estimate'),
                            data_quality_score=enriched_data.get('enrichment', {}).get('quality_score'),
                            last_enriched_at=datetime.utcnow()
                        )
                        
                        self.db.add(enrichment)
                        
                except Exception as e:
                    logger.error(f"Error enriching property {property.id}: {str(e)}")
                    continue
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error in property enrichment: {str(e)}")