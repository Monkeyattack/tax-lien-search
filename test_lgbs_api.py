#!/usr/bin/env python3
"""
Test script to explore LGBS API and find the correct endpoints
"""
import requests
from bs4 import BeautifulSoup
import json
import re

def test_lgbs_website():
    """Test various approaches to get data from LGBS"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    print("=== Testing LGBS Website ===")
    
    # Test 1: Main page
    print("\n1. Testing main page...")
    try:
        response = session.get('https://taxsales.lgbs.com/', timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Main page accessible")
            
            # Check if there's a redirect or specific Dallas URL
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for county links
            county_links = soup.find_all('a', href=re.compile(r'dallas|DALLAS', re.I))
            if county_links:
                print(f"   Found {len(county_links)} Dallas-related links")
                for link in county_links[:3]:
                    print(f"     - {link.get('href')}: {link.text.strip()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Dallas County specific URL
    print("\n2. Testing Dallas County URL...")
    dallas_urls = [
        'https://taxsales.lgbs.com/dallas-county-tx',
        'https://taxsales.lgbs.com/dallas',
        'https://taxsales.lgbs.com/TX/dallas',
        'https://taxsales.lgbs.com/?county=DALLAS%20COUNTY&state=TX'
    ]
    
    for url in dallas_urls:
        try:
            response = session.get(url, timeout=10)
            print(f"   {url}: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ Found working Dallas URL!")
                
                # Look for property data in the HTML
                html = response.text
                
                # Check for JSON data
                json_patterns = [
                    r'window\.__INITIAL_DATA__\s*=\s*({.*?});',
                    r'var\s+properties\s*=\s*(\[.*?\]);',
                    r'window\.properties\s*=\s*(\[.*?\]);',
                    r'data-properties=[\'"](.*?)[\'"]',
                ]
                
                for pattern in json_patterns:
                    match = re.search(pattern, html, re.DOTALL)
                    if match:
                        print(f"   Found JSON data with pattern: {pattern[:30]}...")
                        try:
                            data = json.loads(match.group(1))
                            if isinstance(data, list):
                                print(f"   Found {len(data)} properties")
                            elif isinstance(data, dict):
                                print(f"   Found data object with keys: {list(data.keys())[:5]}")
                        except:
                            print("   Could not parse JSON data")
                
                # Look for API endpoints in JavaScript
                api_patterns = [
                    r'[\'"]api[\'"]:\s*[\'"]([^\'\"]+)[\'"]',
                    r'apiUrl\s*=\s*[\'"]([^\'\"]+)[\'"]',
                    r'fetch\([\'"]([^\'\"]+)[\'"]',
                    r'ajax.*?url:\s*[\'"]([^\'\"]+)[\'"]',
                ]
                
                print("\n   Looking for API endpoints...")
                for pattern in api_patterns:
                    matches = re.findall(pattern, html)
                    if matches:
                        print(f"   Found API endpoints:")
                        for endpoint in set(matches[:5]):
                            print(f"     - {endpoint}")
                
                break
        except Exception as e:
            print(f"   Error: {e}")
    
    # Test 3: Search/filter endpoints
    print("\n3. Testing search endpoints...")
    search_endpoints = [
        'https://taxsales.lgbs.com/api/properties',
        'https://taxsales.lgbs.com/api/sales',
        'https://taxsales.lgbs.com/api/search',
        'https://taxsales.lgbs.com/properties.json',
        'https://taxsales.lgbs.com/sales.json',
    ]
    
    params = {
        'county': 'DALLAS COUNTY',
        'state': 'TX',
        'limit': 10
    }
    
    for endpoint in search_endpoints:
        try:
            response = session.get(endpoint, params=params, timeout=10)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✓ Found working API endpoint!")
                    print(f"   Response type: {type(data)}")
                    if isinstance(data, list):
                        print(f"   Contains {len(data)} items")
                    elif isinstance(data, dict):
                        print(f"   Keys: {list(data.keys())}")
                except:
                    print("   Response is not JSON")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Test 4: Check robots.txt and sitemap
    print("\n4. Checking robots.txt and sitemap...")
    try:
        robots_response = session.get('https://taxsales.lgbs.com/robots.txt', timeout=10)
        if robots_response.status_code == 200:
            print("   robots.txt content:")
            for line in robots_response.text.split('\n')[:10]:
                if line.strip():
                    print(f"     {line}")
    except:
        pass

if __name__ == "__main__":
    test_lgbs_website()