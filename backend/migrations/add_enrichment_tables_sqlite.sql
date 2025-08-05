-- Add property enrichment table
CREATE TABLE property_enrichments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL UNIQUE,
    
    -- Zillow/Realty Data
    zillow_estimated_value DECIMAL(12,2),
    zillow_rent_estimate DECIMAL(10,2),
    zillow_last_sold_date DATETIME,
    zillow_last_sold_price DECIMAL(12,2),
    zillow_price_history TEXT,
    zillow_tax_history TEXT,
    zillow_url VARCHAR(500),
    zestimate DECIMAL(12,2),
    
    -- Google Maps Data
    formatted_address VARCHAR(500),
    place_id VARCHAR(100),
    neighborhood_data TEXT,
    
    -- County Additional Data
    owner_history TEXT,
    permit_history TEXT,
    lien_history TEXT,
    
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
    data_sources TEXT,
    data_quality_score DECIMAL(5,1),
    last_enriched_at DATETIME,
    enrichment_errors TEXT,
    
    -- Market Analysis
    comparable_sales TEXT,
    market_trend VARCHAR(20),
    days_on_market_average INTEGER,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (property_id) REFERENCES properties(id)
);

-- Create index for property enrichments
CREATE INDEX idx_property_enrichments_property_id ON property_enrichments(property_id);
CREATE INDEX idx_property_enrichments_investment_score ON property_enrichments(investment_score);

-- Add columns to properties table (run these individually and handle errors if columns exist)
-- ALTER TABLE properties ADD COLUMN latitude DECIMAL(10,6);
-- ALTER TABLE properties ADD COLUMN longitude DECIMAL(11,6);
-- ALTER TABLE properties ADD COLUMN square_footage INTEGER;
-- ALTER TABLE properties ADD COLUMN bedrooms INTEGER;
-- ALTER TABLE properties ADD COLUMN bathrooms DECIMAL(3,1);