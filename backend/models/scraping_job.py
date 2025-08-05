from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from database import Base

class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, index=True)
    county = Column(String(50))
    status = Column(String(20), default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    properties_found = Column(Integer, default=0)
    sales_found = Column(Integer, default=0)
    errors = Column(Text)
    progress = Column(Integer, default=0)  # 0-100
    details = Column(JSON)
    created_by = Column(String(255))
    
    def __repr__(self):
        return f"<ScrapingJob(id={self.id}, county='{self.county}', status='{self.status}')>"