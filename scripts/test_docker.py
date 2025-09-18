#!/usr/bin/env python3
"""
Docker integration test script

This script tests the Docker container to ensure it's working correctly.
"""

import requests
import time
import sys
import json

def wait_for_server(url, timeout=30, interval=2):
    """Wait for the server to be ready."""
    print(f"Waiting for server at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print("⏳ Server not ready yet, waiting...")
        time.sleep(interval)
    
    print("❌ Server failed to start within timeout")
    return False

def test_endpoints(base_url):
    """Test the main API endpoints."""
    print(f"\n🧪 Testing API endpoints at {base_url}")
    
    tests = []
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            tests.append(("Health Check", "✅ PASS"))
        else:
            tests.append(("Health Check", f"❌ FAIL - Status: {response.status_code}"))
    except Exception as e:
        tests.append(("Health Check", f"❌ FAIL - Error: {e}"))
    
    # Test 2: Home endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            tests.append(("Home Endpoint", "✅ PASS"))
        else:
            tests.append(("Home Endpoint", f"❌ FAIL - Status: {response.status_code}"))
    except Exception as e:
        tests.append(("Home Endpoint", f"❌ FAIL - Error: {e}"))
    
    # Test 3: Get users (empty list)
    try:
        response = requests.get(f"{base_url}/users")
        if response.status_code == 200:
            tests.append(("Get Users", "✅ PASS"))
        else:
            tests.append(("Get Users", f"❌ FAIL - Status: {response.status_code}"))
    except Exception as e:
        tests.append(("Get Users", f"❌ FAIL - Error: {e}"))
    
    # Test 4: Create user
    user_data = {
        "id": "123456782",
        "name": "Docker Test User",
        "phone": "+972501234567",
        "address": "123 Docker Street, Container City"
    }
    
    try:
        response = requests.post(
            f"{base_url}/users",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            tests.append(("Create User", "✅ PASS"))
        else:
            tests.append(("Create User", f"❌ FAIL - Status: {response.status_code}"))
    except Exception as e:
        tests.append(("Create User", f"❌ FAIL - Error: {e}"))
    
    # Test 5: Get specific user
    try:
        response = requests.get(f"{base_url}/users/123456782")
        if response.status_code == 200:
            data = response.json()
            if data.get("user", {}).get("name") == "Docker Test User":
                tests.append(("Get Specific User", "✅ PASS"))
            else:
                tests.append(("Get Specific User", "❌ FAIL - Data mismatch"))
        else:
            tests.append(("Get Specific User", f"❌ FAIL - Status: {response.status_code}"))
    except Exception as e:
        tests.append(("Get Specific User", f"❌ FAIL - Error: {e}"))
    
    # Test 6: Invalid request (should return 400)
    try:
        response = requests.post(
            f"{base_url}/users",
            json={"invalid": "data"},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 400:
            tests.append(("Invalid Request Handling", "✅ PASS"))
        else:
            tests.append(("Invalid Request Handling", f"❌ FAIL - Status: {response.status_code}"))
    except Exception as e:
        tests.append(("Invalid Request Handling", f"❌ FAIL - Error: {e}"))
    
    # Print results
    print("\n📊 Test Results:")
    print("-" * 50)
    passed = 0
    for test_name, result in tests:
        print(f"{test_name:<25} {result}")
        if "✅ PASS" in result:
            passed += 1
    
    print("-" * 50)
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 All tests passed! Docker container is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the container logs.")
        return False

def main():
    """Main test function."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        base_url = "http://localhost:5000"
    
    print("🐳 Docker Container Integration Test")
    print("=" * 50)
    
    # Wait for server to be ready
    if not wait_for_server(base_url):
        sys.exit(1)
    
    # Run tests
    if test_endpoints(base_url):
        print("\n✅ Docker container test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Docker container test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()