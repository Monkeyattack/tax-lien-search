"""Add saved searches and search results tables

This migration adds tables to support saved property searches and alerts.
"""

from sqlalchemy import text

def upgrade(connection):
    """Add saved searches tables"""
    
    # Create saved_searches table
    connection.execute(text("""
        CREATE TABLE saved_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            filters TEXT NOT NULL DEFAULT '{}',
            email_alerts BOOLEAN DEFAULT 1,
            alert_frequency VARCHAR(50) DEFAULT 'daily',
            last_alert_sent TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            match_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """))
    
    # Create index on user_id for saved_searches
    connection.execute(text("""
        CREATE INDEX idx_saved_searches_user_id ON saved_searches(user_id)
    """))
    
    # Create search_results table
    connection.execute(text("""
        CREATE TABLE search_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            saved_search_id INTEGER NOT NULL,
            property_id INTEGER NOT NULL,
            matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            alert_sent BOOLEAN DEFAULT 0,
            alert_sent_at TIMESTAMP,
            FOREIGN KEY (saved_search_id) REFERENCES saved_searches(id),
            FOREIGN KEY (property_id) REFERENCES properties(id)
        )
    """))
    
    # Create indexes for search_results
    connection.execute(text("""
        CREATE INDEX idx_search_results_saved_search_id ON search_results(saved_search_id)
    """))
    
    connection.execute(text("""
        CREATE INDEX idx_search_results_property_id ON search_results(property_id)
    """))
    
    # Create unique constraint to prevent duplicate results
    connection.execute(text("""
        CREATE UNIQUE INDEX idx_search_results_unique ON search_results(saved_search_id, property_id)
    """))

def downgrade(connection):
    """Remove saved searches tables"""
    connection.execute(text("DROP TABLE IF EXISTS search_results"))
    connection.execute(text("DROP TABLE IF EXISTS saved_searches"))