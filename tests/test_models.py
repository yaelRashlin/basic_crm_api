"""
Unit tests for database models.
"""

import unittest
from datetime import datetime
from db.models import User, BaseModel


class TestBaseModel(unittest.TestCase):
    """Test cases for BaseModel functionality."""
    
    def test_to_dict_method(self):
        """Test the to_dict method of BaseModel."""
        # Create a user instance
        user = User(
            id="123456782",
            name="Test User",
            phone="+972501234567",
            address="Test Address"
        )
        
        # Test to_dict method
        user_dict = user.to_dict()
        
        self.assertIsInstance(user_dict, dict)
        self.assertEqual(user_dict['id'], "123456782")
        self.assertEqual(user_dict['name'], "Test User")
        self.assertEqual(user_dict['phone'], "+972501234567")
        self.assertEqual(user_dict['address'], "Test Address")
    
    def test_update_timestamp(self):
        """Test the update_timestamp method."""
        user = User(
            id="123456782",
            name="Test User",
            phone="+972501234567",
            address="Test Address"
        )
        
        # Set initial timestamp (timezone-aware)
        from datetime import timezone
        initial_time = datetime.now(timezone.utc)
        user.updated_at = initial_time
        
        # Update timestamp
        user.update_timestamp()
        
        # Check that timestamp was updated
        self.assertGreater(user.updated_at, initial_time)


class TestUserModel(unittest.TestCase):
    """Test cases for User model."""
    
    def test_user_creation(self):
        """Test creating a User instance."""
        user = User(
            id="123456782",
            name="John Doe",
            phone="+972501234567",
            address="123 Main St, Tel Aviv"
        )
        
        self.assertEqual(user.id, "123456782")
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.phone, "+972501234567")
        self.assertEqual(user.address, "123 Main St, Tel Aviv")
    
    def test_user_to_dict(self):
        """Test User to_dict method with timestamp formatting."""
        user = User(
            id="123456782",
            name="John Doe",
            phone="+972501234567",
            address="123 Main St, Tel Aviv"
        )
        
        # Set timestamps manually for testing
        test_time = datetime(2024, 1, 1, 12, 0, 0)
        user.created_at = test_time
        user.updated_at = test_time
        
        user_dict = user.to_dict()
        
        expected_dict = {
            'id': "123456782",
            'name': "John Doe",
            'phone': "+972501234567",
            'address': "123 Main St, Tel Aviv",
            'created_at': "2024-01-01T12:00:00",
            'updated_at': "2024-01-01T12:00:00"
        }
        
        self.assertEqual(user_dict, expected_dict)
    
    def test_user_update_info(self):
        """Test updating user information."""
        user = User(
            id="123456782",
            name="John Doe",
            phone="+972501234567",
            address="123 Main St, Tel Aviv"
        )
        
        # Set initial timestamp (timezone-aware)
        from datetime import timezone
        initial_time = datetime.now(timezone.utc)
        user.updated_at = initial_time
        
        # Update user info
        user.update_info(
            name="Jane Doe",
            phone="+972507654321",
            address="456 Oak Ave, Jerusalem"
        )
        
        # Check updated values
        self.assertEqual(user.name, "Jane Doe")
        self.assertEqual(user.phone, "+972507654321")
        self.assertEqual(user.address, "456 Oak Ave, Jerusalem")
        self.assertGreater(user.updated_at, initial_time)
    
    def test_user_partial_update(self):
        """Test partial update of user information."""
        user = User(
            id="123456782",
            name="John Doe",
            phone="+972501234567",
            address="123 Main St, Tel Aviv"
        )
        
        # Update only name
        user.update_info(name="Jane Doe")
        
        # Check that only name was updated
        self.assertEqual(user.name, "Jane Doe")
        self.assertEqual(user.phone, "+972501234567")  # Unchanged
        self.assertEqual(user.address, "123 Main St, Tel Aviv")  # Unchanged
    
    def test_user_string_representations(self):
        """Test string representations of User model."""
        user = User(
            id="123456782",
            name="John Doe",
            phone="+972501234567",
            address="123 Main St, Tel Aviv"
        )
        
        # Test __str__ method
        str_repr = str(user)
        self.assertIn("123456782", str_repr)
        self.assertIn("John Doe", str_repr)
        self.assertIn("+972501234567", str_repr)
        
        # Test __repr__ method
        repr_str = repr(user)
        self.assertIn("User", repr_str)
        self.assertIn("123456782", repr_str)
        self.assertIn("John Doe", repr_str)


if __name__ == '__main__':
    unittest.main()