#!/usr/bin/env python3
"""
Test script for User Management Flask Server

This script demonstrates how to make requests to the Flask server
using the requests library for user management operations.
"""

import requests
import json
import time
import sys
import os

# Add the parent directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Server URL
BASE_URL = "http://localhost:5000"

# Sample valid Israeli IDs with correct checksums
VALID_ISRAELI_IDS = [
    "123456782",  # Valid checksum
    "000000018",  # Valid with leading zeros
    "111111118",  # Valid with repeated digits
]

def test_get_home():
    """Test GET request to home endpoint."""
    print("=== Testing GET / ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def create_user():
    """Test POST request to create user."""
    print("=== Testing POST /users ===")
    data = {
        "id": VALID_ISRAELI_IDS[0],
        "name": "John Doe",
        "phone": "+972501234567",
        "address": "123 Main Street, Tel Aviv, Israel"
    }
    
    response = requests.post(
        f"{BASE_URL}/users",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        user_id = response.json()["user"]["id"]
        print(f"Created user ID: {user_id}")
        return user_id
    
    print()
    return None

def test_get_users():
    """Test GET request to get all user IDs."""
    print("=== Testing GET /users ===")
    response = requests.get(f"{BASE_URL}/users")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def get_user_by_id(user_id):
    """Test GET request to get specific user."""
    if not user_id:
        print("Skipping GET /users/<id> - no user ID available")
        return
    
    print(f"=== Testing GET /users/{user_id} ===")
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def create_multiple_users():
    """Test creating multiple users."""
    print("=== Testing Multiple User Creation ===")
    users_data = [
        {
            "id": VALID_ISRAELI_IDS[1],
            "name": "Jane Smith",
            "phone": "+14155552671",
            "address": "456 Oak Avenue, San Francisco, CA"
        },
        {
            "id": VALID_ISRAELI_IDS[2],
            "name": "Mohammed Al-Rashid",
            "phone": "+971501234567",
            "address": "789 Palm Street, Dubai, UAE"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        response = requests.post(
            f"{BASE_URL}/users",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Creating user {user_data['name']}: Status {response.status_code}")
        if response.status_code == 201:
            created_users.append(user_data['id'])
    
    print(f"Created {len(created_users)} additional users")
    print()
    return created_users

def test_invalid_israeli_id():
    """Test creating user with invalid Israeli ID."""
    print("=== Testing Invalid Israeli ID ===")
    data = {
        "id": "123456789",  # Invalid checksum
        "name": "Invalid User",
        "phone": "+972501234567",
        "address": "Test Address"
    }
    
    response = requests.post(
        f"{BASE_URL}/users",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_invalid_phone():
    """Test creating user with invalid phone number."""
    print("=== Testing Invalid Phone Number ===")
    data = {
        "id": "987654321",  # This would need a valid checksum
        "name": "Invalid Phone User",
        "phone": "972501234567",  # Missing +
        "address": "Test Address"
    }
    
    response = requests.post(
        f"{BASE_URL}/users",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_duplicate_user():
    """Test creating duplicate user."""
    print("=== Testing Duplicate User Creation ===")
    data = {
        "id": VALID_ISRAELI_IDS[0],  # Same as first user
        "name": "Duplicate User",
        "phone": "+972521234567",
        "address": "Different Address"
    }
    
    response = requests.post(
        f"{BASE_URL}/users",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_health():
    """Test GET request to health endpoint."""
    print("=== Testing GET /health ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_user_not_found():
    """Test 404 error handling for non-existent user."""
    print("=== Testing User Not Found ===")
    response = requests.get(f"{BASE_URL}/users/999999999")  # Non-existent but valid format
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_invalid_user_id_format():
    """Test invalid Israeli ID format in URL."""
    print("=== Testing Invalid User ID Format ===")
    response = requests.get(f"{BASE_URL}/users/invalid123")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_missing_fields():
    """Test creating user with missing required fields."""
    print("=== Testing Missing Required Fields ===")
    data = {
        "id": VALID_ISRAELI_IDS[0],
        "name": "Incomplete User"
        # Missing phone and address
    }
    
    response = requests.post(
        f"{BASE_URL}/users",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_invalid_json():
    """Test invalid JSON handling."""
    print("=== Testing Invalid JSON ===")
    response = requests.post(
        f"{BASE_URL}/users",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def main():
    """Run all tests."""
    print("Testing User Management Flask Server")
    print("=" * 50)
    
    try:
        # Test basic endpoints
        test_get_home()
        test_health()
        
        # Test user operations
        user_id = create_user()
        test_get_users()
        get_user_by_id(user_id)
        
        # Test creating multiple users
        additional_users = create_multiple_users()
        test_get_users()  # Show all users
        
        # Test validation and error cases
        test_invalid_israeli_id()
        test_invalid_phone()
        test_duplicate_user()
        test_missing_fields()
        
        # Test error handling
        test_user_not_found()
        test_invalid_user_id_format()
        test_invalid_json()
        
        print("All tests completed!")
        print(f"Total users created: {1 + len(additional_users)}")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Flask server.")
        print("Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main()