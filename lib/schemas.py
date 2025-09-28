"""
Marshmallow Schemas for User Management Flask Server

This module defines serialization and validation schemas using Marshmallow,
integrating with existing validation logic.
"""

from datetime import datetime
from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError, post_load, pre_load, EXCLUDE
from lib.validators import UserValidator
from lib.messages import ErrorMessages


class IsraeliIDField(fields.String):
    """
    Custom Marshmallow field for Israeli ID validation.
    
    Integrates with existing Israeli ID validation logic.
    """
    
    def _validate(self, value, attr=None, data=None, **kwargs):
        """Validate Israeli ID using existing validation logic."""
        if value is None or value == '':
            return  # Let schema-level validation handle missing/empty fields
        
        is_valid, error_msg = UserValidator.validate_israeli_id(value)
        if not is_valid:
            raise ValidationError(error_msg)


class PhoneNumberField(fields.String):
    """
    Custom Marshmallow field for phone number validation.
    
    Integrates with existing E.164 phone validation logic.
    """
    
    def _validate(self, value, attr=None, data=None, **kwargs):
        """Validate phone number using existing validation logic."""
        if value is None or value == '':
            return  # Let schema-level validation handle missing/empty fields
        
        is_valid, error_msg = UserValidator.validate_phone_number(value)
        if not is_valid:
            raise ValidationError(error_msg)


class NameField(fields.String):
    """
    Custom Marshmallow field for name validation.
    
    Integrates with existing name validation logic.
    """
    
    def _validate(self, value, attr=None, data=None, **kwargs):
        """Validate name using existing validation logic."""
        if value is None or value == '':
            return  # Let schema-level validation handle missing/empty fields
        
        is_valid, error_msg = UserValidator.validate_name(value)
        if not is_valid:
            raise ValidationError(error_msg)


class AddressField(fields.String):
    """
    Custom Marshmallow field for address validation.
    
    Integrates with existing address validation logic.
    """
    
    def _validate(self, value, attr=None, data=None, **kwargs):
        """Validate address using existing validation logic."""
        if value is None or value == '':
            return  # Let schema-level validation handle missing/empty fields
        
        is_valid, error_msg = UserValidator.validate_address(value)
        if not is_valid:
            raise ValidationError(error_msg)


class BaseUserSchema(Schema):
    """
    Base schema for user data with common fields and validation.
    """
    
    id = IsraeliIDField(required=False, allow_none=True)
    name = NameField(required=False, allow_none=True)
    phone = PhoneNumberField(required=False, allow_none=True)
    address = AddressField(required=False, allow_none=True)
    
    @pre_load
    def sanitize_data(self, data, **kwargs):
        """Sanitize input data by trimming whitespace."""
        if isinstance(data, dict):
            return UserValidator.sanitize_user_data(data)
        return data
    
    @validates_schema
    def validate_required_fields(self, data, **kwargs):
        """Validate that all required fields are present and not empty."""
        required_fields = ['id', 'name', 'phone', 'address']
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field] or (isinstance(data[field], str) and not data[field].strip()):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError({
                'missing_fields': missing_fields,
                'message': f"Missing required fields: {', '.join(missing_fields)}"
            })


class UserCreateSchema(BaseUserSchema):
    """
    Schema for user creation requests.
    
    Validates input data for creating new users.
    """
    
    class Meta:
        # Only allow known fields
        unknown = EXCLUDE
    
    @post_load
    def make_user_data(self, data, **kwargs):
        """Transform validated data into user creation format."""
        return {
            'id': data['id'],
            'name': data['name'],
            'phone': data['phone'],
            'address': data['address']
        }


class UserUpdateSchema(Schema):
    """
    Schema for user update requests.
    
    All fields are optional for updates.
    """
    
    name = NameField(required=False, allow_none=False, load_default=None)
    phone = PhoneNumberField(required=False, allow_none=False, load_default=None)
    address = AddressField(required=False, allow_none=False, load_default=None)
    
    class Meta:
        # Only allow known fields
        unknown = EXCLUDE
    
    @pre_load
    def sanitize_data(self, data, **kwargs):
        """Sanitize input data by trimming whitespace."""
        if isinstance(data, dict):
            return UserValidator.sanitize_user_data(data)
        return data
    
    @validates_schema
    def validate_at_least_one_field(self, data, **kwargs):
        """Ensure at least one field is provided for update."""
        if not any(value is not None for value in data.values()):
            raise ValidationError({
                'message': 'At least one field must be provided for update'
            })
    
    @post_load
    def make_update_data(self, data, **kwargs):
        """Transform validated data into user update format."""
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}


