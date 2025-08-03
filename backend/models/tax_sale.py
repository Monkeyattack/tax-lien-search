from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class TaxSale(Base):
    __tablename__ = "tax_sales"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
    sale_date = Column(Date, nullable=False, index=True)
    minimum_bid = Column(Numeric(12, 2), nullable=False)
    taxes_owed = Column(Numeric(12, 2), nullable=False)
    interest_penalties = Column(Numeric(12, 2), default=0)
    court_costs = Column(Numeric(12, 2), default=0)
    attorney_fees = Column(Numeric(12, 2), default=0)
    total_judgment = Column(Numeric(12, 2), nullable=False)
    sale_status = Column(String(50), default='scheduled', index=True)  # 'scheduled', 'sold', 'struck_off', 'cancelled'
    winning_bid = Column(Numeric(12, 2))
    winner_info = Column(String(255))
    constable_precinct = Column(String(10))
    case_number = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    property_ref = relationship("Property", back_populates="tax_sales")
    county = relationship("County", back_populates="tax_sales")
    investments = relationship("Investment", back_populates="tax_sale")
    
    @property
    def is_upcoming(self):
        """Check if sale is upcoming"""
        from datetime import datetime
        return self.sale_date >= datetime.now().date() and self.sale_status == 'scheduled'
    
    @property
    def excess_proceeds(self):
        """Calculate excess proceeds if winning bid > total judgment"""
        if self.winning_bid and self.total_judgment:
            excess = float(self.winning_bid) - float(self.total_judgment)
            return excess if excess > 0 else 0
        return 0
    
    @property
    def bid_premium_percentage(self):
        """Calculate premium percentage over minimum bid"""
        if self.winning_bid and self.minimum_bid:
            premium = (float(self.winning_bid) - float(self.minimum_bid)) / float(self.minimum_bid)
            return premium * 100
        return 0
    
    def __repr__(self):
        return f"<TaxSale(property_id={self.property_id}, sale_date='{self.sale_date}', status='{self.sale_status}')>"