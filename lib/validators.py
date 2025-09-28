"""
Validation Classes for User Management Server

This module contains validation logic for Israeli IDs, phone numbers,
and other user data fields.
"""

from lib.messages import ErrorMessages


class UserValidator:
    """
    User data validation class.
    
    Contains all validation logic for user-related data including
    Israeli ID validation, phone number validation, and field validation.
    """
    
    @staticmethod
    def validate_israeli_id(id_str):
        """
        Validate Israeli ID using the official checksum algorithm.
        
        Args:
            id_str (str): Israeli ID string to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(id_str, str) or not id_str:
            return False, ErrorMessages.ISRAELI_ID_EMPTY
        
        # Remove any whitespace
        id_str = id_str.strip()
        
        # Check if exactly 9 digits
        if not id_str.isdigit():
            return False, ErrorMessages.ISRAELI_ID_NOT_DIGITS
        
        if len(id_str) != 9:
            return False, ErrorMessages.ISRAELI_ID_WRONG_LENGTH
        
        # Calculate checksum using official Israeli ID algorithm
        total = 0
        for i, digit in enumerate(id_str[:-1]):  # All digits except the last one
            multiplier = 1 if i % 2 == 0 else 2
            result = int(digit) * multiplier
            
            # If result > 9, sum the digits (e.g., 14 -> 1+4 = 5)
            if result > 9:
                result = (result // 10) + (result % 10)
            
            total += result
        
        # Calculate expected checksum
        expected_checksum = (10 - (total % 10)) % 10
        actual_checksum = int(id_str[-1])
        
        if expected_checksum != actual_checksum:
            return False, ErrorMessages.ISRAELI_ID_INVALID_CHECKSUM
        
        return True, None
    
    @staticmethod
    def validate_phone_number(phone):
        """
        Validate phone number using E.164 international standard.
        
        Args:
            phone (str): Phone number string to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(phone, str) or not phone:
            return False, ErrorMessages.PHONE_EMPTY
        
        # Remove any whitespace
        phone = phone.strip()
        
        # Check if starts with +
        if not phone.startswith('+'):
            return False, ErrorMessages.PHONE_NO_PLUS
        
        # Check total length (+ plus 8-16 digits)
        if len(phone) < 9 or len(phone) > 17:
            return False, ErrorMessages.PHONE_WRONG_LENGTH
        
        # Check if all characters after + are digits
        digits_part = phone[1:]
        if not digits_part.isdigit():
            return False, ErrorMessages.PHONE_NOT_DIGITS
        
        return True, None
    
    @staticmethod
    def validate_name(name):
        """
        Validate user name field.
        
        Args:
            name (str): Name string to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(name, str):
            return False, ErrorMessages.NAME_NOT_STRING
        
        # Check if empty or only whitespace
        if not name or not name.strip():
            return False, ErrorMessages.NAME_EMPTY
        
        name = name.strip()
        
        # Check length
        if len(name) > 100:
            return False, ErrorMessages.NAME_TOO_LONG
        
        return True, None
    
    @staticmethod
    def validate_address(address):
        """
        Validate user address field.
        
        Args:
            address (str): Address string to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(address, str):
            return False, ErrorMessages.ADDRESS_NOT_STRING
        
        # Check if empty or only whitespace
        if not address or not address.strip():
            return False, ErrorMessages.ADDRESS_EMPTY
        
        address = address.strip()
        
        # Check length
        if len(address) > 200:
            return False, ErrorMessages.ADDRESS_TOO_LONG
        
        return True, None
    
    @classmethod
    def validate_user_data(cls, user_data):
        """
        Validate complete user data dictionary.
        
        Args:
            user_data (dict): Dictionary containing user data
            
        Returns:
            tuple: (is_valid, errors_dict)
        """
        if not isinstance(user_data, dict):
            return False, {"general": ErrorMessages.USER_DATA_NOT_DICT}
        
        errors = {}
        
        # Check required fields
        required_fields = ['id', 'name', 'phone', 'address']
        missing_fields = [field for field in required_fields if field not in user_data]
        
        if missing_fields:
            errors['missing_fields'] = missing_fields
        
        # Validate Israeli ID (if present in data)
        if 'id' in user_data:
            is_valid, error_msg = cls.validate_israeli_id(user_data['id'])
            if not is_valid:
                errors['id'] = error_msg
        
        # Validate name (if present in data)
        if 'name' in user_data:
            is_valid, error_msg = cls.validate_name(user_data['name'])
            if not is_valid:
                errors['name'] = error_msg
        
        # Validate phone (if present in data)
        if 'phone' in user_data:
            is_valid, error_msg = cls.validate_phone_number(user_data['phone'])
            if not is_valid:
                errors['phone'] = error_msg
        
        # Validate address (if present in data)
        if 'address' in user_data:
            is_valid, error_msg = cls.validate_address(user_data['address'])
            if not is_valid:
                errors['address'] = error_msg
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_user_data(user_data):
        """
        Sanitize user data by trimming whitespace.
        
        Args:
            user_data (dict): Raw user data
            
        Returns:
            dict: Sanitized user data
        """
        if not isinstance(user_data, dict):
            return user_data
        
        sanitized = {}
        for key, value in user_data.items():
            if isinstance(value, str):
                sanitized[key] = value.strip()
            else:
                sanitized[key] = value
        
        return sanitized


class RequestValidator:
    """
    HTTP request validation class.
    
    Contains validation logic for HTTP requests, content types, etc.
    """
    
    @staticmethod
    def validate_json_request(request):
        """
        Validate that request contains valid JSON.
        
        Args:
            request: Flask request object
            
        Returns:
            tuple: (is_valid, error_message, data)
        """
        if not request.is_json:
            return False, ErrorMessages.CONTENT_TYPE_JSON, None
        
        try:
            data = request.get_json()
            if data is None:
                return False, ErrorMessages.INVALID_JSON, None
            return True, None, data
        except Exception as e:
            return False, ErrorMessages.JSON_PARSE_ERROR.format(error=str(e)), None
    
    @staticmethod
    def validate_israeli_id_param(user_id):
        """
        Validate Israeli ID from URL parameter.
        
        Args:
            user_id (str): User ID from URL parameter
            
        Returns:
            tuple: (is_valid, error_message)
        """
        return UserValidator.validate_israeli_id(user_id)


class ValidationError(Exception):
    """
    Custom exception for validation errors.
    
    Attributes:
        message (str): Error message
        errors (dict): Dictionary of field-specific errors
        status_code (int): HTTP status code
    """
    
    def __init__(self, message, errors=None, status_code=400):
        super().__init__(message)
        self.message = message
        self.errors = errors or {}
        self.status_code = status_code
    
    def to_dict(self):
        """Convert exception to dictionary for JSON response."""
        result = {
            'error': ErrorMessages.VALIDATION_ERROR,
            'message': self.message
        }
        
        if self.errors:
            result['details'] = self.errors
        
        return result