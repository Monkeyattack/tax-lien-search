from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class County(Base):
    __tablename__ = "counties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    state = Column(String(2), default='TX')
    auction_schedule = Column(String(255))  # "First Tuesday of each month"
    auction_location = Column(String(255))
    auction_type = Column(String(50))  # 'in_person', 'online', 'hybrid'
    website_url = Column(String(255))
    contact_info = Column(Text)
    special_procedures = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    properties = relationship("Property", back_populates="county")
    tax_sales = relationship("TaxSale", back_populates="county")
    
    def __repr__(self):
        return f"<County(name='{self.name}', state='{self.state}')>"