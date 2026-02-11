from sqlalchemy import Column, Integer, String, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255))
    permissions = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    users = relationship("User", back_populates="role")
