#!/usr/bin/env python3
"""
Test script to enrich existing properties with Zillow data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Property, PropertyEnrichment
from services.property_enrichment_service import PropertyEnrichmentService
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = "sqlite:///tax_liens.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def enrich_test_properties():
    """Enrich the first few properties with addresses"""
    db = SessionLocal()
    enrichment_service = PropertyEnrichmentService()
    
    try:
        # Get properties with addresses but no enrichment
        properties = db.query(Property).filter(
            Property.property_address != None,
            Property.property_address != ''
        ).limit(3).all()
        
        logger.info(f"Found {len(properties)} properties to enrich")
        
        for prop in properties:
            # Check if already enriched
            existing_enrichment = db.query(PropertyEnrichment).filter(
                PropertyEnrichment.property_id == prop.id
            ).first()
            
            if existing_enrichment:
                logger.info(f"Property {prop.id} already has enrichment, skipping")
                continue
            
            logger.info(f"Enriching property {prop.id}: {prop.property_address}, {prop.city}, TX")
            
            # Prepare property data
            property_data = {
                'id': prop.id,
                'parcel_number': prop.parcel_number,
                'property_address': prop.property_address,
                'city': prop.city,
                'state': prop.state or 'TX',
                'zip_code': prop.zip_code,
                'owner_name': prop.owner_name,
                'property_type': prop.property_type,
                'assessed_value': float(prop.assessed_value) if prop.assessed_value else None,
                'market_value': float(prop.market_value) if prop.market_value else None,
            }
            
            # Get enrichment data
            enriched_data = enrichment_service.enrich_property(property_data)
            
            # Create enrichment record
            enrichment = PropertyEnrichment(property_id=prop.id)
            
            # Update from Zillow data
            zillow_data = enriched_data.get('zillow_data', {})
            if zillow_data:
                enrichment.zestimate = zillow_data.get('zestimate')
                enrichment.zillow_estimated_value = zillow_data.get('estimated_value')
                enrichment.zillow_rent_estimate = zillow_data.get('rent_estimate')
                enrichment.monthly_rent_estimate = zillow_data.get('rent_estimate')
                enrichment.zillow_price_history = zillow_data.get('price_history', [])
                enrichment.zillow_tax_history = zillow_data.get('tax_history', [])
                enrichment.zillow_url = zillow_data.get('zillow_url')
                
                # Calculate simple investment score
                if enrichment.zestimate and prop.assessed_value:
                    # Higher score if Zestimate is higher than assessed value
                    value_ratio = enrichment.zestimate / float(prop.assessed_value)
                    enrichment.investment_score = min(100, max(0, value_ratio * 50))
                    
                    # Simple ROI calculation
                    if enrichment.monthly_rent_estimate:
                        annual_rent = enrichment.monthly_rent_estimate * 12
                        enrichment.roi_percentage = (annual_rent / float(prop.assessed_value)) * 100
                        enrichment.cap_rate = enrichment.roi_percentage
                
                logger.info(f"  - Zestimate: ${enrichment.zestimate}")
                logger.info(f"  - Rent Estimate: ${enrichment.monthly_rent_estimate}/mo")
                logger.info(f"  - Investment Score: {enrichment.investment_score}")
            
            # Update neighborhood data
            enrichment.neighborhood_data = enriched_data.get('neighborhood_data', {})
            
            # Set metadata
            enrichment.data_quality_score = 75  # Mock quality score
            enrichment.last_enriched_at = datetime.now()
            
            db.add(enrichment)
            db.commit()
            
            logger.info(f"Successfully enriched property {prop.id}")
            
    except Exception as e:
        logger.error(f"Error during enrichment: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting property enrichment test...")
    enrich_test_properties()
    logger.info("Enrichment test complete!")