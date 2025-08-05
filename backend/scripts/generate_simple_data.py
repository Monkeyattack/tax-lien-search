#!/usr/bin/env python3
"""
Simple data population script that works with current schema
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, date
import random
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import County, Property, TaxSale, PropertyValuation

def main():
    """Populate sample data"""
    print("Populating sample data...")
    
    db = SessionLocal()
    try:
        # Check existing data
        properties = db.query(Property).all()
        print(f"Found {len(properties)} existing properties")
        
        if not properties:
            print("No properties found. Please run scraper or import CSV first.")
            return
        
        # Create property valuations for existing properties
        print("Creating property valuations...")
        for prop in properties[:20]:  # First 20 properties
            # Skip if already has valuations
            existing_val = db.query(PropertyValuation).filter(
                PropertyValuation.property_id == prop.id
            ).first()
            
            if not existing_val:
                # Use assessed value or market value from property
                value = prop.assessed_value or prop.market_value or random.randint(100000, 500000)
                
                valuation = PropertyValuation(
                    property_id=prop.id,
                    valuation_date=date.today(),
                    estimated_value=value,
                    valuation_source='county_assessor',
                    notes='Initial valuation from county data'
                )
                db.add(valuation)
        
        db.commit()
        print("Created property valuations")
        
        # Create some tax sales for properties without sales
        print("Creating tax sales...")
        properties_without_sales = []
        for prop in properties:
            existing_sale = db.query(TaxSale).filter(
                TaxSale.property_id == prop.id
            ).first()
            if not existing_sale:
                properties_without_sales.append(prop)
        
        # Create sales for 30% of properties without sales
        sale_count = min(20, int(len(properties_without_sales) * 0.3))
        for prop in properties_without_sales[:sale_count]:
            # Calculate amounts based on property value
            property_value = float(prop.assessed_value or prop.market_value or 200000)
            tax_rate = 0.025  # 2.5% tax rate
            years_delinquent = random.randint(1, 3)
            
            taxes_owed = property_value * tax_rate * years_delinquent
            interest_penalties = taxes_owed * 0.18 * years_delinquent
            court_costs = random.uniform(500, 2000)
            attorney_fees = random.uniform(1000, 5000)
            total_judgment = taxes_owed + interest_penalties + court_costs + attorney_fees
            
            # Future sale date
            sale_date = date.today() + timedelta(days=random.randint(30, 90))
            
            tax_sale = TaxSale(
                property_id=prop.id,
                county_id=prop.county_id,
                sale_date=sale_date,
                minimum_bid=total_judgment,
                taxes_owed=taxes_owed,
                interest_penalties=interest_penalties,
                court_costs=court_costs,
                attorney_fees=attorney_fees,
                total_judgment=total_judgment,
                sale_status='scheduled',
                constable_precinct=str(random.randint(1, 4)),
                case_number=f'TX-{sale_date.year}-{random.randint(100000, 999999)}'
            )
            db.add(tax_sale)
        
        db.commit()
        print(f"Created {sale_count} tax sales")
        
        # Summary
        total_properties = db.query(Property).count()
        total_sales = db.query(TaxSale).count()
        upcoming_sales = db.query(TaxSale).filter(
            TaxSale.sale_status == 'scheduled',
            TaxSale.sale_date >= date.today()
        ).count()
        
        print(f"\nData Summary:")
        print(f"- Total properties: {total_properties}")
        print(f"- Total tax sales: {total_sales}")
        print(f"- Upcoming sales: {upcoming_sales}")
        
    finally:
        db.close()
    
    print("\nData population complete!")

if __name__ == "__main__":
    main()