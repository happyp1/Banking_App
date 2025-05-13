from sqlalchemy import Column, Integer, String
from app.db.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="customer")
    hashed_password = Column(String)

    accounts = relationship("Account", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
