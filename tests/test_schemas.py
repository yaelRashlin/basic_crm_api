"""
Unit tests for Marshmallow schemas.
"""

import unittest
from marshmallow import ValidationError
from lib.schemas import (
    UserCreateSchema, UserUpdateSchema, UserResponseSchema,
    validate_user_create_data, validate_user_update_data,
    serialize_user, serialize_user_id_list
)
from db.models import User
from datetime import datetime


class TestUserCreateSchema(unittest.TestCase):
    """Test cases for UserCreateSchema."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.schema = UserCreateSchema()
        self.valid_data = {
            'id': '123456782',
            'name': 'John Doe',
            'phone': '+972501234567',
            'address': '123 Main St, Tel Aviv'
        }
    
    def test_valid_user_data(self):
        """Test validation of valid user data."""
        result = self.schema.load(self.valid_data)
        
        self.assertEqual(result['id'], '123456782')
        self.assertEqual(result['name'], 'John Doe')
        self.assertEqual(result['phone'], '+972501234567')
        self.assertEqual(result['address'], '123 Main St, Tel Aviv')
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        incomplete_data = {
            'name': 'John Doe',
            'phone': '+972501234567'
            # Missing 'id' and 'address'
        }
        
        with self.assertRaises(ValidationError) as context:
            self.schema.load(incomplete_data)
        
        errors = context.exception.messages
        self.assertIn('missing_fields', errors)
    
    def test_invalid_israeli_id(self):
        """Test validation with invalid Israeli ID."""
        invalid_data = self.valid_data.copy()
        invalid_data['id'] = '123456789'  # Invalid checksum
        
        with self.assertRaises(ValidationError) as context:
            self.schema.load(invalid_data)
        
        errors = context.exception.messages
        self.assertIn('id', errors)
    
    def test_invalid_phone_number(self):
        """Test validation with invalid phone number."""
        invalid_data = self.valid_data.copy()
        invalid_data['phone'] = '972501234567'  # Missing +
        
        with self.assertRaises(ValidationError) as context:
            self.schema.load(invalid_data)
        
        errors = context.exception.messages
        self.assertIn('phone', errors)
    
    def test_empty_name(self):
        """Test validation with empty name."""
        invalid_data = self.valid_data.copy()
        invalid_data['name'] = ''
        
        with self.assertRaises(ValidationError) as context:
            self.schema.load(invalid_data)
        
        errors = context.exception.messages
        self.assertIn('missing_fields', errors)
    
    def test_data_sanitization(self):
        """Test that data is properly sanitized."""
        data_with_whitespace = {
            'id': ' 123456782 ',
            'name': ' John Doe ',
            'phone': ' +972501234567 ',
            'address': ' 123 Main St, Tel Aviv '
        }
        
        result = self.schema.load(data_with_whitespace)
        
        # Check that whitespace was trimmed
        self.assertEqual(result['id'], '123456782')
        self.assertEqual(result['name'], 'John Doe')
        self.assertEqual(result['phone'], '+972501234567')
        self.assertEqual(result['address'], '123 Main St, Tel Aviv')


class TestUserUpdateSchema(unittest.TestCase):
    """Test cases for UserUpdateSchema."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.schema = UserUpdateSchema()
    
    def test_partial_update(self):
        """Test partial update with only some fields."""
        update_data = {
            'name': 'Jane Doe',
            'phone': '+972507654321'
        }
        
        result = self.schema.load(update_data)
        
        self.assertEqual(result['name'], 'Jane Doe')
        self.assertEqual(result['phone'], '+972507654321')
        self.assertNotIn('address', result)
    
    def test_empty_update_data(self):
        """Test validation with no update fields."""
        with self.assertRaises(ValidationError) as context:
            self.schema.load({})
        
        errors = context.exception.messages
        self.assertIn('message', errors)
    
    def test_invalid_phone_in_update(self):
        """Test validation with invalid phone in update."""
        update_data = {
            'phone': 'invalid-phone'
        }
        
        with self.assertRaises(ValidationError) as context:
            self.schema.load(update_data)
        
        errors = context.exception.messages
        self.assertIn('phone', errors)


class TestUserResponseSchema(unittest.TestCase):
    """Test cases for UserResponseSchema."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.schema = UserResponseSchema()
    
    def test_user_serialization(self):
        """Test serialization of user data."""
        user_data = {
            'id': '123456782',
            'name': 'John Doe',
            'phone': '+972501234567',
            'address': '123 Main St, Tel Aviv',
            'created_at': datetime(2024, 1, 1, 12, 0, 0),
            'updated_at': datetime(2024, 1, 1, 12, 0, 0)
        }
        
        result = self.schema.dump(user_data)
        
        self.assertEqual(result['id'], '123456782')
        self.assertEqual(result['name'], 'John Doe')
        self.assertEqual(result['phone'], '+972501234567')
        self.assertEqual(result['address'], '123 Main St, Tel Aviv')
        self.assertEqual(result['created_at'], '2024-01-01T12:00:00')
        self.assertEqual(result['updated_at'], '2024-01-01T12:00:00')


class TestSchemaHelperFunctions(unittest.TestCase):
    """Test cases for schema helper functions."""
    
    def test_validate_user_create_data(self):
        """Test validate_user_create_data function."""
        valid_data = {
            'id': '123456782',
            'name': 'John Doe',
            'phone': '+972501234567',
            'address': '123 Main St, Tel Aviv'
        }
        
        result = validate_user_create_data(valid_data)
        self.assertEqual(result['id'], '123456782')
    
    def test_validate_user_create_data_invalid(self):
        """Test validate_user_create_data with invalid data."""
        invalid_data = {
            'id': '123456789',  # Invalid checksum
            'name': 'John Doe',
            'phone': '+972501234567',
            'address': '123 Main St, Tel Aviv'
        }
        
        with self.assertRaises(ValidationError):
            validate_user_create_data(invalid_data)
    
    def test_serialize_user(self):
        """Test serialize_user function."""
        user = User(
            id='123456782',
            name='John Doe',
            phone='+972501234567',
            address='123 Main St, Tel Aviv'
        )
        
        # Set timestamps for testing
        user.created_at = datetime(2024, 1, 1, 12, 0, 0)
        user.updated_at = datetime(2024, 1, 1, 12, 0, 0)
        
        result = serialize_user(user)
        
        self.assertEqual(result['id'], '123456782')
        self.assertEqual(result['name'], 'John Doe')
        self.assertEqual(result['created_at'], '2024-01-01T12:00:00')
    
    def test_serialize_user_id_list(self):
        """Test serialize_user_id_list function."""
        user_ids = ['123456782', '987654321', '111111118']
        
        result = serialize_user_id_list(user_ids)
        
        self.assertEqual(result['users'], user_ids)
        self.assertEqual(result['count'], 3)


if __name__ == '__main__':
    unittest.main()