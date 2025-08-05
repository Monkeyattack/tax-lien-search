-- Add property enrichment table
CREATE TABLE IF NOT EXISTS property_enrichments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL UNIQUE,
    
    -- Zillow/Realty Data
    zillow_estimated_value DECIMAL(12,2),
    zillow_rent_estimate DECIMAL(10,2),
    zillow_last_sold_date DATETIME,
    zillow_last_sold_price DECIMAL(12,2),
    zillow_price_history JSON,
    zillow_tax_history JSON,
    zillow_url VARCHAR(500),
    zestimate DECIMAL(12,2),
    
    -- Google Maps Data
    formatted_address VARCHAR(500),
    place_id VARCHAR(100),
    neighborhood_data JSON,
    
    -- County Additional Data
    owner_history JSON,
    permit_history JSON,
    lien_history JSON,
    
    -- Investment Metrics
    estimated_rehab_cost DECIMAL(10,2),
    estimated_arv DECIMAL(12,2),
    monthly_rent_estimate DECIMAL(10,2),
    gross_rent_multiplier DECIMAL(6,2),
    cap_rate DECIMAL(5,2),
    cash_on_cash_return DECIMAL(5,2),
    roi_percentage DECIMAL(6,2),
    investment_score DECIMAL(5,1),
    
    -- External IDs
    lgbs_id VARCHAR(50),
    dallas_cad_account VARCHAR(50),
    redfin_id VARCHAR(50),
    realtor_id VARCHAR(50),
    
    -- Data Quality
    data_sources JSON,
    data_quality_score DECIMAL(5,1),
    last_enriched_at DATETIME,
    enrichment_errors JSON,
    
    -- Market Analysis
    comparable_sales JSON,
    market_trend VARCHAR(20),
    days_on_market_average INTEGER,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (property_id) REFERENCES properties(id)
);

-- Add missing columns to properties table if they don't exist
ALTER TABLE properties ADD COLUMN IF NOT EXISTS latitude DECIMAL(10,6);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS longitude DECIMAL(11,6);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS square_footage INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS bedrooms INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS bathrooms DECIMAL(3,1);

-- Create index for property enrichments
CREATE INDEX IF NOT EXISTS idx_property_enrichments_property_id ON property_enrichments(property_id);
CREATE INDEX IF NOT EXISTS idx_property_enrichments_investment_score ON property_enrichments(investment_score);

-- Update scraping_jobs table to add message column if missing
ALTER TABLE scraping_jobs ADD COLUMN IF NOT EXISTS message TEXT;