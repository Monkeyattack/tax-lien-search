#!/usr/bin/env python3
"""
Script to import scraped LGBS data into the database
"""
import sys
sys.path.append('backend')

from backend.services.scrapers.lgbs_dallas_scraper import LGBSDallasScraper
from backend.database import SessionLocal
from backend.models.property import Property
from backend.models.county import County
from datetime import datetime

def import_lgbs_data():
    db = SessionLocal()
    
    try:
        # Get Dallas county
        dallas_county = db.query(County).filter(County.name == "Dallas").first()
        if not dallas_county:
            print("Dallas county not found!")
            return
        
        print(f"Using Dallas County ID: {dallas_county.id}")
        
        # Create scraper and get data
        scraper = LGBSDallasScraper()
        print("Scraping data from LGBS...")
        properties_data = scraper.scrape_upcoming_sales()
        print(f"Found {len(properties_data)} properties")
        
        if not properties_data:
            print("No properties returned by scraper")
            return
        
        # Save properties to database
        saved_count = 0
        skipped_count = 0
        
        for i, prop_data in enumerate(properties_data):
            try:
                # Extract parcel number or create unique ID
                parcel_number = prop_data.get('parcel_number') or prop_data.get('parcel_id') or f'LGBS-{i}'
                
                # Check if property already exists
                existing = db.query(Property).filter(
                    Property.parcel_number == parcel_number
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Create new property
                property = Property(
                    county_id=dallas_county.id,
                    parcel_number=parcel_number,
                    owner_name=prop_data.get('owner_name', 'Unknown'),
                    property_address=prop_data.get('property_address', ''),
                    city=prop_data.get('city', 'Dallas'),
                    state=prop_data.get('state', 'TX'),
                    zip_code=prop_data.get('zip_code', ''),
                    property_type=prop_data.get('property_type', 'Unknown'),
                    assessed_value=float(prop_data.get('assessed_value', 0)),
                    market_value=float(prop_data.get('market_value', 0)),
                    created_at=datetime.now()
                )
                
                # Add optional fields if available
                if 'latitude' in prop_data:
                    property.latitude = prop_data['latitude']
                if 'longitude' in prop_data:
                    property.longitude = prop_data['longitude']
                if 'year_built' in prop_data:
                    property.year_built = prop_data['year_built']
                if 'square_footage' in prop_data:
                    property.square_footage = prop_data['square_footage']
                if 'lot_size' in prop_data:
                    property.lot_size = prop_data['lot_size']
                
                db.add(property)
                saved_count += 1
                
                # Commit every 10 records
                if saved_count % 10 == 0:
                    db.commit()
                    print(f"Saved {saved_count} properties...")
                    
            except Exception as e:
                print(f"Error saving property {i}: {e}")
                continue
        
        # Final commit
        db.commit()
        print(f"\nImport complete:")
        print(f"  Saved: {saved_count} new properties")
        print(f"  Skipped: {skipped_count} existing properties")
        
        # Verify results
        total_count = db.query(Property).filter(Property.county_id == dallas_county.id).count()
        print(f"\nTotal Dallas properties in database: {total_count}")
        
        # Show samples
        samples = db.query(Property).filter(
            Property.county_id == dallas_county.id
        ).order_by(Property.created_at.desc()).limit(5).all()
        
        print("\nRecently added properties:")
        for prop in samples:
            print(f"  {prop.property_address}, {prop.city}")
            print(f"    Owner: {prop.owner_name}")
            print(f"    Value: ${prop.assessed_value:,.0f}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_lgbs_data()