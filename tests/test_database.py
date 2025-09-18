"""
Integration tests for database functionality.
"""

import unittest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import DatabaseManager, UserRepository, DatabaseError
from db.models import Base, User
from config.manager import ConfigManager


class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager."""
    
    def setUp(self):
        """Set up test fixtures with temporary database."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create test configuration
        self.test_config = ConfigManager(verbose=False)
        self.test_config.config = {
            'database': {
                'type': 'sqlite',
                'filename': self.temp_db.name,
                'echo': False,
                'pool_size': 1,
                'max_overflow': 0,
                'connect_args': {'check_same_thread': False}
            }
        }
        
        self.db_manager = DatabaseManager(self.test_config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.db_manager:
            self.db_manager.close()
        
        # Remove temporary database file
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database initialization."""
        success = self.db_manager.initialize()
        self.assertTrue(success)
        self.assertTrue(self.db_manager.is_initialized())
    
    def test_database_connection(self):
        """Test database connection."""
        self.db_manager.initialize()
        
        # Test getting a session
        session = self.db_manager.get_session()
        self.assertIsNotNone(session)
        session.close()
    
    def test_session_scope_context_manager(self):
        """Test session scope context manager."""
        self.db_manager.initialize()
        
        with self.db_manager.session_scope() as session:
            # Test that we can query the database
            count = session.query(User).count()
            self.assertEqual(count, 0)
    
    def test_health_check(self):
        """Test database health check."""
        self.db_manager.initialize()
        
        health = self.db_manager.health_check()
        self.assertEqual(health['status'], 'healthy')
        self.assertIn('user_count', health)
    
    def test_health_check_uninitialized(self):
        """Test health check on uninitialized database."""
        health = self.db_manager.health_check()
        self.assertEqual(health['status'], 'unhealthy')
        self.assertIn('error', health)


class TestUserRepository(unittest.TestCase):
    """Test cases for UserRepository."""
    
    def setUp(self):
        """Set up test fixtures with temporary database."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create test configuration
        self.test_config = ConfigManager(verbose=False)
        self.test_config.config = {
            'database': {
                'type': 'sqlite',
                'filename': self.temp_db.name,
                'echo': False,
                'pool_size': 1,
                'max_overflow': 0,
                'connect_args': {'check_same_thread': False}
            }
        }
        
        self.db_manager = DatabaseManager(self.test_config)
        self.db_manager.initialize()
        self.user_repo = UserRepository(self.db_manager)
        
        # Test user data
        self.test_user_data = {
            'id': '123456782',
            'name': 'John Doe',
            'phone': '+972501234567',
            'address': '123 Main St, Tel Aviv'
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.db_manager:
            self.db_manager.close()
        
        # Remove temporary database file
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_create_user(self):
        """Test creating a user."""
        user = self.user_repo.create_user(self.test_user_data)
        
        self.assertEqual(user.id, '123456782')
        self.assertEqual(user.name, 'John Doe')
        self.assertEqual(user.phone, '+972501234567')
        self.assertEqual(user.address, '123 Main St, Tel Aviv')
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
    
    def test_create_duplicate_user(self):
        """Test creating a user with duplicate ID."""
        # Create first user
        self.user_repo.create_user(self.test_user_data)
        
        # Try to create duplicate
        with self.assertRaises(Exception):  # Should raise IntegrityError
            self.user_repo.create_user(self.test_user_data)
    
    def test_get_user_by_id(self):
        """Test retrieving a user by ID."""
        # Create user first
        created_user = self.user_repo.create_user(self.test_user_data)
        
        # Retrieve user
        retrieved_user = self.user_repo.get_user_by_id('123456782')
        
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.id, created_user.id)
        self.assertEqual(retrieved_user.name, created_user.name)
    
    def test_get_nonexistent_user(self):
        """Test retrieving a non-existent user."""
        user = self.user_repo.get_user_by_id('999999999')
        self.assertIsNone(user)
    
    def test_get_all_users(self):
        """Test retrieving all users."""
        # Create multiple users
        user_data_1 = self.test_user_data.copy()
        user_data_2 = {
            'id': '987654321',
            'name': 'Jane Smith',
            'phone': '+972507654321',
            'address': '456 Oak Ave, Jerusalem'
        }
        
        self.user_repo.create_user(user_data_1)
        self.user_repo.create_user(user_data_2)
        
        # Get all users
        users = self.user_repo.get_all_users()
        
        self.assertEqual(len(users), 2)
        user_ids = [user.id for user in users]
        self.assertIn('123456782', user_ids)
        self.assertIn('987654321', user_ids)
    
    def test_get_all_user_ids(self):
        """Test retrieving all user IDs."""
        # Create multiple users
        user_data_1 = self.test_user_data.copy()
        user_data_2 = {
            'id': '987654321',
            'name': 'Jane Smith',
            'phone': '+972507654321',
            'address': '456 Oak Ave, Jerusalem'
        }
        
        self.user_repo.create_user(user_data_1)
        self.user_repo.create_user(user_data_2)
        
        # Get all user IDs
        user_ids = self.user_repo.get_all_user_ids()
        
        self.assertEqual(len(user_ids), 2)
        self.assertIn('123456782', user_ids)
        self.assertIn('987654321', user_ids)
    
    def test_update_user(self):
        """Test updating a user."""
        # Create user first
        self.user_repo.create_user(self.test_user_data)
        
        # Update user
        update_data = {
            'name': 'Jane Doe',
            'phone': '+972507654321'
        }
        
        updated_user = self.user_repo.update_user('123456782', update_data)
        
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.name, 'Jane Doe')
        self.assertEqual(updated_user.phone, '+972507654321')
        self.assertEqual(updated_user.address, '123 Main St, Tel Aviv')  # Unchanged
    
    def test_update_nonexistent_user(self):
        """Test updating a non-existent user."""
        update_data = {'name': 'New Name'}
        updated_user = self.user_repo.update_user('999999999', update_data)
        self.assertIsNone(updated_user)
    
    def test_delete_user(self):
        """Test deleting a user."""
        # Create user first
        self.user_repo.create_user(self.test_user_data)
        
        # Delete user
        success = self.user_repo.delete_user('123456782')
        self.assertTrue(success)
        
        # Verify user is deleted
        user = self.user_repo.get_user_by_id('123456782')
        self.assertIsNone(user)
    
    def test_delete_nonexistent_user(self):
        """Test deleting a non-existent user."""
        success = self.user_repo.delete_user('999999999')
        self.assertFalse(success)
    
    def test_user_exists(self):
        """Test checking if user exists."""
        # User doesn't exist initially
        self.assertFalse(self.user_repo.user_exists('123456782'))
        
        # Create user
        self.user_repo.create_user(self.test_user_data)
        
        # User should exist now
        self.assertTrue(self.user_repo.user_exists('123456782'))
    
    def test_get_user_count(self):
        """Test getting user count."""
        # Initially no users
        self.assertEqual(self.user_repo.get_user_count(), 0)
        
        # Create users
        self.user_repo.create_user(self.test_user_data)
        self.assertEqual(self.user_repo.get_user_count(), 1)
        
        user_data_2 = {
            'id': '987654321',
            'name': 'Jane Smith',
            'phone': '+972507654321',
            'address': '456 Oak Ave, Jerusalem'
        }
        self.user_repo.create_user(user_data_2)
        self.assertEqual(self.user_repo.get_user_count(), 2)


if __name__ == '__main__':
    unittest.main()