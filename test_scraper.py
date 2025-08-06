#!/usr/bin/env python3
"""
Test script for the tax lien scraper
Run this to test scraper functionality without triggering full scrapes
"""
import sys
import os
import sqlite3
import requests
from datetime import datetime

# Add backend to path
sys.path.append('backend')

def check_database():
    """Check current database state"""
    print('=== Database Status ===')
    try:
        conn = sqlite3.connect('backend/tax_liens.db')
        cursor = conn.cursor()
        
        # Check tables and counts
        tables_to_check = ['counties', 'properties', 'scraping_jobs', 'users']
        for table in tables_to_check:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                print(f'{table}: {count} records')
            except:
                print(f'{table}: table not found')
        
        # Check sample properties
        cursor.execute('SELECT property_address, city, assessed_value FROM properties LIMIT 3')
        props = cursor.fetchall()
        if props:
            print('\nSample properties:')
            for prop in props:
                print(f'  {prop[0]}, {prop[1]} - ${prop[2]}')
        
        conn.close()
        print('✓ Database accessible')
        
    except Exception as e:
        print(f'✗ Database error: {e}')

def test_scraper_import():
    """Test if scraper can be imported and instantiated"""
    print('\n=== Scraper Import Test ===')
    try:
        from backend.services.scrapers.lgbs_dallas_scraper import LGBSDallasScraper
        print('✓ LGBS scraper imported successfully')
        
        scraper = LGBSDallasScraper()
        print('✓ Scraper instance created successfully')
        
        # Test parse_property_details with mock data
        mock_data = {
            'parcel_id': 'TEST123',
            'owner_name': 'John Doe', 
            'property_address': '123 Main St',
            'city': 'Dallas',
            'state': 'TX',
            'zip': '75201',
            'assessed_value': 150000,
            'taxes_owed': 5000,
            'minimum_bid': 8000
        }
        
        parsed = scraper.parse_property_details(mock_data)
        print('✓ parse_property_details working:')
        print(f'  Address: {parsed["property_address"]}')
        print(f'  Owner: {parsed["owner_name"]}')
        print(f'  Value: ${parsed["assessed_value"]}')
        
        return scraper
        
    except Exception as e:
        print(f'✗ Scraper import failed: {e}')
        import traceback
        traceback.print_exc()
        return None

def test_api_endpoints():
    """Test scraper API endpoints"""
    print('\n=== API Endpoints Test ===')
    base_url = 'https://tax.profithits.app/api'
    
    endpoints_to_test = [
        '/counties',
        '/data-import/counties', 
        '/property-search/filters'
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
            print(f'{endpoint}: {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f'  Returns {len(data)} items')
                elif isinstance(data, dict):
                    print(f'  Returns dict with keys: {list(data.keys())}')
        except Exception as e:
            print(f'{endpoint}: Error - {e}')

def manual_scrape_test():
    """Manually test a small scrape operation"""
    print('\n=== Manual Scrape Test ===')
    scraper = test_scraper_import()
    if not scraper:
        return
    
    try:
        print('Testing LGBS API connection...')
        
        # Try to make a simple request to LGBS
        import requests
        test_url = 'https://taxsales.lgbs.com'
        response = requests.get(test_url, timeout=10)
        print(f'LGBS website response: {response.status_code}')
        
        if response.status_code == 200:
            print('✓ LGBS website is accessible')
            
            # Test API endpoint
            api_url = 'https://taxsales.lgbs.com/api/tax_sales'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            try:
                api_response = requests.get(api_url, headers=headers, timeout=10)
                print(f'LGBS API response: {api_response.status_code}')
                
                if api_response.status_code == 200:
                    print('✓ LGBS API is accessible')
                else:
                    print('⚠ LGBS API may require different parameters or authentication')
                    
            except Exception as e:
                print(f'LGBS API test failed: {e}')
        else:
            print('⚠ LGBS website not accessible - may be blocking requests')
            
    except Exception as e:
        print(f'Manual scrape test failed: {e}')

def create_test_data():
    """Create some test properties for frontend testing"""
    print('\n=== Creating Test Data ===')
    try:
        conn = sqlite3.connect('backend/tax_liens.db')
        cursor = conn.cursor()
        
        # Check if we have Dallas county
        cursor.execute('SELECT id FROM counties WHERE county_name LIKE "%Dallas%" LIMIT 1')
        county_result = cursor.fetchone()
        
        if not county_result:
            print('No Dallas county found, creating one...')
            cursor.execute('''
                INSERT INTO counties (county_name, county_state, auction_type, redemption_period_months, expected_penalty_rate)
                VALUES (?, ?, ?, ?, ?)
            ''', ('Dallas County', 'TX', 'online', 6, 25))
            county_id = cursor.lastrowid
        else:
            county_id = county_result[0]
            
        print(f'Using county_id: {county_id}')
        
        # Create a few test properties
        test_properties = [
            {
                'parcel_number': 'TEST001',
                'owner_name': 'John Smith',
                'property_address': '123 Main Street',
                'city': 'Dallas',
                'state': 'TX',
                'zip_code': '75201',
                'property_type': 'Residential',
                'assessed_value': 180000,
                'market_value': 200000,
                'square_footage': 1500,
                'bedrooms': 3,
                'bathrooms': 2,
                'year_built': 1995,
                'county_id': county_id,
                'redemption_period_months': 6,
                'expected_penalty_rate': 25
            },
            {
                'parcel_number': 'TEST002', 
                'owner_name': 'Jane Doe',
                'property_address': '456 Oak Avenue',
                'city': 'Dallas',
                'state': 'TX',
                'zip_code': '75202',
                'property_type': 'Residential',
                'assessed_value': 250000,
                'market_value': 275000,
                'square_footage': 2000,
                'bedrooms': 4,
                'bathrooms': 3,
                'year_built': 2005,
                'county_id': county_id,
                'redemption_period_months': 6,
                'expected_penalty_rate': 25
            }
        ]
        
        for prop in test_properties:
            # Check if property already exists
            cursor.execute('SELECT id FROM properties WHERE parcel_number = ?', (prop['parcel_number'],))
            if not cursor.fetchone():
                columns = ', '.join(prop.keys())
                placeholders = ', '.join(['?' for _ in prop.values()])
                
                cursor.execute(f'''
                    INSERT INTO properties ({columns})
                    VALUES ({placeholders})
                ''', list(prop.values()))
                
                print(f'Created test property: {prop["property_address"]}')
        
        conn.commit()
        conn.close()
        print('✓ Test data created successfully')
        
    except Exception as e:
        print(f'✗ Failed to create test data: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print('Tax Lien Scraper Test Suite')
    print('=' * 50)
    
    check_database()
    test_scraper_import() 
    test_api_endpoints()
    manual_scrape_test()
    
    # Ask if user wants to create test data
    create_test = input('\nCreate test properties for frontend testing? (y/n): ')
    if create_test.lower() == 'y':
        create_test_data()
    
    print('\n=== Test Complete ===')
    print('Next steps to test scraper:')
    print('1. Check the frontend at https://tax.profithits.app')
    print('2. Try the "Data Import" page to manually trigger scraping')
    print('3. Check the Properties page to see if data appears')
    print('4. Look at PM2 logs: ssh root@172.93.51.42 "pm2 logs tax-lien-api"')