from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    investment_id = Column(Integer, ForeignKey("investments.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))
    document_type = Column(String(50), nullable=False)  # 'deed', 'receipt', 'judgment', 'appraisal', 'photo'
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    investment = relationship("Investment", back_populates="documents")
    property_ref = relationship("Property", back_populates="documents")
    
    @property
    def file_size_mb(self):
        """Convert file size to MB"""
        if self.file_size_bytes:
            return round(self.file_size_bytes / (1024 * 1024), 2)
        return 0
    
    @property
    def is_image(self):
        """Check if document is an image"""
        if self.mime_type:
            return self.mime_type.startswith('image/')
        return False
    
    @property
    def is_pdf(self):
        """Check if document is a PDF"""
        return self.mime_type == 'application/pdf'
    
    def __repr__(self):
        return f"<Document(name='{self.document_name}', type='{self.document_type}')>"