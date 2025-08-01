-- Tax Lien Search Database Schema
-- Texas Tax Deed Investment Tracking System

-- Users table for authentication
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Counties table for Texas counties
CREATE TABLE counties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    state VARCHAR(2) DEFAULT 'TX',
    auction_schedule VARCHAR(255), -- e.g., "First Tuesday of each month"
    auction_location VARCHAR(255),
    auction_type VARCHAR(50), -- 'in_person', 'online', 'hybrid'
    website_url VARCHAR(255),
    contact_info TEXT,
    special_procedures TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Properties table for tax sale properties
CREATE TABLE properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    county_id INTEGER REFERENCES counties(id),
    property_address VARCHAR(255) NOT NULL,
    legal_description TEXT,
    appraisal_district_id VARCHAR(50),
    property_type VARCHAR(50), -- 'residential', 'commercial', 'land', 'agricultural'
    assessed_value DECIMAL(12,2),
    market_value DECIMAL(12,2),
    lot_size DECIMAL(10,2),
    square_feet INTEGER,
    year_built INTEGER,
    homestead_exemption BOOLEAN DEFAULT FALSE,
    agricultural_exemption BOOLEAN DEFAULT FALSE,
    mineral_rights BOOLEAN DEFAULT FALSE,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tax sales table for tracking specific sales events
CREATE TABLE tax_sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER REFERENCES properties(id),
    county_id INTEGER REFERENCES counties(id),
    sale_date DATE NOT NULL,
    minimum_bid DECIMAL(12,2) NOT NULL,
    taxes_owed DECIMAL(12,2) NOT NULL,
    interest_penalties DECIMAL(12,2) DEFAULT 0,
    court_costs DECIMAL(12,2) DEFAULT 0,
    attorney_fees DECIMAL(12,2) DEFAULT 0,
    total_judgment DECIMAL(12,2) NOT NULL,
    sale_status VARCHAR(50) DEFAULT 'scheduled', -- 'scheduled', 'sold', 'struck_off', 'cancelled'
    winning_bid DECIMAL(12,2),
    winner_info VARCHAR(255),
    constable_precinct VARCHAR(10),
    case_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User investments table for tracking purchases
CREATE TABLE investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    tax_sale_id INTEGER REFERENCES tax_sales(id),
    property_id INTEGER REFERENCES properties(id),
    purchase_date DATE NOT NULL,
    purchase_amount DECIMAL(12,2) NOT NULL,
    deed_recording_fee DECIMAL(8,2) DEFAULT 0,
    other_costs DECIMAL(10,2) DEFAULT 0,
    total_investment DECIMAL(12,2) NOT NULL,
    deed_type VARCHAR(50), -- 'constable', 'sheriff', 'quitclaim'
    deed_recorded_date DATE,
    deed_volume VARCHAR(20),
    deed_page VARCHAR(20),
    redemption_period_months INTEGER NOT NULL, -- 6 or 24
    redemption_deadline DATE NOT NULL,
    investment_status VARCHAR(50) DEFAULT 'active', -- 'active', 'redeemed', 'clear_title', 'sold'
    expected_return_pct DECIMAL(5,2), -- 25 or 50
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Redemptions table for tracking when properties are redeemed
CREATE TABLE redemptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    investment_id INTEGER REFERENCES investments(id),
    redemption_date DATE NOT NULL,
    redemption_amount DECIMAL(12,2) NOT NULL,
    penalty_amount DECIMAL(12,2) NOT NULL,
    penalty_percentage DECIMAL(5,2) NOT NULL,
    days_held INTEGER NOT NULL,
    annualized_return DECIMAL(8,4) NOT NULL,
    redeemer_info VARCHAR(255),
    payment_method VARCHAR(50),
    county_processing_fee DECIMAL(8,2) DEFAULT 0,
    net_profit DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Property valuations for tracking market values over time
CREATE TABLE property_valuations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER REFERENCES properties(id),
    valuation_date DATE NOT NULL,
    estimated_value DECIMAL(12,2) NOT NULL,
    valuation_source VARCHAR(100), -- 'county_assessor', 'zillow', 'manual', 'appraisal'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts and notifications
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    investment_id INTEGER REFERENCES investments(id),
    alert_type VARCHAR(50) NOT NULL, -- 'redemption_deadline', 'auction_reminder', 'payment_due'
    alert_date DATE NOT NULL,
    message TEXT NOT NULL,
    is_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents storage for tracking important files
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    investment_id INTEGER REFERENCES investments(id),
    property_id INTEGER REFERENCES properties(id),
    document_type VARCHAR(50) NOT NULL, -- 'deed', 'receipt', 'judgment', 'appraisal', 'photo'
    document_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_size_bytes INTEGER,
    mime_type VARCHAR(100),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Research notes for property analysis
CREATE TABLE research_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    property_id INTEGER REFERENCES properties(id),
    note_date DATE DEFAULT (DATE('now')),
    note_type VARCHAR(50), -- 'title_search', 'market_analysis', 'inspection', 'legal'
    content TEXT NOT NULL,
    is_important BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default counties
INSERT INTO counties (name, auction_schedule, auction_location, auction_type, website_url, special_procedures) VALUES
('Collin', 'First Tuesday of each month, 10:00 AM - 4:00 PM', 'Collin County Courthouse steps, McKinney', 'in_person', 'https://www.collincountytx.gov/Tax-Assessor/properties-for-sale', 'Requires $10 no-taxes-due certificate obtained in advance. Cash/cashier''s check required immediately.'),
('Dallas', 'First Tuesday of each month (online)', 'Online via RealAuction platform', 'online', 'https://dallas.texas.sheriffsaleauctions.com', 'Online bidding requires registration and deposit. Wire transfer/cashier''s check payment required by next business day.');

-- Create indexes for better performance
CREATE INDEX idx_properties_county ON properties(county_id);
CREATE INDEX idx_properties_address ON properties(property_address);
CREATE INDEX idx_tax_sales_date ON tax_sales(sale_date);
CREATE INDEX idx_tax_sales_status ON tax_sales(sale_status);
CREATE INDEX idx_investments_user ON investments(user_id);
CREATE INDEX idx_investments_status ON investments(investment_status);
CREATE INDEX idx_investments_deadline ON investments(redemption_deadline);
CREATE INDEX idx_alerts_user_date ON alerts(user_id, alert_date);
CREATE INDEX idx_documents_investment ON documents(investment_id);