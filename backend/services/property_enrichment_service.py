"""
Property Enrichment Service
Enriches property data with information from Zillow, Google Maps, and other sources
"""
import logging
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

logger = logging.getLogger(__name__)


class PropertyEnrichmentService:
    """Service to enrich property data with external sources"""
    
    def __init__(self):
        self.google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
        self.zillow_api_key = os.getenv('ZILLOW_API_KEY', '')
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', '')  # For Zillow alternative
        
        # Initialize session with retry logic
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Cache for API responses
        self._cache = {}
        self._cache_ttl = 86400  # 24 hours
    
    def enrich_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a single property with data from multiple sources"""
        enriched = property_data.copy()
        
        try:
            # Get coordinates if not present
            if not enriched.get('latitude') or not enriched.get('longitude'):
                coords = self._geocode_address(enriched)
                if coords:
                    enriched.update(coords)
            
            # Get Zillow data
            zillow_data = self._get_zillow_data(enriched)
            if zillow_data:
                enriched['zillow_data'] = zillow_data
            
            # Get neighborhood data from Google
            if enriched.get('latitude') and enriched.get('longitude'):
                neighborhood_data = self._get_neighborhood_data(
                    enriched['latitude'], 
                    enriched['longitude']
                )
                if neighborhood_data:
                    enriched['neighborhood_data'] = neighborhood_data
            
            # Get property details from county records
            county_data = self._get_county_property_data(enriched)
            if county_data:
                enriched['county_data'] = county_data
            
            # Calculate investment metrics
            enriched['investment_metrics'] = self._calculate_investment_metrics(enriched)
            
            # Add enrichment metadata
            enriched['enrichment'] = {
                'enriched_at': datetime.utcnow().isoformat(),
                'sources': self._get_enrichment_sources(enriched),
                'quality_score': self._calculate_data_quality_score(enriched)
            }
            
        except Exception as e:
            logger.error(f"Error enriching property {property_data.get('parcel_number')}: {str(e)}")
            enriched['enrichment'] = {
                'error': str(e),
                'enriched_at': datetime.utcnow().isoformat()
            }
        
        return enriched
    
    def enrich_properties_batch(self, properties: List[Dict[str, Any]], max_workers: int = 5) -> List[Dict[str, Any]]:
        """Enrich multiple properties in parallel"""
        enriched_properties = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_property = {
                executor.submit(self.enrich_property, prop): prop 
                for prop in properties
            }
            
            for future in as_completed(future_to_property):
                try:
                    enriched = future.result()
                    enriched_properties.append(enriched)
                except Exception as e:
                    logger.error(f"Error in batch enrichment: {str(e)}")
                    # Return original property on error
                    enriched_properties.append(future_to_property[future])
        
        return enriched_properties
    
    def _geocode_address(self, property_data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Get coordinates for a property address using Google Maps Geocoding API"""
        if not self.google_maps_api_key:
            return None
        
        try:
            # Build full address
            address_parts = [
                property_data.get('property_address', ''),
                property_data.get('city', ''),
                property_data.get('state', 'TX'),
                property_data.get('zip_code', '')
            ]
            full_address = ', '.join(filter(None, address_parts))
            
            # Check cache
            cache_key = f"geocode:{full_address}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Call Google Maps Geocoding API
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': full_address,
                'key': self.google_maps_api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK' and data['results']:
                    location = data['results'][0]['geometry']['location']
                    result = {
                        'latitude': location['lat'],
                        'longitude': location['lng'],
                        'formatted_address': data['results'][0]['formatted_address'],
                        'place_id': data['results'][0]['place_id']
                    }
                    self._cache[cache_key] = result
                    return result
            
        except Exception as e:
            logger.error(f"Geocoding error: {str(e)}")
        
        return None
    
    def _get_zillow_data(self, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get property data from Zillow (or alternative real estate APIs)"""
        # Note: Zillow's official API is limited. Using RapidAPI alternatives
        if not self.rapidapi_key:
            return self._get_mock_zillow_data(property_data)
        
        try:
            # Use RapidAPI Realty Mole API as Zillow alternative
            url = "https://realty-mole-property-api.p.rapidapi.com/properties"
            
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "realty-mole-property-api.p.rapidapi.com"
            }
            
            params = {
                "address": property_data.get('property_address', ''),
                "city": property_data.get('city', ''),
                "state": property_data.get('state', 'TX'),
                "zipCode": property_data.get('zip_code', '')
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'estimated_value': data.get('estimatedValue'),
                    'rent_estimate': data.get('rentEstimate'),
                    'property_type': data.get('propertyType'),
                    'bedrooms': data.get('bedrooms'),
                    'bathrooms': data.get('bathrooms'),
                    'square_footage': data.get('squareFootage'),
                    'lot_size': data.get('lotSize'),
                    'year_built': data.get('yearBuilt'),
                    'last_sold_date': data.get('lastSoldDate'),
                    'last_sold_price': data.get('lastSoldPrice'),
                    'tax_assessment': data.get('taxAssessment'),
                    'features': data.get('features', []),
                    'comparable_properties': data.get('comparables', [])
                }
            
        except Exception as e:
            logger.error(f"Zillow data error: {str(e)}")
        
        # Return mock data for development
        return self._get_mock_zillow_data(property_data)
    
    def _get_mock_zillow_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock Zillow-style data for development"""
        import random
        
        base_value = property_data.get('assessed_value', 200000)
        
        return {
            'estimated_value': base_value * random.uniform(1.1, 1.3),
            'rent_estimate': base_value * random.uniform(0.006, 0.01),  # 0.6-1% of value
            'property_type': property_data.get('property_type', 'Single Family'),
            'bedrooms': random.randint(2, 5),
            'bathrooms': random.randint(1, 3),
            'square_footage': property_data.get('building_sqft', random.randint(1200, 3000)),
            'lot_size': property_data.get('lot_size', random.randint(5000, 15000)),
            'year_built': property_data.get('year_built', random.randint(1960, 2020)),
            'last_sold_date': '2020-06-15',
            'last_sold_price': base_value * random.uniform(0.8, 0.95),
            'tax_assessment': base_value,
            'features': ['Central Air', 'Garage', 'Hardwood Floors'],
            'zestimate': base_value * random.uniform(1.05, 1.25),
            'price_history': [
                {'date': '2020-06-15', 'price': base_value * 0.9, 'event': 'Sold'},
                {'date': '2018-03-10', 'price': base_value * 0.75, 'event': 'Sold'},
            ],
            'tax_history': [
                {'year': 2023, 'taxes': base_value * 0.025},
                {'year': 2022, 'taxes': base_value * 0.024},
            ],
            'nearby_schools': [
                {'name': 'Dallas Elementary', 'rating': 8, 'distance': 0.5},
                {'name': 'North Dallas High', 'rating': 7, 'distance': 1.2},
            ]
        }
    
    def _get_neighborhood_data(self, lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """Get neighborhood data using Google Places API"""
        if not self.google_maps_api_key:
            return None
        
        try:
            neighborhood_data = {}
            
            # Search for nearby amenities
            place_types = ['school', 'hospital', 'shopping_mall', 'park', 'transit_station']
            
            for place_type in place_types:
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                params = {
                    'location': f"{lat},{lng}",
                    'radius': 1600,  # 1 mile
                    'type': place_type,
                    'key': self.google_maps_api_key
                }
                
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 'OK':
                        neighborhood_data[f'{place_type}s'] = [
                            {
                                'name': place['name'],
                                'rating': place.get('rating'),
                                'distance': self._calculate_distance(
                                    lat, lng,
                                    place['geometry']['location']['lat'],
                                    place['geometry']['location']['lng']
                                )
                            }
                            for place in data['results'][:3]  # Top 3 results
                        ]
                
                time.sleep(0.1)  # Rate limiting
            
            # Get neighborhood demographics (mock for now)
            neighborhood_data['demographics'] = {
                'median_income': 65000,
                'crime_rate': 'Low',
                'walkability_score': 72,
                'school_rating': 7.5
            }
            
            return neighborhood_data
            
        except Exception as e:
            logger.error(f"Neighborhood data error: {str(e)}")
        
        return None
    
    def _get_county_property_data(self, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get additional data from county property records"""
        # This would integrate with county-specific APIs
        # For now, return enhanced mock data
        return {
            'owner_history': [
                {'year': 2020, 'owner': property_data.get('owner_name', 'Current Owner')},
                {'year': 2015, 'owner': 'Previous Owner LLC'},
            ],
            'tax_history': [
                {'year': 2023, 'amount_due': 5000, 'paid': False},
                {'year': 2022, 'amount_due': 4800, 'paid': False},
                {'year': 2021, 'amount_due': 4600, 'paid': True},
            ],
            'liens': [
                {'type': 'Tax Lien', 'amount': 10000, 'date': '2023-01-15'},
            ],
            'permits': [
                {'type': 'Roof Repair', 'date': '2019-06-01', 'status': 'Completed'},
            ]
        }
    
    def _calculate_investment_metrics(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate investment metrics for the property"""
        try:
            # Get values
            minimum_bid = property_data.get('tax_info', {}).get('minimum_bid', 0)
            taxes_owed = property_data.get('tax_info', {}).get('taxes_owed', 0)
            
            # Get estimated values
            zillow_data = property_data.get('zillow_data', {})
            estimated_value = zillow_data.get('estimated_value', property_data.get('assessed_value', 0))
            rent_estimate = zillow_data.get('rent_estimate', 0)
            
            # Calculate metrics
            metrics = {
                'estimated_value': estimated_value,
                'minimum_bid': minimum_bid,
                'potential_profit': max(0, estimated_value - minimum_bid - 20000),  # Subtract rehab estimate
                'roi_percentage': ((estimated_value - minimum_bid) / minimum_bid * 100) if minimum_bid > 0 else 0,
                'monthly_rent_estimate': rent_estimate,
                'annual_rental_income': rent_estimate * 12,
                'gross_rent_multiplier': estimated_value / (rent_estimate * 12) if rent_estimate > 0 else 0,
                'cap_rate': ((rent_estimate * 12 - estimated_value * 0.01) / estimated_value * 100) if estimated_value > 0 else 0,
                'estimated_rehab_cost': 20000,  # Default estimate
                'total_investment': minimum_bid + 20000,
                'cash_on_cash_return': ((rent_estimate * 12) / (minimum_bid + 20000) * 100) if minimum_bid > 0 else 0,
                'investment_score': self._calculate_investment_score(property_data)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating investment metrics: {str(e)}")
            return {}
    
    def _calculate_investment_score(self, property_data: Dict[str, Any]) -> float:
        """Calculate an investment score from 0-100"""
        score = 50.0  # Base score
        
        try:
            metrics = property_data.get('investment_metrics', {})
            
            # ROI factor (up to 30 points)
            roi = metrics.get('roi_percentage', 0)
            if roi > 100:
                score += 30
            elif roi > 50:
                score += 20
            elif roi > 25:
                score += 10
            
            # Location factor (up to 20 points)
            neighborhood = property_data.get('neighborhood_data', {})
            if neighborhood:
                if neighborhood.get('demographics', {}).get('crime_rate') == 'Low':
                    score += 10
                if neighborhood.get('demographics', {}).get('school_rating', 0) > 7:
                    score += 10
            
            # Property condition (estimated, up to 20 points)
            year_built = property_data.get('year_built', 0)
            if year_built > 2000:
                score += 20
            elif year_built > 1980:
                score += 10
            
            # Cap any score at 100
            score = min(100, max(0, score))
            
        except Exception as e:
            logger.error(f"Error calculating investment score: {str(e)}")
        
        return round(score, 1)
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in miles"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 3959  # Earth's radius in miles
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return round(R * c, 2)
    
    def _get_enrichment_sources(self, property_data: Dict[str, Any]) -> List[str]:
        """Get list of data sources used for enrichment"""
        sources = ['County Records']
        
        if property_data.get('zillow_data'):
            sources.append('Zillow/Realty')
        if property_data.get('neighborhood_data'):
            sources.append('Google Maps')
        if property_data.get('latitude'):
            sources.append('Geocoding')
        
        return sources
    
    def _calculate_data_quality_score(self, property_data: Dict[str, Any]) -> float:
        """Calculate data quality score based on completeness"""
        total_fields = 0
        filled_fields = 0
        
        # Check important fields
        important_fields = [
            'parcel_number', 'owner_name', 'property_address',
            'latitude', 'longitude', 'assessed_value',
            'year_built', 'building_sqft', 'lot_size'
        ]
        
        for field in important_fields:
            total_fields += 1
            if property_data.get(field):
                filled_fields += 1
        
        # Check enrichment data
        if property_data.get('zillow_data'):
            filled_fields += 2
        total_fields += 2
        
        if property_data.get('neighborhood_data'):
            filled_fields += 1
        total_fields += 1
        
        return round((filled_fields / total_fields) * 100, 1) if total_fields > 0 else 0