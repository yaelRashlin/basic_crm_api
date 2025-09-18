#!/usr/bin/env python3
"""
API testing script.

This script can be run from anywhere to test the API endpoints.
"""

import sys
import os

# Add the parent directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import and run the API tests
from tests.test_requests import main

if __name__ == '__main__':
    main()