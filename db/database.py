"""
Database Management for User Management Flask Server

This module handles database connections, session management, and data access operations.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db.models import Base, User
from config.manager import get_config


# Set up logging
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass


class DatabaseManager:
    """
    Database connection and session management class.
    
    Handles database initialization, connection pooling, and session lifecycle.
    """
    
    def __init__(self, config_manager=None):
        """
        Initialize the database manager.
        
        Args:
            config_manager: Configuration manager instance (optional)
        """
        self.config = config_manager or get_config()
        self.engine: Optional[Engine] = None
        self.session_factory = None
        self.scoped_session_factory = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the database connection and create tables.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Get database configuration
            db_url = self.config.get_database_url()
            engine_config = self.config.get_database_engine_config()
            
            logger.info(f"Initializing database connection to: {db_url}")
            
            # Create engine
            self.engine = create_engine(db_url, **engine_config)
            
            # Test connection
            with self.engine.connect() as conn:
                logger.info("Database connection test successful")
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            self.scoped_session_factory = scoped_session(self.session_factory)
            
            # Create tables
            self._create_tables()
            
            self._initialized = True
            logger.info("Database initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self._initialized = False
            return False
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise DatabaseError(f"Table creation failed: {e}")
    
    def is_initialized(self) -> bool:
        """Check if database is initialized."""
        return self._initialized and self.engine is not None
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            Session: SQLAlchemy session instance
            
        Raises:
            DatabaseError: If database is not initialized
        """
        if not self.is_initialized():
            raise DatabaseError("Database not initialized. Call initialize() first.")
        
        return self.session_factory()
    
    def get_scoped_session(self):
        """
        Get a scoped session (thread-local).
        
        Returns:
            Scoped session instance
            
        Raises:
            DatabaseError: If database is not initialized
        """
        if not self.is_initialized():
            raise DatabaseError("Database not initialized. Call initialize() first.")
        
        return self.scoped_session_factory()
    
    @contextmanager
    def session_scope(self):
        """
        Context manager for database sessions with automatic commit/rollback.
        
        Usage:
            with db_manager.session_scope() as session:
                # perform database operations
                session.add(user)
                # automatic commit on success, rollback on exception
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def close(self):
        """Close database connections and clean up resources."""
        if self.scoped_session_factory:
            self.scoped_session_factory.remove()
        
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")
        
        self._initialized = False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check.
        
        Returns:
            dict: Health check results
        """
        if not self.is_initialized():
            return {
                'status': 'unhealthy',
                'error': 'Database not initialized'
            }
        
        try:
            with self.session_scope() as session:
                # Simple query to test connection
                user_count = session.query(User).count()
                
            return {
                'status': 'healthy',
                'user_count': user_count,
                'database_url': self.config.get_database_url()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


class UserRepository:
    """
    Data access layer for User operations.
    
    Provides CRUD operations and query methods for User entities.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the user repository.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        Create a new user.
        
        Args:
            user_data (dict): User data dictionary
            
        Returns:
            User: Created user instance
            
        Raises:
            DatabaseError: If user creation fails
            IntegrityError: If user with same ID already exists
        """
        try:
            with self.db_manager.session_scope() as session:
                user = User(
                    id=user_data['id'],
                    name=user_data['name'],
                    phone=user_data['phone'],
                    address=user_data['address']
                )
                session.add(user)
                session.flush()  # Flush to get any database-generated values
                
                # Refresh to get the complete object with timestamps
                session.refresh(user)
                
                # Detach from session to avoid lazy loading issues
                session.expunge(user)
                return user
                
        except IntegrityError as e:
            logger.error(f"User creation failed - duplicate ID: {user_data.get('id')}")
            raise IntegrityError("User with this ID already exists", None, None)
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            raise DatabaseError(f"Failed to create user: {e}")
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id (str): User ID to search for
            
        Returns:
            User or None: User instance if found, None otherwise
        """
        try:
            with self.db_manager.session_scope() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    # Detach from session to avoid lazy loading issues
                    session.expunge(user)
                return user
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            raise DatabaseError(f"Failed to retrieve user: {e}")
    
    def get_all_users(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            List[User]: List of all users
        """
        try:
            with self.db_manager.session_scope() as session:
                users = session.query(User).order_by(User.created_at.desc()).all()
                # Detach from session
                for user in users:
                    session.expunge(user)
                return users
        except Exception as e:
            logger.error(f"Failed to get all users: {e}")
            raise DatabaseError(f"Failed to retrieve users: {e}")
    
    def get_all_user_ids(self) -> List[str]:
        """
        Get all user IDs.
        
        Returns:
            List[str]: List of all user IDs
        """
        try:
            with self.db_manager.session_scope() as session:
                user_ids = session.query(User.id).order_by(User.created_at.desc()).all()
                return [user_id[0] for user_id in user_ids]
        except Exception as e:
            logger.error(f"Failed to get user IDs: {e}")
            raise DatabaseError(f"Failed to retrieve user IDs: {e}")
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Update user information.
        
        Args:
            user_id (str): User ID to update
            user_data (dict): Updated user data
            
        Returns:
            User or None: Updated user instance if found, None otherwise
        """
        try:
            with self.db_manager.session_scope() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.update_info(
                        name=user_data.get('name'),
                        phone=user_data.get('phone'),
                        address=user_data.get('address')
                    )
                    session.flush()
                    session.refresh(user)
                    session.expunge(user)
                return user
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise DatabaseError(f"Failed to update user: {e}")
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id (str): User ID to delete
            
        Returns:
            bool: True if user was deleted, False if not found
        """
        try:
            with self.db_manager.session_scope() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    session.delete(user)
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise DatabaseError(f"Failed to delete user: {e}")
    
    def user_exists(self, user_id: str) -> bool:
        """
        Check if user exists.
        
        Args:
            user_id (str): User ID to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        try:
            with self.db_manager.session_scope() as session:
                exists = session.query(User.id).filter(User.id == user_id).first() is not None
                return exists
        except Exception as e:
            logger.error(f"Failed to check user existence {user_id}: {e}")
            raise DatabaseError(f"Failed to check user existence: {e}")
    
    def get_user_count(self) -> int:
        """
        Get total number of users.
        
        Returns:
            int: Total user count
        """
        try:
            with self.db_manager.session_scope() as session:
                count = session.query(User).count()
                return count
        except Exception as e:
            logger.error(f"Failed to get user count: {e}")
            raise DatabaseError(f"Failed to get user count: {e}")


# Global database manager instance
_db_manager = None
_user_repository = None


def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager: Global database manager
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_user_repository() -> UserRepository:
    """
    Get the global user repository instance.
    
    Returns:
        UserRepository: Global user repository
    """
    global _user_repository
    if _user_repository is None:
        _user_repository = UserRepository(get_database_manager())
    return _user_repository


def initialize_database() -> bool:
    """
    Initialize the global database manager.
    
    Returns:
        bool: True if initialization successful
    """
    db_manager = get_database_manager()
    return db_manager.initialize()


def close_database():
    """Close the global database manager."""
    global _db_manager, _user_repository
    if _db_manager:
        _db_manager.close()
        _db_manager = None
        _user_repository = None


# Export main classes and functions
__all__ = [
    'DatabaseManager', 'UserRepository', 'DatabaseError',
    'get_database_manager', 'get_user_repository', 
    'initialize_database', 'close_database'
]