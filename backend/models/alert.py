from sqlalchemy import Column, Integer, String, Date, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    investment_id = Column(Integer, ForeignKey("investments.id"))
    alert_type = Column(String(50), nullable=False)  # 'redemption_deadline', 'auction_reminder', 'payment_due'
    alert_date = Column(Date, nullable=False, index=True)
    message = Column(Text, nullable=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    investment = relationship("Investment", back_populates="alerts")
    
    @property
    def is_overdue(self):
        """Check if alert date has passed"""
        from datetime import datetime
        return self.alert_date < datetime.now().date()
    
    @property
    def days_until_alert(self):
        """Calculate days until alert date"""
        from datetime import datetime
        delta = self.alert_date - datetime.now().date()
        return delta.days
    
    def __repr__(self):
        return f"<Alert(type='{self.alert_type}', date='{self.alert_date}', sent={self.is_sent})>"