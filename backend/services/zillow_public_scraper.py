"""
Zillow Public Data Scraper
Scrapes publicly available property data from Zillow without API keys
"""
import logging
import re
import json
import time
from typing import Dict, Any, Optional
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ZillowPublicScraper:
    """Scrape public property data from Zillow"""
    
    def __init__(self):
        self.base_url = "https://www.zillow.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self._cache = {}
    
    def get_property_data(self, address: str, city: str, state: str, zip_code: str = None) -> Optional[Dict[str, Any]]:
        """Get property data from Zillow public pages"""
        try:
            # Build search query
            if zip_code:
                search_query = f"{address} {city} {state} {zip_code}"
            else:
                search_query = f"{address} {city} {state}"
            
            # Check cache
            cache_key = f"zillow:{search_query}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Search for property
            property_url = self._search_property(search_query)
            if not property_url:
                logger.info(f"Property not found on Zillow: {search_query}")
                return None
            
            # Get property details
            property_data = self._scrape_property_page(property_url)
            if property_data:
                self._cache[cache_key] = property_data
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error getting Zillow data for {address}: {str(e)}")
            return None
    
    def _search_property(self, search_query: str) -> Optional[str]:
        """Search for a property on Zillow and return its URL"""
        try:
            # Zillow search URL
            search_url = f"{self.base_url}/homes/{quote(search_query)}_rb/"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for property card with exact or close match
            # Try different selectors as Zillow changes their HTML
            selectors = [
                'article[data-test="property-card"]',
                'div[class*="property-card"]',
                'div[class*="list-card"]',
                'article[class*="StyledCard"]'
            ]
            
            for selector in selectors:
                property_cards = soup.select(selector)
                if property_cards:
                    # Get the first property link
                    for card in property_cards:
                        link = card.find('a', href=True)
                        if link and link['href'].startswith('/homedetails/'):
                            return self.base_url + link['href']
            
            # Try to find direct property link in page
            links = soup.find_all('a', href=re.compile(r'/homedetails/.*'))
            if links:
                return self.base_url + links[0]['href']
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching Zillow: {str(e)}")
            return None
    
    def _scrape_property_page(self, property_url: str) -> Optional[Dict[str, Any]]:
        """Scrape property details from a Zillow property page"""
        try:
            response = self.session.get(property_url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data from page
            property_data = {}
            
            # Try to find JSON-LD structured data
            json_ld = soup.find('script', type='application/ld+json')
            if json_ld:
                try:
                    ld_data = json.loads(json_ld.string)
                    if isinstance(ld_data, list):
                        ld_data = ld_data[0]
                    
                    # Extract from structured data
                    property_data['structured_data'] = {
                        'name': ld_data.get('name'),
                        'description': ld_data.get('description'),
                        'url': ld_data.get('url'),
                    }
                    
                    if 'address' in ld_data:
                        property_data['address'] = {
                            'streetAddress': ld_data['address'].get('streetAddress'),
                            'addressLocality': ld_data['address'].get('addressLocality'),
                            'addressRegion': ld_data['address'].get('addressRegion'),
                            'postalCode': ld_data['address'].get('postalCode'),
                        }
                    
                    if 'geo' in ld_data:
                        property_data['coordinates'] = {
                            'latitude': ld_data['geo'].get('latitude'),
                            'longitude': ld_data['geo'].get('longitude'),
                        }
                except:
                    pass
            
            # Extract Zestimate
            zestimate_selectors = [
                'span[data-test="zestimate-value"]',
                'div[class*="zestimate"] span[class*="value"]',
                'span[class*="Text-"][class*="zestimate"]'
            ]
            
            for selector in zestimate_selectors:
                elem = soup.select_one(selector)
                if elem:
                    property_data['zestimate'] = self._parse_price(elem.text)
                    break
            
            # Extract property details
            details = {}
            
            # Bedrooms and bathrooms
            bed_bath_selectors = [
                'span[data-test="bed-bath-item"]',
                'div[class*="bed-bath"] span',
                'span[class*="beds-baths"]'
            ]
            
            for selector in bed_bath_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.text.lower()
                    if 'bed' in text:
                        match = re.search(r'(\d+)', text)
                        if match:
                            details['bedrooms'] = int(match.group(1))
                    elif 'bath' in text:
                        match = re.search(r'(\d+\.?\d*)', text)
                        if match:
                            details['bathrooms'] = float(match.group(1))
            
            # Square footage
            sqft_selectors = [
                'span[data-test="property-sqft"]',
                'span:contains("sqft")',
                'div[class*="sqft"]'
            ]
            
            for selector in sqft_selectors:
                if ':contains' in selector:
                    # BeautifulSoup doesn't support :contains, use different approach
                    elements = soup.find_all(text=re.compile(r'\d+[\s,]*sqft', re.I))
                    if elements:
                        match = re.search(r'([\d,]+)\s*sqft', elements[0], re.I)
                        if match:
                            details['square_footage'] = int(match.group(1).replace(',', ''))
                            break
                else:
                    elem = soup.select_one(selector)
                    if elem:
                        match = re.search(r'([\d,]+)', elem.text)
                        if match:
                            details['square_footage'] = int(match.group(1).replace(',', ''))
                            break
            
            # Year built
            year_selectors = [
                'span:contains("Built in")',
                'div[class*="year-built"]'
            ]
            
            for text in soup.find_all(text=re.compile(r'Built in \d{4}')):
                match = re.search(r'Built in (\d{4})', text)
                if match:
                    details['year_built'] = int(match.group(1))
                    break
            
            # Lot size
            lot_selectors = [
                'span:contains("Lot:")',
                'span[class*="lot-size"]'
            ]
            
            for text in soup.find_all(text=re.compile(r'Lot:\s*[\d,.]+ (sqft|acres?)', re.I)):
                match = re.search(r'Lot:\s*([\d,.]+)\s*(sqft|acres?)', text, re.I)
                if match:
                    size = float(match.group(1).replace(',', ''))
                    unit = match.group(2).lower()
                    if 'acre' in unit:
                        details['lot_size_acres'] = size
                        details['lot_size_sqft'] = int(size * 43560)
                    else:
                        details['lot_size_sqft'] = int(size)
                        details['lot_size_acres'] = size / 43560
                    break
            
            property_data['details'] = details
            
            # Extract price history if available
            price_history = self._extract_price_history(soup)
            if price_history:
                property_data['price_history'] = price_history
            
            # Extract tax history
            tax_history = self._extract_tax_history(soup)
            if tax_history:
                property_data['tax_history'] = tax_history
            
            # Extract nearby schools
            schools = self._extract_nearby_schools(soup)
            if schools:
                property_data['nearby_schools'] = schools
            
            # Extract neighborhood info
            neighborhood = self._extract_neighborhood_info(soup)
            if neighborhood:
                property_data['neighborhood'] = neighborhood
            
            # Add metadata
            property_data['source'] = 'Zillow Public Data'
            property_data['url'] = property_url
            property_data['scraped_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Rate limiting
            time.sleep(1)
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error scraping property page: {str(e)}")
            return None
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """Parse price string to float"""
        try:
            # Remove currency symbols and convert K/M to thousands/millions
            price_str = price_str.replace('$', '').replace(',', '').strip()
            
            if 'K' in price_str.upper():
                return float(price_str.upper().replace('K', '')) * 1000
            elif 'M' in price_str.upper():
                return float(price_str.upper().replace('M', '')) * 1000000
            else:
                return float(price_str)
        except:
            return None
    
    def _extract_price_history(self, soup: BeautifulSoup) -> list:
        """Extract price history from property page"""
        price_history = []
        
        try:
            # Look for price history section
            history_section = soup.find('div', {'id': 'price-history'}) or \
                            soup.find('section', {'aria-label': re.compile('price history', re.I)})
            
            if history_section:
                rows = history_section.find_all('tr') or history_section.find_all('div', class_=re.compile('row'))
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'div'])
                    if len(cells) >= 3:
                        date_text = cells[0].text.strip()
                        event_text = cells[1].text.strip()
                        price_text = cells[2].text.strip()
                        
                        price = self._parse_price(price_text)
                        if price:
                            price_history.append({
                                'date': date_text,
                                'event': event_text,
                                'price': price
                            })
        except:
            pass
        
        return price_history
    
    def _extract_tax_history(self, soup: BeautifulSoup) -> list:
        """Extract tax history from property page"""
        tax_history = []
        
        try:
            # Look for tax history section
            tax_section = soup.find('div', {'id': 'tax-history'}) or \
                         soup.find('section', {'aria-label': re.compile('tax history', re.I)})
            
            if tax_section:
                rows = tax_section.find_all('tr') or tax_section.find_all('div', class_=re.compile('row'))
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'div'])
                    if len(cells) >= 2:
                        year_text = cells[0].text.strip()
                        amount_text = cells[1].text.strip()
                        
                        amount = self._parse_price(amount_text)
                        if amount and year_text.isdigit():
                            tax_history.append({
                                'year': int(year_text),
                                'amount': amount
                            })
        except:
            pass
        
        return tax_history
    
    def _extract_nearby_schools(self, soup: BeautifulSoup) -> list:
        """Extract nearby schools information"""
        schools = []
        
        try:
            # Look for schools section
            schools_section = soup.find('div', {'id': 'schools'}) or \
                            soup.find('section', {'aria-label': re.compile('schools', re.I)})
            
            if schools_section:
                school_items = schools_section.find_all('div', class_=re.compile('school'))
                
                for item in school_items[:5]:  # Limit to 5 schools
                    name_elem = item.find(['h4', 'h5', 'span'], class_=re.compile('name'))
                    rating_elem = item.find(['span', 'div'], class_=re.compile('rating'))
                    distance_elem = item.find(['span', 'div'], class_=re.compile('distance'))
                    
                    if name_elem:
                        school = {'name': name_elem.text.strip()}
                        
                        if rating_elem:
                            rating_match = re.search(r'(\d+)', rating_elem.text)
                            if rating_match:
                                school['rating'] = int(rating_match.group(1))
                        
                        if distance_elem:
                            dist_match = re.search(r'([\d.]+)', distance_elem.text)
                            if dist_match:
                                school['distance_miles'] = float(dist_match.group(1))
                        
                        schools.append(school)
        except:
            pass
        
        return schools
    
    def _extract_neighborhood_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract neighborhood information"""
        neighborhood = {}
        
        try:
            # Look for Walk Score
            walk_score = soup.find(text=re.compile(r'Walk Score.*\d+'))
            if walk_score:
                match = re.search(r'Walk Score.*?(\d+)', walk_score)
                if match:
                    neighborhood['walk_score'] = int(match.group(1))
            
            # Look for Transit Score
            transit_score = soup.find(text=re.compile(r'Transit Score.*\d+'))
            if transit_score:
                match = re.search(r'Transit Score.*?(\d+)', transit_score)
                if match:
                    neighborhood['transit_score'] = int(match.group(1))
            
            # Look for neighborhood name
            neighborhood_elem = soup.find(['h2', 'h3'], text=re.compile('Neighborhood'))
            if neighborhood_elem:
                next_elem = neighborhood_elem.find_next_sibling()
                if next_elem:
                    neighborhood['name'] = next_elem.text.strip()
        except:
            pass
        
        return neighborhood
    
    def get_rental_estimate(self, property_data: Dict[str, Any]) -> Optional[float]:
        """Estimate rental value based on property data"""
        # Simple rental estimate based on property value
        # Typically 0.8% to 1.2% of property value per month
        
        if 'zestimate' in property_data and property_data['zestimate']:
            # Use 1% rule as baseline
            monthly_rent = property_data['zestimate'] * 0.01
            
            # Adjust based on property details
            details = property_data.get('details', {})
            
            # Adjust for bedrooms
            bedrooms = details.get('bedrooms', 3)
            if bedrooms < 2:
                monthly_rent *= 0.85
            elif bedrooms > 4:
                monthly_rent *= 1.15
            
            # Adjust for square footage
            sqft = details.get('square_footage', 1500)
            if sqft < 1000:
                monthly_rent *= 0.9
            elif sqft > 2500:
                monthly_rent *= 1.1
            
            return round(monthly_rent, -1)  # Round to nearest 10
        
        return None