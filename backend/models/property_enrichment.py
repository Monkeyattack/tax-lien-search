from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class PropertyEnrichment(Base):
    __tablename__ = "property_enrichments"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, unique=True)
    
    # Zillow/Realty Data
    zillow_estimated_value = Column(Numeric(12, 2))
    zillow_rent_estimate = Column(Numeric(10, 2))
    zillow_last_sold_date = Column(DateTime)
    zillow_last_sold_price = Column(Numeric(12, 2))
    zillow_price_history = Column(JSON)  # List of price history entries
    zillow_tax_history = Column(JSON)    # List of tax history entries
    zillow_url = Column(String(500))
    zestimate = Column(Numeric(12, 2))
    
    # Google Maps Data
    formatted_address = Column(String(500))
    place_id = Column(String(100))
    neighborhood_data = Column(JSON)  # Schools, amenities, demographics
    
    # County Additional Data
    owner_history = Column(JSON)      # Historical ownership records
    permit_history = Column(JSON)     # Building permits
    lien_history = Column(JSON)       # All liens on property
    
    # Investment Metrics
    estimated_rehab_cost = Column(Numeric(10, 2))
    estimated_arv = Column(Numeric(12, 2))  # After Repair Value
    monthly_rent_estimate = Column(Numeric(10, 2))
    gross_rent_multiplier = Column(Numeric(6, 2))
    cap_rate = Column(Numeric(5, 2))
    cash_on_cash_return = Column(Numeric(5, 2))
    roi_percentage = Column(Numeric(6, 2))
    investment_score = Column(Numeric(5, 1))  # 0-100 score
    
    # External IDs
    lgbs_id = Column(String(50))
    dallas_cad_account = Column(String(50))
    redfin_id = Column(String(50))
    realtor_id = Column(String(50))
    
    # Data Quality
    data_sources = Column(JSON)  # List of sources used
    data_quality_score = Column(Numeric(5, 1))  # 0-100 score
    last_enriched_at = Column(DateTime(timezone=True))
    enrichment_errors = Column(JSON)
    
    # Market Analysis
    comparable_sales = Column(JSON)  # Recent comparable sales
    market_trend = Column(String(20))  # 'appreciating', 'stable', 'declining'
    days_on_market_average = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    property_ref = relationship("Property", back_populates="enrichment", uselist=False)
    
    def __repr__(self):
        return f"<PropertyEnrichment(property_id={self.property_id}, score={self.investment_score})>"