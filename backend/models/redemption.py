from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Redemption(Base):
    __tablename__ = "redemptions"
    
    id = Column(Integer, primary_key=True, index=True)
    investment_id = Column(Integer, ForeignKey("investments.id"), nullable=False)
    redemption_date = Column(Date, nullable=False)
    redemption_amount = Column(Numeric(12, 2), nullable=False)
    penalty_amount = Column(Numeric(12, 2), nullable=False)
    penalty_percentage = Column(Numeric(5, 2), nullable=False)
    days_held = Column(Integer, nullable=False)
    annualized_return = Column(Numeric(8, 4), nullable=False)
    redeemer_info = Column(String(255))
    payment_method = Column(String(50))
    county_processing_fee = Column(Numeric(8, 2), default=0)
    net_profit = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    investment = relationship("Investment", back_populates="redemption")
    
    @property
    def return_on_investment(self):
        """Calculate ROI percentage"""
        if self.investment and self.investment.total_investment:
            roi = (float(self.net_profit) / float(self.investment.total_investment)) * 100
            return round(roi, 2)
        return 0
    
    @property
    def effective_annual_rate(self):
        """Calculate effective annual rate based on actual holding period"""
        if self.days_held > 0:
            daily_return = float(self.penalty_percentage) / 100 / self.days_held
            annual_return = daily_return * 365 * 100
            return round(annual_return, 2)
        return 0
    
    def __repr__(self):
        return f"<Redemption(investment_id={self.investment_id}, amount=${self.redemption_amount}, return={self.penalty_percentage}%)>"