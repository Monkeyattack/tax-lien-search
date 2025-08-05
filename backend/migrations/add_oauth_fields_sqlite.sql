-- SQLite-compatible migration for OAuth fields

-- First, check and add new columns if they don't exist
-- SQLite doesn't support IF NOT EXISTS with ALTER TABLE, so we use a different approach

-- Create a new table with the updated schema
CREATE TABLE IF NOT EXISTS users_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- Now nullable for OAuth users
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    auth_provider VARCHAR(50) DEFAULT 'local',
    google_id VARCHAR(255) UNIQUE,
    profile_picture VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Copy existing data to the new table
INSERT INTO users_new (id, username, email, password_hash, first_name, last_name, is_active, created_at, updated_at)
SELECT id, username, email, password_hash, first_name, last_name, is_active, created_at, updated_at
FROM users;

-- Drop the old table and rename the new one
DROP TABLE users;
ALTER TABLE users_new RENAME TO users;

-- Set admin status for your email
UPDATE users 
SET is_admin = TRUE 
WHERE email = 'meredith@monkeyattack.com';

-- Create admin user if doesn't exist
INSERT OR IGNORE INTO users (username, email, password_hash, first_name, last_name, is_active, is_admin, auth_provider)
VALUES ('meredith', 'meredith@monkeyattack.com', '', 'C.', 'Meredith', TRUE, TRUE, 'google');