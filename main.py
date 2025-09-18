#!/usr/bin/env python3
"""
Main entry point for User Management Flask Server

This script provides the main entry point for running the server
with the new organized file structure.
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.server import UserManagementServer

if __name__ == '__main__':
    # Create and run the server
    server = UserManagementServer()
    server.run()