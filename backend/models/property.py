from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
    parcel_number = Column(String(50), unique=True, nullable=False, index=True)
    owner_name = Column(String(255), nullable=False)
    property_address = Column(String(255), nullable=False, index=True)
    city = Column(String(100))
    state = Column(String(2), default='TX')
    zip_code = Column(String(10))
    legal_description = Column(Text)
    appraisal_district_id = Column(String(50))
    property_type = Column(String(50))  # 'residential', 'commercial', 'land', 'agricultural'
    assessed_value = Column(Numeric(12, 2))
    market_value = Column(Numeric(12, 2))
    lot_size = Column(Numeric(10, 2))
    square_footage = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Numeric(3, 1))
    year_built = Column(Integer)
    homestead_exemption = Column(Boolean, default=False)
    senior_exemption = Column(Boolean, default=False)
    agricultural_exemption = Column(Boolean, default=False)
    mineral_rights = Column(Boolean, default=False)
    latitude = Column(Numeric(10, 6))
    longitude = Column(Numeric(11, 6))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    county = relationship("County", back_populates="properties")
    tax_sales = relationship("TaxSale", back_populates="property_ref")
    investments = relationship("Investment", back_populates="property_ref")
    documents = relationship("Document", back_populates="property_ref")
    research_notes = relationship("ResearchNote", back_populates="property_ref")
    valuations = relationship("PropertyValuation", back_populates="property_ref")
    
    @property
    def redemption_period_months(self):
        """Calculate redemption period based on property characteristics"""
        if self.homestead_exemption or self.agricultural_exemption or self.mineral_rights:
            return 24  # 2 years
        return 6  # 6 months (180 days)
    
    @property
    def expected_penalty_rate(self):
        """Expected penalty rate for redemption"""
        if self.redemption_period_months == 24:
            return 25  # 25% first year, could be 50% second year
        return 25  # 25% for 6-month redemption
    
    def __repr__(self):
        return f"<Property(address='{self.property_address}', type='{self.property_type}')>"