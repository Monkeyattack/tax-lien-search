-- Add OAuth fields to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(50) DEFAULT 'local',
ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) UNIQUE,
ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500);

-- Allow null password for OAuth users
ALTER TABLE users 
ALTER COLUMN password_hash DROP NOT NULL;

-- Set admin status for your email
UPDATE users 
SET is_admin = TRUE 
WHERE email = 'meredith@monkeyattack.com';

-- Create admin user if doesn't exist
INSERT INTO users (username, email, password_hash, first_name, last_name, is_active, is_admin, auth_provider)
SELECT 'meredith', 'meredith@monkeyattack.com', '', 'C.', 'Meredith', TRUE, TRUE, 'google'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'meredith@monkeyattack.com'
);