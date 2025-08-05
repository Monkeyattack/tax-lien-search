# Tax Lien Scrapers and Property Enrichment

This directory contains scrapers for various county tax sale websites and property enrichment services.

## Available Scrapers

### 1. Collin County Scraper (`collin_county_scraper.py`)
- **Source**: Collin County official website
- **Type**: In-person auctions
- **Features**: Monthly tax sales, PDF parsing

### 2. Dallas County Scraper (`dallas_county_scraper.py`)
- **Source**: RealAuction.com
- **Type**: Online auctions
- **Features**: API integration, real-time bidding info

### 3. LGBS Dallas Scraper (`lgbs_dallas_scraper.py`)
- **Source**: taxsales.lgbs.com
- **URL**: https://taxsales.lgbs.com/map?county=DALLAS%20COUNTY&state=TX
- **Type**: Comprehensive tax sale listings
- **Features**: 
  - Batch property fetching
  - Geolocation data
  - Multiple sale types (SALE, RESALE, STRUCK OFF)
  - Progress tracking

## Property Enrichment

### Zillow Public Data Scraper (`zillow_public_scraper.py`)
Scrapes publicly available property data from Zillow without requiring API keys:
- Property details (bedrooms, bathrooms, square footage)
- Zestimate values
- Price history
- Tax history
- Nearby schools with ratings
- Neighborhood information (Walk Score, Transit Score)
- Rental estimates

### Property Enrichment Service (`property_enrichment_service.py`)
Combines data from multiple sources:
1. **Zillow Data**: Property values, details, history
2. **Google Maps** (optional with API key):
   - Geocoding for exact coordinates
   - Nearby amenities (schools, hospitals, parks)
   - Neighborhood demographics
3. **Investment Metrics**:
   - ROI percentage
   - Cap rate
   - Cash-on-cash return
   - Investment score (0-100)

## Usage

### Running a Scraper

```python
from services.scrapers.lgbs_dallas_scraper import LGBSDallasScraper

scraper = LGBSDallasScraper()

# Set progress callback (optional)
def progress_callback(progress, message, properties_found, sales_found):
    print(f"{progress}% - {message}")
    
scraper.set_progress_callback(progress_callback)

# Scrape properties
sales = scraper.scrape_upcoming_sales()
```

### Enriching Properties

```python
from services.property_enrichment_service import PropertyEnrichmentService

enrichment_service = PropertyEnrichmentService()

property_data = {
    'property_address': '123 Main St',
    'city': 'Dallas',
    'state': 'TX',
    'zip_code': '75201',
    'assessed_value': 250000
}

enriched = enrichment_service.enrich_property(property_data)
```

## API Endpoints

### Scrape County Data
```
POST /api/data-import/scrape/{county_code}
```

County codes:
- `collin` - Collin County
- `dallas` - Dallas County (RealAuction)
- `dallas-lgbs` - Dallas County (LGBS system)

### Check Scraping Status
```
GET /api/data-import/scrape/status/{job_id}
```

## Environment Variables (Optional)

```env
# Google Maps API for geocoding and neighborhood data
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Not needed - we use public Zillow data
# ZILLOW_API_KEY=not_required
# RAPIDAPI_KEY=not_required
```

## Data Quality

Each enriched property receives a data quality score (0-100) based on:
- Completeness of basic fields
- Availability of enrichment data
- Accuracy of coordinates
- Presence of valuation data

## Investment Scoring

Properties are scored 0-100 based on:
- **ROI Factor** (30 points max):
  - >100% ROI: 30 points
  - 50-100% ROI: 20 points
  - 25-50% ROI: 10 points
- **Location Factor** (20 points max):
  - Low crime area: 10 points
  - Good schools (>7 rating): 10 points
- **Property Condition** (20 points max):
  - Built after 2000: 20 points
  - Built 1980-2000: 10 points

## Rate Limiting

All scrapers implement respectful rate limiting:
- Zillow: 1 second between requests
- Google Maps: 0.1 seconds between API calls
- LGBS: 1 second between batch requests

## Error Handling

- All scrapers use try-except blocks with logging
- Failed enrichments don't block the scraping process
- Partial data is better than no data
- Mock data is provided when external services fail

## Future Enhancements

1. **Additional Counties**: Add more Texas counties
2. **More Data Sources**: 
   - Redfin public data
   - Realtor.com listings
   - County appraisal districts
3. **Machine Learning**: Predict redemption likelihood
4. **Historical Analysis**: Track property performance over time