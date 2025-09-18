"""
User Management Flask Server - Class-Based Implementation

A Flask application for user management with Israeli ID validation,
implemented using a class-based approach for better organization.
"""

from flask import Flask, request, jsonify
from datetime import datetime
from lib.validators import UserValidator, RequestValidator, ValidationError as CustomValidationError
from marshmallow import ValidationError
from lib.messages import ErrorMessages, SuccessMessages, ResponseTemplates, WelcomeMessages
from config.manager import get_config
from db.database import get_database_manager, get_user_repository, initialize_database, DatabaseError
from lib.schemas import validate_user_create_data, serialize_user, serialize_user_id_list
from sqlalchemy.exc import IntegrityError
import logging

# Set up logging
logger = logging.getLogger(__name__)


class UserManagementServer:
    """
    User Management Flask Server Class
    
    Handles user creation, retrieval, and validation with Israeli ID support.
    """
    
    # HTTP Status Code Constants
    HTTP_OK = 200
    HTTP_CREATED = 201
    HTTP_BAD_REQUEST = 400
    HTTP_NOT_FOUND = 404
    HTTP_METHOD_NOT_ALLOWED = 405
    HTTP_CONFLICT = 409
    HTTP_INTERNAL_SERVER_ERROR = 500
    
    def __init__(self):
        """Initialize the Flask app and configure routes."""
        self.app = Flask(__name__)
        self.user_validator = UserValidator()
        self.request_validator = RequestValidator()
        self.config = get_config()  # Load configuration
        
        # Initialize database
        self.db_manager = get_database_manager()
        self.user_repository = get_user_repository()
        self._initialize_database()
        
        self._setup_routes()
        self._setup_error_handlers()
    
    def _initialize_database(self):
        """Initialize the database connection."""
        try:
            success = initialize_database()
            if success:
                logger.info("Database initialized successfully")
            else:
                logger.error("Database initialization failed")
                raise DatabaseError("Failed to initialize database")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def _setup_routes(self):
        """Set up all Flask routes."""
        self.app.add_url_rule('/', 'home', self.home, methods=['GET'])
        self.app.add_url_rule('/users', 'get_users', self.get_users, methods=['GET'])
        self.app.add_url_rule('/users', 'create_user', self.create_user, methods=['POST'])
        self.app.add_url_rule('/users/<user_id>', 'get_user', self.get_user, methods=['GET'])
        self.app.add_url_rule('/health', 'health_check', self.health_check, methods=['GET'])
    
    def _setup_error_handlers(self):
        """Set up error handlers."""
        self.app.errorhandler(404)(self.not_found)
        self.app.errorhandler(405)(self.method_not_allowed)
        self.app.errorhandler(500)(self.internal_error)
    



    def home(self):
        """Home endpoint - basic GET request."""
        try:
            user_count = self.user_repository.get_user_count()
        except DatabaseError:
            user_count = 0
        
        return jsonify(ResponseTemplates.success_response(
            message=WelcomeMessages.WELCOME_MESSAGE,
            data={
                'total_users': user_count,
                'endpoints': WelcomeMessages.ENDPOINTS_INFO
            }
        ))


    def get_users(self):
        """List all user IDs - GET request."""
        try:
            user_ids = self.user_repository.get_all_user_ids()
            data = serialize_user_id_list(user_ids)
            
            return jsonify(ResponseTemplates.success_response(
                message=SuccessMessages.USERS_LISTED,
                data=data
            ))
        except DatabaseError as e:
            logger.error(f"Failed to get users: {e}")
            return jsonify(ResponseTemplates.error_response(
                ErrorMessages.INTERNAL_SERVER_ERROR,
                "Failed to retrieve users"
            )), self.HTTP_INTERNAL_SERVER_ERROR


    def get_user(self, user_id):
        """Get user by Israeli ID - GET request with parameter."""
        # Validate Israeli ID format
        is_valid, error_msg = self.request_validator.validate_israeli_id_param(user_id)
        if not is_valid:
            return jsonify(ResponseTemplates.invalid_id_format_response(user_id, error_msg)), self.HTTP_BAD_REQUEST
        
        try:
            user = self.user_repository.get_user_by_id(user_id)
            if not user:
                return jsonify(ResponseTemplates.user_not_found_response(user_id)), self.HTTP_NOT_FOUND
            
            user_data = serialize_user(user)
            return jsonify(ResponseTemplates.success_response(
                message=SuccessMessages.USER_RETRIEVED,
                data={'user': user_data}
            ))
        except DatabaseError as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return jsonify(ResponseTemplates.error_response(
                ErrorMessages.INTERNAL_SERVER_ERROR,
                "Failed to retrieve user"
            )), self.HTTP_INTERNAL_SERVER_ERROR


    def create_user(self):
        """Create new user - POST request."""
        try:
            # Validate JSON request
            is_valid, error_msg, data = self.request_validator.validate_json_request(request)
            if not is_valid:
                return jsonify(ResponseTemplates.error_response(
                    ErrorMessages.INVALID_REQUEST, 
                    error_msg
                )), self.HTTP_BAD_REQUEST
            
            # Validate and sanitize user data using Marshmallow schema
            try:
                validated_data = validate_user_create_data(data)
            except ValidationError as e:
                return jsonify(ResponseTemplates.validation_error_response(e.messages)), self.HTTP_BAD_REQUEST
            
            # Create user in database
            try:
                user = self.user_repository.create_user(validated_data)
                user_data = serialize_user(user)
                
                return jsonify(ResponseTemplates.success_response(
                    message=SuccessMessages.USER_CREATED,
                    data={'user': user_data}
                )), self.HTTP_CREATED
                
            except IntegrityError:
                # User already exists
                return jsonify(ResponseTemplates.user_already_exists_response(validated_data['id'])), self.HTTP_CONFLICT
            except DatabaseError as e:
                logger.error(f"Database error creating user: {e}")
                return jsonify(ResponseTemplates.error_response(
                    ErrorMessages.INTERNAL_SERVER_ERROR,
                    "Failed to create user"
                )), self.HTTP_INTERNAL_SERVER_ERROR
            
        except CustomValidationError as e:
            return jsonify(e.to_dict()), e.status_code
        except Exception as e:
            logger.error(f"Unexpected error creating user: {e}")
            return jsonify(ResponseTemplates.error_response(
                ErrorMessages.INTERNAL_SERVER_ERROR,
                ErrorMessages.INTERNAL_SERVER_ERROR_MESSAGE
            )), self.HTTP_INTERNAL_SERVER_ERROR


    def health_check(self):
        """Health check endpoint."""
        try:
            # Check database health
            db_health = self.db_manager.health_check()
            user_count = self.user_repository.get_user_count()
            
            return jsonify(ResponseTemplates.success_response(
                message=SuccessMessages.HEALTH_CHECK,
                data={
                    'status': 'healthy',
                    'users_count': user_count,
                    'version': '1.0.0',
                    'server_type': 'Class-based Flask Server with Database',
                    'database': db_health
                }
            ))
        except DatabaseError as e:
            logger.error(f"Health check database error: {e}")
            return jsonify(ResponseTemplates.success_response(
                message=SuccessMessages.HEALTH_CHECK,
                data={
                    'status': 'degraded',
                    'users_count': 0,
                    'version': '1.0.0',
                    'server_type': 'Class-based Flask Server with Database',
                    'database': {'status': 'unhealthy', 'error': str(e)}
                }
            ))


    # Error handlers
    def not_found(self, error):
        """Handle 404 errors."""
        return jsonify(ResponseTemplates.error_response(
            ErrorMessages.NOT_FOUND,
            ErrorMessages.NOT_FOUND_MESSAGE
        )), self.HTTP_NOT_FOUND

    def method_not_allowed(self, error):
        """Handle 405 errors."""
        return jsonify(ResponseTemplates.error_response(
            ErrorMessages.METHOD_NOT_ALLOWED,
            ErrorMessages.METHOD_NOT_ALLOWED_MESSAGE
        )), self.HTTP_METHOD_NOT_ALLOWED

    def internal_error(self, error):
        """Handle 500 errors."""
        return jsonify(ResponseTemplates.error_response(
            ErrorMessages.INTERNAL_SERVER_ERROR,
            ErrorMessages.INTERNAL_SERVER_ERROR_MESSAGE
        )), self.HTTP_INTERNAL_SERVER_ERROR
    
    def run(self, debug=None, host=None, port=None):
        """Run the Flask application using configuration values."""
        # Get server configuration
        server_config = self.config.get_server_config()
        
        # Override with provided parameters if given
        if debug is not None:
            server_config['debug'] = debug
        if host is not None:
            server_config['host'] = host
        if port is not None:
            server_config['port'] = port
        
        print(WelcomeMessages.SERVER_STARTING)
        print("Available endpoints:")
        for endpoint in WelcomeMessages.AVAILABLE_ENDPOINTS:
            print(endpoint)
        print()
        print(WelcomeMessages.SERVER_RUNNING.format(
            host=server_config['host'], 
            port=server_config['port']
        ))
        
        self.app.run(**server_config)
    
    def get_app(self):
        """Get the Flask app instance (useful for testing)."""
        return self.app


if __name__ == '__main__':
    # Create and run the server
    server = UserManagementServer()
    server.run()  # Now uses configuration values