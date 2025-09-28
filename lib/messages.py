"""
Centralized Error Messages and Response Messages

This module contains all error messages, success messages, and response templates
used throughout the User Management Server application.
"""


class ErrorMessages:
    """
    Centralized error messages for the application.
    
    All error messages are defined here to ensure consistency
    and make maintenance easier.
    """
    
    # Israeli ID Validation Errors
    ISRAELI_ID_EMPTY = "Israeli ID must be a non-empty string"
    ISRAELI_ID_NOT_DIGITS = "Israeli ID must contain only digits"
    ISRAELI_ID_WRONG_LENGTH = "Israeli ID must be exactly 9 digits"
    ISRAELI_ID_INVALID_CHECKSUM = "Invalid Israeli ID checksum"
    ISRAELI_ID_INVALID_FORMAT = "Invalid Israeli ID format"
    
    # Phone Number Validation Errors
    PHONE_EMPTY = "Phone number must be a non-empty string"
    PHONE_NO_PLUS = "Phone number must start with +"
    PHONE_WRONG_LENGTH = "Phone number must be between 8-16 characters total"
    PHONE_NOT_DIGITS = "Phone number must contain only digits after +"
    PHONE_INVALID = "Invalid phone number"
    
    # Name Validation Errors
    NAME_NOT_STRING = "Name must be a string"
    NAME_EMPTY = "Name cannot be empty"
    NAME_TOO_LONG = "Name must not exceed 100 characters"
    NAME_INVALID = "Invalid name"
    
    # Address Validation Errors
    ADDRESS_NOT_STRING = "Address must be a string"
    ADDRESS_EMPTY = "Address cannot be empty"
    ADDRESS_TOO_LONG = "Address must not exceed 200 characters"
    ADDRESS_INVALID = "Invalid address"
    
    # Request Validation Errors
    CONTENT_TYPE_JSON = "Content-Type must be application/json"
    INVALID_JSON = "Invalid JSON data"
    JSON_PARSE_ERROR = "JSON parsing error: {error}"
    
    # User Data Validation Errors
    USER_DATA_NOT_DICT = "User data must be a dictionary"
    MISSING_REQUIRED_FIELDS = "Missing required fields"
    VALIDATION_FAILED = "Validation failed"
    
    # Business Logic Errors
    USER_ALREADY_EXISTS = "User already exists"
    USER_NOT_FOUND = "User not found"
    
    # HTTP Errors
    NOT_FOUND = "Not Found"
    NOT_FOUND_MESSAGE = "The requested resource was not found"
    METHOD_NOT_ALLOWED = "Method Not Allowed"
    METHOD_NOT_ALLOWED_MESSAGE = "The method is not allowed for the requested URL"
    INTERNAL_SERVER_ERROR = "Internal Server Error"
    INTERNAL_SERVER_ERROR_MESSAGE = "An unexpected error occurred"
    
    # General Errors
    INVALID_REQUEST = "Invalid Request"
    VALIDATION_ERROR = "Validation Error"


class SuccessMessages:
    """
    Centralized success messages for the application.
    """
    
    USER_CREATED = "User created successfully"
    USER_RETRIEVED = "User retrieved successfully"
    USERS_LISTED = "Users listed successfully"
    HEALTH_CHECK = "Service is healthy"


class ResponseTemplates:
    """
    Response templates for consistent API responses.
    """
    
    @staticmethod
    def error_response(error_type, message, details=None, status_code=None):
        """
        Create standardized error response.
        
        Args:
            error_type (str): Type of error
            message (str): Error message
            details (dict, optional): Additional error details
            status_code (int, optional): HTTP status code
            
        Returns:
            dict: Standardized error response
        """
        response = {
            'error': error_type,
            'message': message
        }
        
        if details:
            response['details'] = details
            
        if status_code:
            response['status_code'] = status_code
            
        return response
    
    @staticmethod
    def success_response(message, data=None, timestamp=None):
        """
        Create standardized success response.
        
        Args:
            message (str): Success message
            data (dict, optional): Response data
            timestamp (str, optional): Response timestamp
            
        Returns:
            dict: Standardized success response
        """
        from datetime import datetime
        
        response = {
            'message': message
        }
        
        if data is not None:
            if isinstance(data, dict):
                response.update(data)
            else:
                response['data'] = data
        
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        response['timestamp'] = timestamp
        
        return response
    
    @staticmethod
    def validation_error_response(errors):
        """
        Create validation error response.
        
        Args:
            errors (dict): Dictionary of validation errors
            
        Returns:
            dict: Validation error response
        """
        if 'missing_fields' in errors:
            return {
                'error': ErrorMessages.MISSING_REQUIRED_FIELDS,
                'missing_fields': errors['missing_fields'],
                'required_fields': ['id', 'name', 'phone', 'address']
            }
        else:
            return {
                'error': ErrorMessages.VALIDATION_FAILED,
                'details': errors
            }
    
    @staticmethod
    def user_not_found_response(user_id):
        """
        Create user not found error response.
        
        Args:
            user_id (str): User ID that was not found
            
        Returns:
            dict: User not found error response
        """
        return {
            'error': ErrorMessages.USER_NOT_FOUND,
            'user_id': user_id
        }
    
    @staticmethod
    def user_already_exists_response(user_id):
        """
        Create user already exists error response.
        
        Args:
            user_id (str): User ID that already exists
            
        Returns:
            dict: User already exists error response
        """
        return {
            'error': ErrorMessages.USER_ALREADY_EXISTS,
            'user_id': user_id
        }
    
    @staticmethod
    def invalid_id_format_response(user_id, error_msg):
        """
        Create invalid ID format error response.
        
        Args:
            user_id (str): Invalid user ID
            error_msg (str): Specific error message
            
        Returns:
            dict: Invalid ID format error response
        """
        return {
            'error': ErrorMessages.ISRAELI_ID_INVALID_FORMAT,
            'message': error_msg,
            'user_id': user_id
        }


class WelcomeMessages:
    """
    Welcome and informational messages.
    """
    
    WELCOME_MESSAGE = "Welcome to User Management Flask Server"
    SERVER_STARTING = "Starting User Management Flask Server (Class-based)..."
    SERVER_RUNNING = "Server running on http://{host}:{port}"
    
    ENDPOINTS_INFO = {
        'GET /': 'This endpoint',
        'POST /users': 'Create new user',
        'GET /users/<id>': 'Get user by Israeli ID',
        'GET /users': 'List all user IDs',
        'GET /health': 'Health check'
    }
    
    AVAILABLE_ENDPOINTS = [
        "  GET  /              - Home page",
        "  POST /users         - Create new user",
        "  GET  /users/<id>    - Get user by Israeli ID",
        "  GET  /users         - List all user IDs",
        "  GET  /health        - Health check"
    ]


class LogMessages:
    """
    Log messages for debugging and monitoring.
    """
    
    USER_CREATED_LOG = "User created: {user_id} - {name}"
    USER_RETRIEVED_LOG = "User retrieved: {user_id}"
    USER_NOT_FOUND_LOG = "User not found: {user_id}"
    VALIDATION_ERROR_LOG = "Validation error for user: {errors}"
    REQUEST_ERROR_LOG = "Request error: {error}"
    
    SERVER_STARTED = "Server started successfully on {host}:{port}"
    SERVER_ERROR = "Server error: {error}"