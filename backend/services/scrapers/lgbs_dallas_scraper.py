"""
Dallas County Tax Sales Scraper
Scrapes tax sale properties from Dallas County official sources
"""
import json
import logging
import time
import re
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
import pdfplumber

from .base_scraper import BaseTaxSaleScraper

logger = logging.getLogger(__name__)


class LGBSDallasScraper(BaseTaxSaleScraper):
    """Scraper for Dallas County tax sales from official Dallas County sources"""
    
    def __init__(self):
        super().__init__(
            county_name="Dallas County",
            base_url="https://www.dallascounty.org"
        )
        self.county = "DALLAS COUNTY"
        self.state = "TX"
        
    def scrape_upcoming_sales(self) -> List[Dict[str, Any]]:
        """Scrape tax sale properties from Dallas County official sources"""
        all_properties = []
        
        try:
            self.update_progress(10, "Connecting to Dallas County tax sales system...")
            
            # Fetch all properties from official sources
            all_properties = self._fetch_property_batch(0, 1000)  # Get all available
            total_properties = len(all_properties)
            
            self.update_progress(80, f"Processing {total_properties} properties...")
            
            # Group properties by sale date
            sales_by_date = self._group_properties_by_sale(all_properties)
            
            self.update_progress(90, "Finalizing data...")
            
            # Format for our system
            formatted_sales = self._format_sales_data(sales_by_date)
            
            self.update_progress(
                100, 
                f"Completed! Found {total_properties} properties across {len(formatted_sales)} sale dates.",
                properties_found=total_properties,
                sales_found=len(formatted_sales)
            )
            
            return formatted_sales
            
        except Exception as e:
            logger.error(f"Error scraping LGBS Dallas County: {str(e)}")
            self.update_progress(0, f"Error: {str(e)}")
            raise
    
    def _fetch_property_batch(self, offset: int, limit: int) -> List[Dict[str, Any]]:
        """Fetch a batch of properties from Dallas County official sources"""
        try:
            # First try Dallas County Public Works (struck-off properties)
            properties = self._fetch_from_public_works()
            
            # If we got data, return a slice based on offset/limit
            if properties:
                start = offset
                end = offset + limit
                return properties[start:end]
            
            # Fallback: Try Dallas County Clerk foreclosure notices
            properties = self._fetch_from_county_clerk()
            if properties:
                start = offset
                end = offset + limit
                return properties[start:end]
            
            # If no real data available, return empty list (no more mock data)
            logger.warning("No real property data available from Dallas County sources")
            return []
            
        except Exception as e:
            logger.error(f"Error fetching property batch: {str(e)}")
            return []
    
    def _fetch_from_public_works(self) -> List[Dict[str, Any]]:
        """Fetch struck-off properties from Dallas County Public Works PDF"""
        try:
            logger.info("Fetching properties from Dallas County Public Works PDF")
            
            # First get the page to find the current PDF link
            response = self.session.get(
                "https://www.dallascounty.org/departments/pubworks/property-division.php",
                timeout=30
            )
            
            if response.status_code != 200:
                return []
            
            # Find the struck-off properties PDF link
            soup = BeautifulSoup(response.content, 'html.parser')
            pdf_url = None
            
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                
                if 'struck' in text and '.pdf' in href.lower():
                    pdf_url = href
                    if not pdf_url.startswith('http'):
                        pdf_url = 'https://www.dallascounty.org' + pdf_url
                    break
            
            if not pdf_url:
                # Fallback to known URL
                pdf_url = "https://www.dallascounty.org/Assets/uploads/docs/public-works/StruckListWorking_2024_Inventory-Post-2025-2.pdf"
            
            logger.info(f"Downloading PDF from: {pdf_url}")
            
            # Download and parse PDF
            properties = self._parse_struck_off_pdf(pdf_url)
            
            logger.info(f"Found {len(properties)} properties from Public Works PDF")
            return properties
            
        except Exception as e:
            logger.error(f"Error fetching from Public Works PDF: {str(e)}")
            return []
    
    def _fetch_from_county_clerk(self) -> List[Dict[str, Any]]:
        """Fetch foreclosure notices from Dallas County Clerk"""
        try:
            logger.info("Fetching foreclosure notices from Dallas County Clerk")
            response = self.session.get(
                "https://www.dallascounty.org/government/county-clerk/recording/foreclosures.php",
                timeout=30
            )
            
            if response.status_code != 200:
                return []
            
            # For now, return empty as this requires additional parsing
            # This would need to be implemented to parse the foreclosure notice system
            logger.info("County Clerk foreclosure system needs additional implementation")
            return []
            
        except Exception as e:
            logger.error(f"Error fetching from County Clerk: {str(e)}")
            return []
    
    def _parse_struck_off_pdf(self, pdf_url: str) -> List[Dict[str, Any]]:
        """Download and parse the struck-off properties PDF"""
        try:
            # Download PDF
            response = self.session.get(pdf_url, timeout=30)
            if response.status_code != 200:
                logger.error(f"Failed to download PDF: {response.status_code}")
                return []
            
            pdf_file = io.BytesIO(response.content)
            properties = []
            
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    # Extract tables from each page
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if len(table) < 2:  # Need header + data
                            continue
                        
                        # Find the header row (might not be the first row)
                        header_row_idx = None
                        for i, row in enumerate(table):
                            if row and any(cell and 'PROPERTY ADDRESS' in str(cell).upper() for cell in row):
                                header_row_idx = i
                                break
                        
                        if header_row_idx is None:
                            continue
                        
                        headers = [str(cell).strip() if cell else '' for cell in table[header_row_idx]]
                        
                        # Process data rows
                        for row in table[header_row_idx + 1:]:
                            if not row or not any(row):  # Skip empty rows
                                continue
                                
                            cells = [str(cell).strip() if cell else '' for cell in row]
                            
                            # Parse property data
                            property_data = self._parse_pdf_property_row(headers, cells)
                            if property_data:
                                properties.append(property_data)
            
            return properties
            
        except Exception as e:
            logger.error(f"Error parsing struck-off PDF: {str(e)}")
            return []
    
    def _parse_pdf_property_row(self, headers: List[str], cells: List[str]) -> Dict[str, Any]:
        """Parse a property row from the PDF table"""
        try:
            # Initialize property data
            property_data = {
                'id': f'DC-{hash(str(cells))}',
                'parcel_id': '',
                'account_number': '',
                'owner_name': 'Unknown Owner',
                'property_address': '',
                'city': 'Dallas',
                'state': 'TX',
                'zip': '',
                'legal_description': '',
                'sale_date': '2025-02-04',  # First Tuesday of February
                'sale_type': 'STRUCK OFF',
                'precinct': '',
                'sale_number': '2025-001',
                'minimum_bid': 0,
                'judgment_amount': 0,
                'adjudged_value': 0,
                'assessed_value': 0,
                'taxes_owed': 0,
                'years_owed': 1,
                'latitude': 32.7767,
                'longitude': -96.7970,
                'property_type': 'Unknown',
                'year_built': None,
                'lot_size': 0,
                'building_sqft': None,
            }
            
            # Map columns to property data
            for i, header in enumerate(headers):
                if i >= len(cells) or not cells[i]:
                    continue
                
                header = header.upper().strip()
                cell_value = cells[i].strip()
                
                if not cell_value:
                    continue
                
                # Map PDF columns to property fields
                if 'PROPERTY ADDRESS' in header:
                    property_data['property_address'] = cell_value
                elif 'CITY' in header:
                    property_data['city'] = cell_value
                elif 'DCAD' in header and 'TAX ACC' in header:
                    property_data['parcel_id'] = cell_value
                    property_data['account_number'] = cell_value
                elif 'LEGAL DESCRIPTION' in header:
                    property_data['legal_description'] = cell_value
                elif 'DCAD Value' in header or '2024 DCAD' in header:
                    try:
                        # Extract numeric value from DCAD assessment
                        clean_value = re.sub(r'[^\d.]', '', cell_value)
                        if clean_value:
                            property_data['assessed_value'] = float(clean_value)
                    except:
                        pass
                elif 'MINIMUM BID' in header:
                    try:
                        # Extract numeric value from minimum bid
                        clean_value = re.sub(r'[^\d.]', '', cell_value)
                        if clean_value:
                            property_data['minimum_bid'] = float(clean_value)
                    except:
                        pass
                elif 'IMPROVED' in header or 'LAND ONLY' in header:
                    if 'IMPROVED' in cell_value.upper():
                        property_data['property_type'] = 'Improved'
                    elif 'LAND' in cell_value.upper():
                        property_data['property_type'] = 'Land'
                elif 'APPROX LAND SIZE' in header:
                    try:
                        # Extract numeric value from land size
                        numbers = re.findall(r'[\d.]+', cell_value)
                        if numbers:
                            property_data['lot_size'] = float(numbers[0])
                    except:
                        pass
                elif 'R&B DISTRICT' in header:
                    property_data['precinct'] = cell_value
                elif 'CAUSE' in header and 'JUDGMENT' in header:
                    # This might contain case number and date
                    property_data['case_number'] = cell_value
            
            # Only return if we have essential data
            if property_data['property_address'] or property_data['parcel_id']:
                return property_data
                
            return None
            
        except Exception as e:
            logger.error(f"Error parsing PDF property row: {str(e)}")
            return None
    
    def _parse_public_works_property(self, headers: List[str], cells: List[str]) -> Dict[str, Any]:
        """Parse property data from Public Works table row"""
        try:
            property_data = {
                'id': f'PW-{hash(str(cells))}',
                'parcel_id': '',
                'account_number': '',
                'owner_name': 'Unknown',
                'property_address': '',
                'city': 'Dallas',
                'state': 'TX',
                'zip': '',
                'legal_description': '',
                'sale_date': '2025-02-04',  # First Tuesday of month
                'sale_type': 'STRUCK OFF',
                'precinct': '',
                'sale_number': '2025-001',
                'minimum_bid': 0,
                'judgment_amount': 0,
                'adjudged_value': 0,
                'assessed_value': 0,
                'taxes_owed': 0,
                'years_owed': 1,
                'latitude': 32.7767,
                'longitude': -96.7970,
                'property_type': 'Unknown',
                'year_built': None,
                'lot_size': 0,
                'building_sqft': None,
            }
            
            # Map table columns to property fields
            for i, header in enumerate(headers):
                if i >= len(cells):
                    break
                
                cell_value = cells[i].strip()
                if not cell_value:
                    continue
                
                # Map common column headers to property fields
                if 'address' in header:
                    property_data['property_address'] = cell_value
                elif 'parcel' in header or 'account' in header:
                    property_data['parcel_id'] = cell_value
                elif 'owner' in header:
                    property_data['owner_name'] = cell_value
                elif 'bid' in header or 'price' in header:
                    try:
                        # Extract numeric value
                        import re
                        numbers = re.findall(r'[\d,]+\.?\d*', cell_value)
                        if numbers:
                            property_data['minimum_bid'] = float(numbers[0].replace(',', ''))
                    except:
                        pass
                elif 'legal' in header or 'description' in header:
                    property_data['legal_description'] = cell_value
                elif 'type' in header:
                    property_data['property_type'] = cell_value
            
            # Only return if we have essential data
            if property_data['property_address'] or property_data['parcel_id']:
                return property_data
                
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Public Works property: {str(e)}")
            return None
    
    def _extract_properties_from_html(self, html: str) -> List[Dict[str, Any]]:
        """Extract property data from HTML response"""
        properties = []
        
        try:
            # Look for JSON data embedded in the HTML
            import re
            
            # Common patterns for embedded JSON data
            patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'var\s+properties\s*=\s*(\[.*?\]);',
                r'data:\s*({.*?})\s*[,}]',
                r'properties":\s*(\[.*?\])',
            ]
            
            for pattern in patterns:
                matches = re.search(pattern, html, re.DOTALL)
                if matches:
                    try:
                        data = json.loads(matches.group(1))
                        if isinstance(data, list):
                            properties.extend(data)
                        elif isinstance(data, dict) and 'properties' in data:
                            properties.extend(data['properties'])
                    except json.JSONDecodeError:
                        continue
            
            # If no JSON found, properties remain empty
            if not properties:
                logger.warning("No embedded property data found in HTML")
            
        except Exception as e:
            logger.error(f"Error extracting properties from HTML: {str(e)}")
        
        return properties
    
    
    def _group_properties_by_sale(self, properties: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group properties by sale date"""
        sales_by_date = {}
        
        for prop in properties:
            sale_date = prop.get('sale_date', 'Unknown')
            if sale_date not in sales_by_date:
                sales_by_date[sale_date] = []
            sales_by_date[sale_date].append(prop)
        
        return sales_by_date
    
    def _format_sales_data(self, sales_by_date: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Format grouped sales data for our system"""
        formatted_sales = []
        
        for sale_date, properties in sales_by_date.items():
            sale_data = {
                'sale_date': sale_date,
                'sale_type': 'in-person',
                'platform': 'LGBS Tax Sales',
                'county': self.county,
                'properties': []
            }
            
            for prop in properties:
                formatted_property = {
                    'parcel_number': prop.get('parcel_id', prop.get('account_number', '')),
                    'owner_name': prop.get('owner_name', ''),
                    'property_address': prop.get('property_address', ''),
                    'city': prop.get('city', ''),
                    'state': prop.get('state', 'TX'),
                    'zip_code': prop.get('zip', ''),
                    'legal_description': prop.get('legal_description', ''),
                    'property_type': prop.get('property_type', 'Unknown'),
                    'year_built': prop.get('year_built'),
                    'lot_size': prop.get('lot_size'),
                    'building_sqft': prop.get('building_sqft'),
                    'assessed_value': prop.get('assessed_value', 0),
                    'market_value': prop.get('adjudged_value', prop.get('assessed_value', 0)),
                    'latitude': prop.get('latitude'),
                    'longitude': prop.get('longitude'),
                    'tax_info': {
                        'taxes_owed': prop.get('taxes_owed', 0),
                        'years_delinquent': prop.get('years_owed', 1),
                        'judgment_amount': prop.get('judgment_amount', 0),
                        'minimum_bid': prop.get('minimum_bid', 0),
                    },
                    'sale_info': {
                        'sale_type': prop.get('sale_type', 'SALE'),
                        'precinct': prop.get('precinct', ''),
                        'sale_number': prop.get('sale_number', ''),
                        'case_number': prop.get('case_number', ''),
                    },
                    'external_ids': {
                        'lgbs_id': prop.get('id', ''),
                        'parcel_id': prop.get('parcel_id', ''),
                        'account_number': prop.get('account_number', ''),
                    }
                }
                sale_data['properties'].append(formatted_property)
            
            formatted_sales.append(sale_data)
        
        return formatted_sales
    
    def parse_property_details(self, property_data: Any) -> Dict[str, Any]:
        """Parse property details from LGBS API response"""
        if isinstance(property_data, dict):
            return {
                'parcel_number': property_data.get('parcel_id', property_data.get('account_number', '')),
                'owner_name': property_data.get('owner_name', ''),
                'property_address': property_data.get('property_address', ''),
                'city': property_data.get('city', ''),
                'state': property_data.get('state', 'TX'),
                'zip_code': property_data.get('zip', ''),
                'legal_description': property_data.get('legal_description', ''),
                'property_type': property_data.get('property_type', 'Unknown'),
                'year_built': property_data.get('year_built'),
                'lot_size': property_data.get('lot_size'),
                'building_sqft': property_data.get('building_sqft'),
                'assessed_value': property_data.get('assessed_value', 0),
                'market_value': property_data.get('adjudged_value', property_data.get('assessed_value', 0)),
                'latitude': property_data.get('latitude'),
                'longitude': property_data.get('longitude'),
                'taxes_owed': property_data.get('taxes_owed', 0),
                'minimum_bid': property_data.get('minimum_bid', 0),
                'sale_type': property_data.get('sale_type', 'SALE'),
                'precinct': property_data.get('precinct', ''),
                'case_number': property_data.get('case_number', ''),
            }
        return {}
    
    def update_progress(self, progress: int, message: str, properties_found: int = 0, sales_found: int = 0):
        """Update scraping progress"""
        if hasattr(self, 'progress_callback') and self.progress_callback:
            self.progress_callback(progress, message, properties_found, sales_found)