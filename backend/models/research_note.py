from sqlalchemy import Column, Integer, String, Date, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class ResearchNote(Base):
    __tablename__ = "research_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    note_date = Column(Date, default=func.current_date())
    note_type = Column(String(50))  # 'title_search', 'market_analysis', 'inspection', 'legal'
    content = Column(Text, nullable=False)
    is_important = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="research_notes")
    property_ref = relationship("Property", back_populates="research_notes")
    
    def __repr__(self):
        return f"<ResearchNote(property_id={self.property_id}, type='{self.note_type}', important={self.is_important})>"