from sqlalchemy import Column, Integer, String, Date, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class PropertyValuation(Base):
    __tablename__ = "property_valuations"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    valuation_date = Column(Date, nullable=False)
    estimated_value = Column(Numeric(12, 2), nullable=False)
    valuation_source = Column(String(100))  # 'county_assessor', 'zillow', 'manual', 'appraisal'
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    property_ref = relationship("Property", back_populates="valuations")
    
    @property
    def value_per_sqft(self):
        """Calculate value per square foot if available"""
        if self.property and self.property.square_feet and self.property.square_feet > 0:
            return float(self.estimated_value) / self.property.square_feet
        return None
    
    def __repr__(self):
        return f"<PropertyValuation(property_id={self.property_id}, value=${self.estimated_value}, source='{self.valuation_source}')>"