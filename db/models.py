"""
SQLAlchemy Database Models for User Management Flask Server

This module defines the database models using SQLAlchemy ORM.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


# Create the declarative base
Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model with common fields and functionality.
    
    Provides automatic timestamp management and common methods.
    """
    __abstract__ = True
    
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now(), server_default=func.now())
    
    def to_dict(self):
        """
        Convert model instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        from datetime import timezone
        self.updated_at = datetime.now(timezone.utc)
    
    def __repr__(self):
        """String representation of the model."""
        class_name = self.__class__.__name__
        return f"<{class_name}({self.to_dict()})>"


class User(BaseModel):
    """
    User model representing users in the system.
    
    Stores user information including Israeli ID, name, phone, and address.
    """
    __tablename__ = 'users'
    
    # Primary key - Israeli ID (9 digits)
    id = Column(String(9), primary_key=True, nullable=False)
    
    # User information
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(200), nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_users_created_at', 'created_at'),
        Index('idx_users_name', 'name'),
    )
    
    def __init__(self, id, name, phone, address):
        """
        Initialize a new User instance.
        
        Args:
            id (str): Israeli ID (9 digits)
            name (str): User's full name
            phone (str): Phone number in E.164 format
            address (str): User's address
        """
        self.id = id
        self.name = name
        self.phone = phone
        self.address = address
    
    def to_dict(self):
        """
        Convert User instance to dictionary with ISO formatted timestamps.
        
        Returns:
            dict: Dictionary representation of the user
        """
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_info(self, name=None, phone=None, address=None):
        """
        Update user information.
        
        Args:
            name (str, optional): New name
            phone (str, optional): New phone number
            address (str, optional): New address
        """
        if name is not None:
            self.name = name
        if phone is not None:
            self.phone = phone
        if address is not None:
            self.address = address
        self.update_timestamp()
    
    def __str__(self):
        """Human-readable string representation."""
        return f"User(id={self.id}, name='{self.name}', phone='{self.phone}')"
    
    def __repr__(self):
        """Developer-friendly string representation."""
        return (f"<User(id='{self.id}', name='{self.name}', "
                f"phone='{self.phone}', address='{self.address}', "
                f"created_at='{self.created_at}', updated_at='{self.updated_at}')>")


# Export the models and base for easy importing
__all__ = ['Base', 'BaseModel', 'User']