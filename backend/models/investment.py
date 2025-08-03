from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timedelta

class Investment(Base):
    __tablename__ = "investments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tax_sale_id = Column(Integer, ForeignKey("tax_sales.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    purchase_date = Column(Date, nullable=False)
    purchase_amount = Column(Numeric(12, 2), nullable=False)
    deed_recording_fee = Column(Numeric(8, 2), default=0)
    other_costs = Column(Numeric(10, 2), default=0)
    total_investment = Column(Numeric(12, 2), nullable=False)
    deed_type = Column(String(50))  # 'constable', 'sheriff', 'quitclaim'
    deed_recorded_date = Column(Date)
    deed_volume = Column(String(20))
    deed_page = Column(String(20))
    redemption_period_months = Column(Integer, nullable=False)  # 6 or 24
    redemption_deadline = Column(Date, nullable=False)
    investment_status = Column(String(50), default='active')  # 'active', 'redeemed', 'clear_title', 'sold'
    expected_return_pct = Column(Numeric(5, 2))  # 25 or 50
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="investments")
    tax_sale = relationship("TaxSale", back_populates="investments")
    property_ref = relationship("Property", back_populates="investments")
    redemption = relationship("Redemption", back_populates="investment", uselist=False)
    documents = relationship("Document", back_populates="investment")
    alerts = relationship("Alert", back_populates="investment")
    
    @property
    def days_until_redemption(self):
        """Calculate days until redemption deadline"""
        if self.redemption_deadline:
            delta = self.redemption_deadline - datetime.now().date()
            return delta.days
        return None
    
    @property
    def is_redemption_expired(self):
        """Check if redemption period has expired"""
        if self.redemption_deadline:
            return datetime.now().date() > self.redemption_deadline
        return False
    
    @property
    def potential_return_amount(self):
        """Calculate potential return if redeemed today"""
        penalty_rate = self.expected_return_pct or 25
        return float(self.purchase_amount) * (penalty_rate / 100)
    
    @property
    def total_potential_return(self):
        """Total amount if redeemed (investment + penalty)"""
        return float(self.purchase_amount) + self.potential_return_amount
    
    @property
    def annualized_return_rate(self):
        """Calculate annualized return rate based on redemption period"""
        if self.redemption_period_months and self.expected_return_pct:
            monthly_rate = float(self.expected_return_pct) / self.redemption_period_months
            return monthly_rate * 12
        return None
    
    def calculate_redemption_amount(self, redemption_date=None):
        """Calculate redemption amount for a specific date"""
        if not redemption_date:
            redemption_date = datetime.now().date()
        
        # Calculate days held
        days_held = (redemption_date - self.purchase_date).days
        
        # Determine penalty rate based on timing
        if self.redemption_period_months == 24:  # 2-year redemption
            if days_held <= 365:
                penalty_rate = 25  # 25% first year
            else:
                penalty_rate = 50  # 50% second year
        else:
            penalty_rate = 25  # 25% for 6-month redemption
        
        penalty_amount = float(self.purchase_amount) * (penalty_rate / 100)
        total_redemption = float(self.purchase_amount) + penalty_amount
        
        return {
            'redemption_amount': total_redemption,
            'penalty_amount': penalty_amount,
            'penalty_rate': penalty_rate,
            'days_held': days_held
        }
    
    def __repr__(self):
        return f"<Investment(property_id={self.property_id}, amount=${self.purchase_amount}, status='{self.investment_status}')>"