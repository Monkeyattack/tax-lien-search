#!/usr/bin/env python3
"""
Test Google Maps API integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from services.property_enrichment_service import PropertyEnrichmentService
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_maps():
    """Test Google Maps geocoding and places"""
    enrichment_service = PropertyEnrichmentService()
    
    # Test property with a real Dallas address
    test_property = {
        'property_address': '2711 N Haskell Ave',
        'city': 'Dallas',
        'state': 'TX',
        'zip_code': '75204'
    }
    
    logger.info(f"Testing property: {test_property['property_address']}, {test_property['city']}, {test_property['state']}")
    
    # Test geocoding
    coords = enrichment_service._geocode_address(test_property)
    if coords:
        logger.info(f"  Geocoding successful!")
        logger.info(f"  - Latitude: {coords['latitude']}")
        logger.info(f"  - Longitude: {coords['longitude']}")
        logger.info(f"  - Formatted address: {coords.get('formatted_address')}")
        logger.info(f"  - Place ID: {coords.get('place_id')}")
        
        # Test Street View URL
        street_view_url = enrichment_service._get_street_view_url(
            coords['latitude'], 
            coords['longitude']
        )
        logger.info(f"  - Street View URL: {street_view_url[:100]}...")
        
        # Test Google Maps URL
        maps_url = enrichment_service._get_google_maps_url(
            coords['latitude'],
            coords['longitude'],
            test_property['property_address']
        )
        logger.info(f"  - Google Maps URL: {maps_url}")
        
        # Test nearby schools
        schools = enrichment_service._get_nearby_schools(
            coords['latitude'],
            coords['longitude']
        )
        logger.info(f"  - Found {len(schools)} nearby schools:")
        for school in schools[:3]:
            logger.info(f"    • {school['name']} - Rating: {school['rating']}/5, Distance: {school['distance_miles']} miles")
        
        # Test neighborhood data
        neighborhood = enrichment_service._get_neighborhood_data(
            coords['latitude'],
            coords['longitude']
        )
        if neighborhood:
            logger.info(f"  - Neighborhood data collected: {list(neighborhood.keys())}")
    else:
        logger.error("  Geocoding failed!")

if __name__ == "__main__":
    logger.info("Starting Google Maps API test...")
    test_google_maps()
    logger.info("Test complete!")