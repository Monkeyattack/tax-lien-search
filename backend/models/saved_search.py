from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class SavedSearch(Base):
    __tablename__ = "saved_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Search filters stored as JSON
    filters = Column(JSON, nullable=False, default={})
    # Includes: counties, property_types, min_value, max_value, min_investment_score,
    # bedrooms_min, bathrooms_min, year_built_after, lot_size_min, has_zestimate, etc.
    
    # Alert preferences
    email_alerts = Column(Boolean, default=True)
    alert_frequency = Column(String(50), default="daily")  # 'instant', 'daily', 'weekly'
    last_alert_sent = Column(DateTime(timezone=True))
    
    # Tracking
    is_active = Column(Boolean, default=True)
    match_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="saved_searches")
    search_results = relationship("SearchResult", back_populates="saved_search", cascade="all, delete-orphan")
    
    def matches_property(self, property_data):
        """Check if a property matches this saved search filters"""
        filters = self.filters or {}
        
        # County filter
        if 'counties' in filters and filters['counties']:
            if property_data.get('county_id') not in filters['counties']:
                return False
        
        # Property type filter
        if 'property_types' in filters and filters['property_types']:
            if property_data.get('property_type') not in filters['property_types']:
                return False
        
        # Value filters
        if 'min_value' in filters and filters['min_value']:
            value = property_data.get('assessed_value') or property_data.get('market_value') or 0
            if value < filters['min_value']:
                return False
        
        if 'max_value' in filters and filters['max_value']:
            value = property_data.get('assessed_value') or property_data.get('market_value') or float('inf')
            if value > filters['max_value']:
                return False
        
        # Investment score filter
        if 'min_investment_score' in filters and filters['min_investment_score']:
            score = property_data.get('investment_score', 0)
            if score < filters['min_investment_score']:
                return False
        
        # Property characteristics
        if 'bedrooms_min' in filters and filters['bedrooms_min']:
            if (property_data.get('bedrooms') or 0) < filters['bedrooms_min']:
                return False
        
        if 'bathrooms_min' in filters and filters['bathrooms_min']:
            if (property_data.get('bathrooms') or 0) < filters['bathrooms_min']:
                return False
        
        if 'year_built_after' in filters and filters['year_built_after']:
            if (property_data.get('year_built') or 0) < filters['year_built_after']:
                return False
        
        if 'lot_size_min' in filters and filters['lot_size_min']:
            if (property_data.get('lot_size') or 0) < filters['lot_size_min']:
                return False
        
        # Boolean filters
        if filters.get('has_zestimate') and not property_data.get('zestimate'):
            return False
        
        if filters.get('homestead_only') and not property_data.get('homestead_exemption'):
            return False
        
        if filters.get('no_homestead') and property_data.get('homestead_exemption'):
            return False
        
        # ROI and investment filters
        if 'min_roi' in filters and filters['min_roi']:
            roi = property_data.get('roi_percentage', 0)
            if roi < filters['min_roi']:
                return False
        
        if 'min_cap_rate' in filters and filters['min_cap_rate']:
            cap_rate = property_data.get('cap_rate', 0)
            if cap_rate < filters['min_cap_rate']:
                return False
        
        # Location filter (city/zip)
        if 'cities' in filters and filters['cities']:
            if property_data.get('city') not in filters['cities']:
                return False
        
        if 'zip_codes' in filters and filters['zip_codes']:
            if property_data.get('zip_code') not in filters['zip_codes']:
                return False
        
        return True
    
    def __repr__(self):
        return f"<SavedSearch(name='{self.name}', user_id={self.user_id}, active={self.is_active})>"


class SearchResult(Base):
    __tablename__ = "search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    saved_search_id = Column(Integer, ForeignKey("saved_searches.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    
    # Track when this match was found
    matched_at = Column(DateTime(timezone=True), server_default=func.now())
    alert_sent = Column(Boolean, default=False)
    alert_sent_at = Column(DateTime(timezone=True))
    
    # Relationships
    saved_search = relationship("SavedSearch", back_populates="search_results")
    property = relationship("Property")
    
    def __repr__(self):
        return f"<SearchResult(search_id={self.saved_search_id}, property_id={self.property_id})>"