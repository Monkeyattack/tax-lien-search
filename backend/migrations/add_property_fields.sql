-- Add missing property fields
ALTER TABLE properties ADD COLUMN parcel_number VARCHAR(50);
ALTER TABLE properties ADD COLUMN owner_name VARCHAR(255);
ALTER TABLE properties ADD COLUMN city VARCHAR(100);
ALTER TABLE properties ADD COLUMN state VARCHAR(2) DEFAULT 'TX';
ALTER TABLE properties ADD COLUMN zip_code VARCHAR(10);
ALTER TABLE properties ADD COLUMN square_footage INTEGER;
ALTER TABLE properties ADD COLUMN bedrooms INTEGER;
ALTER TABLE properties ADD COLUMN bathrooms DECIMAL(3,1);
ALTER TABLE properties ADD COLUMN senior_exemption BOOLEAN DEFAULT FALSE;
-- latitude and longitude columns already exist

-- Create unique index on parcel_number
CREATE UNIQUE INDEX idx_properties_parcel_number ON properties(parcel_number);