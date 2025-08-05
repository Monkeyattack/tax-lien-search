from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    auth_provider = Column(String(50), default='local')  # 'local' or 'google'
    google_id = Column(String(255), unique=True, nullable=True)
    profile_picture = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    investments = relationship("Investment", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    documents = relationship("Document", back_populates="user")
    research_notes = relationship("ResearchNote", back_populates="user")
    saved_searches = relationship("SavedSearch", back_populates="user")
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username