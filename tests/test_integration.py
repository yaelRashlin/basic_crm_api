"""
Integration tests for the Flask application.
"""

import unittest
import json
import tempfile
import os
from app.server import UserManagementServer
from config.manager import ConfigManager


class TestFlaskAppIntegration(unittest.TestCase):
    """Integration tests for the Flask application."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create test configuration
        test_config = ConfigManager(verbose=False)
        test_config.config = {
            'server': {
                'host': '127.0.0.1',
                'port': 5000,
                'debug': True,
                'threaded': True
            },
            'database': {
                'type': 'sqlite',
                'filename': self.temp_db.name,
                'echo': False,
                'pool_size': 1,
                'max_overflow': 0,
                'connect_args': {'check_same_thread': False}
            }
        }
        
        # Create server instance with test config
        self.server = UserManagementServer()
        self.server.config = test_config
        self.server.db_manager.config = test_config
        self.server.user_repository.db_manager.config = test_config
        
        # Initialize database
        self.server.db_manager.initialize()
        
        # Create test client
        self.client = self.server.app.test_client()
        self.client.testing = True
        
        # Test user data
        self.test_user = {
            'id': '123456782',
            'name': 'John Doe',
            'phone': '+972501234567',
            'address': '123 Main St, Tel Aviv'
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.server.db_manager:
            self.server.db_manager.close()
        
        # Remove temporary database file
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_home_endpoint(self):
        """Test the home endpoint."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('total_users', data)
        self.assertIn('endpoints', data)
    
    def test_health_check_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('status', data)
        self.assertIn('database', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_create_user_success(self):
        """Test successful user creation."""
        response = self.client.post('/users',
                                  data=json.dumps(self.test_user),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['id'], '123456782')
        self.assertEqual(data['user']['name'], 'John Doe')
    
    def test_create_user_invalid_data(self):
        """Test user creation with invalid data."""
        invalid_user = {
            'id': '123456789',  # Invalid checksum
            'name': 'John Doe',
            'phone': '+972501234567',
            'address': '123 Main St, Tel Aviv'
        }
        
        response = self.client.post('/users',
                                  data=json.dumps(invalid_user),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('details', data)
    
    def test_create_user_missing_fields(self):
        """Test user creation with missing fields."""
        incomplete_user = {
            'name': 'John Doe',
            'phone': '+972501234567'
            # Missing 'id' and 'address'
        }
        
        response = self.client.post('/users',
                                  data=json.dumps(incomplete_user),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_create_duplicate_user(self):
        """Test creating a user with duplicate ID."""
        # Create first user
        self.client.post('/users',
                        data=json.dumps(self.test_user),
                        content_type='application/json')
        
        # Try to create duplicate
        response = self.client.post('/users',
                                  data=json.dumps(self.test_user),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 409)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('user_id', data)
    
    def test_get_user_success(self):
        """Test successful user retrieval."""
        # Create user first
        self.client.post('/users',
                        data=json.dumps(self.test_user),
                        content_type='application/json')
        
        # Get user
        response = self.client.get('/users/123456782')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['id'], '123456782')
    
    def test_get_user_not_found(self):
        """Test retrieving non-existent user."""
        response = self.client.get('/users/999999998')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('user_id', data)
    
    def test_get_user_invalid_id_format(self):
        """Test retrieving user with invalid ID format."""
        response = self.client.get('/users/invalid-id')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('user_id', data)
    
    def test_get_users_list_empty(self):
        """Test getting user list when empty."""
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('users', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['users']), 0)
    
    def test_get_users_list_with_users(self):
        """Test getting user list with users."""
        # Create multiple users
        user1 = self.test_user.copy()
        user2 = {
            'id': '987654324',
            'name': 'Jane Smith',
            'phone': '+972507654321',
            'address': '456 Oak Ave, Jerusalem'
        }
        
        self.client.post('/users', data=json.dumps(user1), content_type='application/json')
        self.client.post('/users', data=json.dumps(user2), content_type='application/json')
        
        # Get user list
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['count'], 2)
        self.assertIn('123456782', data['users'])
        self.assertIn('987654324', data['users'])
    
    def test_invalid_json_request(self):
        """Test request with invalid JSON."""
        response = self.client.post('/users',
                                  data='invalid json',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_non_json_request(self):
        """Test request without JSON content type."""
        response = self.client.post('/users',
                                  data=json.dumps(self.test_user),
                                  content_type='text/plain')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_method_not_allowed(self):
        """Test method not allowed error."""
        response = self.client.put('/users')
        self.assertEqual(response.status_code, 405)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_not_found_endpoint(self):
        """Test 404 error for non-existent endpoint."""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_complete_user_workflow(self):
        """Test complete user workflow: create, get, list."""
        # 1. Initially no users
        response = self.client.get('/users')
        data = json.loads(response.data)
        self.assertEqual(data['count'], 0)
        
        # 2. Create user
        response = self.client.post('/users',
                                  data=json.dumps(self.test_user),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        # 3. Get specific user
        response = self.client.get('/users/123456782')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['user']['name'], 'John Doe')
        
        # 4. List users (should have 1)
        response = self.client.get('/users')
        data = json.loads(response.data)
        self.assertEqual(data['count'], 1)
        self.assertIn('123456782', data['users'])
        
        # 5. Health check should show 1 user
        response = self.client.get('/health')
        data = json.loads(response.data)
        self.assertEqual(data['users_count'], 1)


if __name__ == '__main__':
    unittest.main()