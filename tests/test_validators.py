"""
Unit tests for validation logic.
"""

import unittest
from lib.validators import UserValidator, RequestValidator, ValidationError
from unittest.mock import Mock


class TestUserValidator(unittest.TestCase):
    """Test cases for UserValidator."""
    
    def test_valid_israeli_id(self):
        """Test validation of valid Israeli IDs."""
        valid_ids = [
            '123456782',  # Valid checksum
            '000000018',  # Valid checksum
            '111111118',  # Valid checksum
        ]
        
        for id_str in valid_ids:
            with self.subTest(id_str=id_str):
                is_valid, error_msg = UserValidator.validate_israeli_id(id_str)
                self.assertTrue(is_valid, f"ID {id_str} should be valid")
                self.assertIsNone(error_msg)
    
    def test_invalid_israeli_id_checksum(self):
        """Test validation of Israeli IDs with invalid checksums."""
        invalid_ids = [
            '123456789',  # Invalid checksum
            '000000019',  # Invalid checksum
            '111111119',  # Invalid checksum
        ]
        
        for id_str in invalid_ids:
            with self.subTest(id_str=id_str):
                is_valid, error_msg = UserValidator.validate_israeli_id(id_str)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error_msg)
    
    def test_israeli_id_wrong_length(self):
        """Test validation of Israeli IDs with wrong length."""
        invalid_ids = [
            '12345678',   # Too short
            '1234567890', # Too long
            '123',        # Too short
            '',           # Empty
        ]
        
        for id_str in invalid_ids:
            with self.subTest(id_str=id_str):
                is_valid, error_msg = UserValidator.validate_israeli_id(id_str)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error_msg)
    
    def test_israeli_id_non_digits(self):
        """Test validation of Israeli IDs with non-digit characters."""
        invalid_ids = [
            '12345678a',  # Contains letter
            '123-456-78', # Contains dashes
            '123 456 78', # Contains spaces
            'abcdefghi',  # All letters
        ]
        
        for id_str in invalid_ids:
            with self.subTest(id_str=id_str):
                is_valid, error_msg = UserValidator.validate_israeli_id(id_str)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error_msg)
    
    def test_israeli_id_invalid_types(self):
        """Test validation of Israeli IDs with invalid types."""
        invalid_inputs = [
            None,
            123456782,  # Integer instead of string
            [],         # List
            {},         # Dict
        ]
        
        for input_val in invalid_inputs:
            with self.subTest(input_val=input_val):
                is_valid, error_msg = UserValidator.validate_israeli_id(input_val)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error_msg)
    
    def test_valid_phone_numbers(self):
        """Test validation of valid phone numbers."""
        valid_phones = [
            '+972501234567',  # Israeli mobile
            '+14155552671',   # US number
            '+441234567890',  # UK number
            '+33123456789',   # French number
            '+12345678',      # Minimum length
            '+1234567890123456', # Maximum length
        ]
        
        for phone in valid_phones:
            with self.subTest(phone=phone):
                is_valid, error_msg = UserValidator.validate_phone_number(phone)
                self.assertTrue(is_valid, f"Phone {phone} should be valid")
                self.assertIsNone(error_msg)
    
    def test_invalid_phone_numbers(self):
        """Test validation of invalid phone numbers."""
        invalid_phones = [
            '972501234567',    # Missing +
            '+972-50-123-4567', # Contains dashes
            '+972 50 123 4567', # Contains spaces
            '+972abc1234567',   # Contains letters
            '+1234567',         # Too short
            '+12345678901234567', # Too long
            '',                 # Empty
            '+',                # Only +
        ]
        
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                is_valid, error_msg = UserValidator.validate_phone_number(phone)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error_msg)
    
    def test_valid_names(self):
        """Test validation of valid names."""
        valid_names = [
            'John Doe',
            'Jane Smith-Johnson',
            'José María',
            'A' * 100,  # Maximum length
            'X',         # Single character
        ]
        
        for name in valid_names:
            with self.subTest(name=name):
                is_valid, error_msg = UserValidator.validate_name(name)
                self.assertTrue(is_valid, f"Name '{name}' should be valid")
                self.assertIsNone(error_msg)
    
    def test_invalid_names(self):
        """Test validation of invalid names."""
        invalid_names = [
            '',           # Empty
            '   ',        # Only whitespace
            'A' * 101,    # Too long
            None,         # None
            123,          # Not a string
        ]
        
        for name in invalid_names:
            with self.subTest(name=name):
                is_valid, error_msg = UserValidator.validate_name(name)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error_msg)
    
    def test_valid_addresses(self):
        """Test validation of valid addresses."""
        valid_addresses = [
            '123 Main St, Tel Aviv',
            'Apartment 5B, 456 Oak Avenue, Jerusalem',
            'A' * 200,  # Maximum length
            'X',         # Single character
        ]
        
        for address in valid_addresses:
            with self.subTest(address=address):
                is_valid, error_msg = UserValidator.validate_address(address)
                self.assertTrue(is_valid, f"Address '{address}' should be valid")
                self.assertIsNone(error_msg)
    
    def test_invalid_addresses(self):
        """Test validation of invalid addresses."""
        invalid_addresses = [
            '',           # Empty
            '   ',        # Only whitespace
            'A' * 201,    # Too long
            None,         # None
            123,          # Not a string
        ]
        
        for address in invalid_addresses:
            with self.subTest(address=address):
                is_valid, error_msg = UserValidator.validate_address(address)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error_msg)
    
    def test_validate_complete_user_data(self):
        """Test validation of complete user data."""
        valid_data = {
            'id': '123456782',
            'name': 'John Doe',
            'phone': '+972501234567',
            'address': '123 Main St, Tel Aviv'
        }
        
        is_valid, errors = UserValidator.validate_user_data(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_user_data_missing_fields(self):
        """Test validation with missing required fields."""
        incomplete_data = {
            'name': 'John Doe',
            'phone': '+972501234567'
            # Missing 'id' and 'address'
        }
        
        is_valid, errors = UserValidator.validate_user_data(incomplete_data)
        self.assertFalse(is_valid)
        self.assertIn('missing_fields', errors)
    
    def test_validate_user_data_invalid_fields(self):
        """Test validation with invalid field values."""
        invalid_data = {
            'id': '123456789',      # Invalid checksum
            'name': '',             # Empty name
            'phone': '972501234567', # Missing +
            'address': '123 Main St'
        }
        
        is_valid, errors = UserValidator.validate_user_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('id', errors)
        self.assertIn('name', errors)
        self.assertIn('phone', errors)
    
    def test_sanitize_user_data(self):
        """Test data sanitization."""
        data_with_whitespace = {
            'id': ' 123456782 ',
            'name': ' John Doe ',
            'phone': ' +972501234567 ',
            'address': ' 123 Main St, Tel Aviv ',
            'extra_field': 123  # Non-string field
        }
        
        sanitized = UserValidator.sanitize_user_data(data_with_whitespace)
        
        self.assertEqual(sanitized['id'], '123456782')
        self.assertEqual(sanitized['name'], 'John Doe')
        self.assertEqual(sanitized['phone'], '+972501234567')
        self.assertEqual(sanitized['address'], '123 Main St, Tel Aviv')
        self.assertEqual(sanitized['extra_field'], 123)  # Unchanged


class TestRequestValidator(unittest.TestCase):
    """Test cases for RequestValidator."""
    
    def test_valid_json_request(self):
        """Test validation of valid JSON request."""
        mock_request = Mock()
        mock_request.is_json = True
        mock_request.get_json.return_value = {'key': 'value'}
        
        is_valid, error_msg, data = RequestValidator.validate_json_request(mock_request)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)
        self.assertEqual(data, {'key': 'value'})
    
    def test_non_json_request(self):
        """Test validation of non-JSON request."""
        mock_request = Mock()
        mock_request.is_json = False
        
        is_valid, error_msg, data = RequestValidator.validate_json_request(mock_request)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_msg)
        self.assertIsNone(data)
    
    def test_invalid_json_request(self):
        """Test validation of request with invalid JSON."""
        mock_request = Mock()
        mock_request.is_json = True
        mock_request.get_json.return_value = None
        
        is_valid, error_msg, data = RequestValidator.validate_json_request(mock_request)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_msg)
        self.assertIsNone(data)
    
    def test_json_parse_error(self):
        """Test validation when JSON parsing raises exception."""
        mock_request = Mock()
        mock_request.is_json = True
        mock_request.get_json.side_effect = Exception("JSON parse error")
        
        is_valid, error_msg, data = RequestValidator.validate_json_request(mock_request)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_msg)
        self.assertIn("JSON parse error", error_msg)
        self.assertIsNone(data)
    
    def test_validate_israeli_id_param(self):
        """Test validation of Israeli ID from URL parameter."""
        # Valid ID
        is_valid, error_msg = RequestValidator.validate_israeli_id_param('123456782')
        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)
        
        # Invalid ID
        is_valid, error_msg = RequestValidator.validate_israeli_id_param('123456789')
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_msg)


class TestValidationError(unittest.TestCase):
    """Test cases for ValidationError exception."""
    
    def test_validation_error_creation(self):
        """Test creating ValidationError."""
        error = ValidationError("Test error", {"field": "error"}, 400)
        
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.errors, {"field": "error"})
        self.assertEqual(error.status_code, 400)
    
    def test_validation_error_to_dict(self):
        """Test converting ValidationError to dictionary."""
        error = ValidationError("Test error", {"field": "error"})
        error_dict = error.to_dict()
        
        self.assertIn('error', error_dict)
        self.assertIn('message', error_dict)
        self.assertIn('details', error_dict)
        self.assertEqual(error_dict['message'], "Test error")
        self.assertEqual(error_dict['details'], {"field": "error"})


if __name__ == '__main__':
    unittest.main()