class UserResponseSchema(Schema):
    """
    Schema for user response serialization.
    
    Formats user data for API responses.
    """
    
    id = fields.String(required=True)
    name = fields.String(required=True)
    phone = fields.String(required=True)
    address = fields.String(required=True)
    created_at = fields.DateTime(format='iso', required=True)
    updated_at = fields.DateTime(format='iso', required=True)
    
    class Meta:
        # Preserve field order
        ordered = True


class UserListResponseSchema(Schema):
    """
    Schema for user list responses.
    
    Formats multiple users for API responses.
    """
    
    users = fields.List(fields.Nested(UserResponseSchema), required=True)
    count = fields.Integer(required=True)
    
    class Meta:
        ordered = True


class UserIDListResponseSchema(Schema):
    """
    Schema for user ID list responses.
    
    Formats user ID lists for API responses.
    """
    
    users = fields.List(fields.String(), required=True)
    count = fields.Integer(required=True)
    
    class Meta:
        ordered = True


class ErrorResponseSchema(Schema):
    """
    Schema for error responses.
    
    Standardizes error response format.
    """
    
    error = fields.String(required=True)
    message = fields.String(required=True)
    details = fields.Dict(load_default=None)
    
    class Meta:
        ordered = True


class ValidationErrorResponseSchema(ErrorResponseSchema):
    """
    Schema for validation error responses.
    
    Includes field-specific validation errors.
    """
    
    details = fields.Dict(required=True)


class SuccessResponseSchema(Schema):
    """
    Schema for success responses.
    
    Standardizes success response format.
    """
    
    success = fields.Boolean(required=True, dump_default=True)
    message = fields.String(required=True)
    data = fields.Dict(load_default=None)
    
    class Meta:
        ordered = True


# Schema instances for easy importing
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()
user_response_schema = UserResponseSchema()
user_list_response_schema = UserListResponseSchema()
user_id_list_response_schema = UserIDListResponseSchema()
error_response_schema = ErrorResponseSchema()
validation_error_response_schema = ValidationErrorResponseSchema()
success_response_schema = SuccessResponseSchema()


def serialize_user(user_obj):
    """
    Serialize a User model instance to dictionary.
    
    Args:
        user_obj: User model instance
        
    Returns:
        dict: Serialized user data
    """
    if hasattr(user_obj, 'to_dict'):
        # Use model's to_dict method if available
        return user_obj.to_dict()
    else:
        # Fallback serialization
        return user_response_schema.dump(user_obj)


def serialize_user_list(users):
    """
    Serialize a list of User model instances.
    
    Args:
        users: List of User model instances
        
    Returns:
        dict: Serialized user list data
    """
    serialized_users = [serialize_user(user) for user in users]
    return {
        'users': serialized_users,
        'count': len(serialized_users)
    }


def serialize_user_id_list(user_ids):
    """
    Serialize a list of user IDs.
    
    Args:
        user_ids: List of user ID strings
        
    Returns:
        dict: Serialized user ID list data
    """
    return {
        'users': user_ids,
        'count': len(user_ids)
    }


def validate_user_create_data(data):
    """
    Validate user creation data using Marshmallow schema.
    
    Args:
        data: Raw user data dictionary
        
    Returns:
        dict: Validated and sanitized user data
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        return user_create_schema.load(data)
    except ValidationError as e:
        # Re-raise the original ValidationError
        raise e


def validate_user_update_data(data):
    """
    Validate user update data using Marshmallow schema.
    
    Args:
        data: Raw user update data dictionary
        
    Returns:
        dict: Validated and sanitized user update data
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        return user_update_schema.load(data)
    except ValidationError as e:
        # Re-raise the original ValidationError
        raise e


def format_validation_error(validation_error):
    """
    Format Marshmallow validation error for API response.
    
    Args:
        validation_error: Marshmallow ValidationError
        
    Returns:
        dict: Formatted error response
    """
    return {
        'error': ErrorMessages.VALIDATION_ERROR,
        'message': 'Validation failed',
        'details': validation_error.messages
    }


# Export main schemas and functions
__all__ = [
    'UserCreateSchema', 'UserUpdateSchema', 'UserResponseSchema',
    'UserListResponseSchema', 'UserIDListResponseSchema',
    'ErrorResponseSchema', 'ValidationErrorResponseSchema', 'SuccessResponseSchema',
    'user_create_schema', 'user_update_schema', 'user_response_schema',
    'user_list_response_schema', 'user_id_list_response_schema',
    'error_response_schema', 'validation_error_response_schema', 'success_response_schema',
    'serialize_user', 'serialize_user_list', 'serialize_user_id_list',
    'validate_user_create_data', 'validate_user_update_data', 'format_validation_error'
]