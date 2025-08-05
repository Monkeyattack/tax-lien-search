#!/usr/bin/env python3
"""
Generate sample tax lien data for testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, date
from decimal import Decimal
import random
from faker import Faker
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import County, Property, TaxSale, PropertyValuation, User

fake = Faker()

def create_counties(db: Session):
    """Create Texas counties"""
    counties_data = [
        {"name": "Dallas County", "state": "TX"},
        {"name": "Collin County", "state": "TX"},
        {"name": "Tarrant County", "state": "TX"},
        {"name": "Denton County", "state": "TX"},
        {"name": "Harris County", "state": "TX"},
    ]
    
    counties = []
    for data in counties_data:
        county = db.query(County).filter(County.name == data["name"]).first()
        if not county:
            county = County(**data)
            db.add(county)
            db.commit()
            db.refresh(county)
        counties.append(county)
    
    return counties

def create_properties(db: Session, counties: list, count: int = 50):
    """Create sample properties"""
    property_types = ['Residential', 'Commercial', 'Vacant Land', 'Industrial']
    
    properties = []
    for i in range(count):
        county = random.choice(counties)
        
        # Generate realistic Texas addresses
        property_data = {
            'parcel_number': f'{county.id:02d}-{fake.random_number(digits=8):08d}',
            'owner_name': fake.name(),
            'property_address': fake.street_address(),
            'city': fake.city(),
            'state': 'TX',
            'zip_code': fake.zipcode()[:5],
            'property_type': random.choice(property_types),
            'year_built': random.randint(1950, 2020) if random.random() > 0.2 else None,
            'square_footage': random.randint(800, 5000) if random.random() > 0.3 else None,
            'lot_size': random.randint(5000, 43560),  # 5,000 to 43,560 sq ft (1 acre)
            'bedrooms': random.randint(1, 5) if random.random() > 0.4 else None,
            'bathrooms': random.uniform(1, 4) if random.random() > 0.4 else None,
            'county_id': county.id,
            'latitude': round(32.7767 + random.uniform(-2, 2), 6),  # Around Dallas
            'longitude': round(-96.7970 + random.uniform(-2, 2), 6),
        }
        
        # Set exemptions
        if property_data['property_type'] == 'Residential':
            property_data['homestead_exemption'] = random.random() > 0.7
        property_data['senior_exemption'] = random.random() > 0.8
        property_data['agricultural_exemption'] = property_data['property_type'] == 'Vacant Land' and random.random() > 0.6
        
        # Check if property exists
        existing = db.query(Property).filter(
            Property.parcel_number == property_data['parcel_number']
        ).first()
        
        if not existing:
            property_obj = Property(**property_data)
            db.add(property_obj)
            db.commit()
            db.refresh(property_obj)
            properties.append(property_obj)
        else:
            properties.append(existing)
    
    return properties

def create_property_valuations(db: Session, properties: list):
    """Create property valuations"""
    current_year = datetime.now().year
    
    for property_obj in properties:
        # Create valuations for last 3 years
        for year_offset in range(3):
            year = current_year - year_offset
            
            # Check if valuation exists
            existing = db.query(PropertyValuation).filter(
                PropertyValuation.property_id == property_obj.id,
                PropertyValuation.tax_year == year
            ).first()
            
            if not existing:
                base_value = random.randint(50000, 500000)
                market_value = base_value * (1 + (year_offset * 0.05))  # 5% appreciation per year
                
                valuation = PropertyValuation(
                    property_id=property_obj.id,
                    tax_year=year,
                    market_value=market_value,
                    assessed_value=market_value * 0.8,  # 80% of market value
                    land_value=market_value * random.uniform(0.2, 0.4),
                    improvement_value=market_value * random.uniform(0.6, 0.8),
                    exemption_amount=market_value * 0.1 if property_obj.homestead_exemption else 0
                )
                db.add(valuation)
        
    db.commit()

def create_tax_sales(db: Session, properties: list):
    """Create upcoming and past tax sales"""
    today = date.today()
    
    # Select 30% of properties for tax sales
    sale_properties = random.sample(properties, int(len(properties) * 0.3))
    
    tax_sales = []
    for property_obj in sale_properties:
        # Get latest valuation
        valuation = db.query(PropertyValuation).filter(
            PropertyValuation.property_id == property_obj.id
        ).order_by(PropertyValuation.tax_year.desc()).first()
        
        if not valuation:
            continue
            
        # Calculate amounts
        assessed_value = float(valuation.assessed_value)
        tax_rate = 0.025  # 2.5% tax rate
        years_delinquent = random.randint(1, 3)
        
        taxes_owed = assessed_value * tax_rate * years_delinquent
        interest_penalties = taxes_owed * 0.18 * years_delinquent  # 18% penalty per year
        court_costs = random.uniform(500, 2000)
        attorney_fees = random.uniform(1000, 5000)
        
        total_judgment = taxes_owed + interest_penalties + court_costs + attorney_fees
        minimum_bid = total_judgment  # In Texas, minimum bid is total judgment
        
        # Set sale date (some past, most future)
        if random.random() > 0.7:  # 30% past sales
            sale_date = today - timedelta(days=random.randint(30, 365))
            sale_status = 'sold' if random.random() > 0.3 else 'struck_off'
        else:  # 70% upcoming sales
            sale_date = today + timedelta(days=random.randint(7, 90))
            sale_status = 'scheduled'
        
        tax_sale = TaxSale(
            property_id=property_obj.id,
            county_id=property_obj.county_id,
            sale_date=sale_date,
            minimum_bid=minimum_bid,
            taxes_owed=taxes_owed,
            interest_penalties=interest_penalties,
            court_costs=court_costs,
            attorney_fees=attorney_fees,
            total_judgment=total_judgment,
            sale_status=sale_status,
            constable_precinct=str(random.randint(1, 4)),
            case_number=f'TX-{sale_date.year}-{fake.random_number(digits=6):06d}'
        )
        
        # If sold, add winning bid info
        if sale_status == 'sold':
            tax_sale.winning_bid = minimum_bid * random.uniform(1.0, 1.5)
            tax_sale.winner_info = fake.name()
        
        db.add(tax_sale)
        tax_sales.append(tax_sale)
    
    db.commit()
    return tax_sales

def main():
    """Generate sample data"""
    print("Creating sample data...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create counties
        print("Creating counties...")
        counties = create_counties(db)
        print(f"Created {len(counties)} counties")
        
        # Create properties
        print("Creating properties...")
        properties = create_properties(db, counties, count=100)
        print(f"Created {len(properties)} properties")
        
        # Create property valuations
        print("Creating property valuations...")
        create_property_valuations(db, properties)
        
        # Create tax sales
        print("Creating tax sales...")
        tax_sales = create_tax_sales(db, properties)
        print(f"Created {len(tax_sales)} tax sales")
        
        # Summary
        upcoming_sales = [s for s in tax_sales if s.sale_status == 'scheduled']
        print(f"\nSummary:")
        print(f"- Total properties: {len(properties)}")
        print(f"- Total tax sales: {len(tax_sales)}")
        print(f"- Upcoming sales: {len(upcoming_sales)}")
        print(f"- Counties: {', '.join([c.name for c in counties])}")
        
    finally:
        db.close()
    
    print("\nSample data generation complete!")

if __name__ == "__main__":
    main()