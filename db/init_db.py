#!/usr/bin/env python3
"""
Database Initialization Script for User Management Flask Server

This script initializes the database, creates tables, and can be used
for database migrations and setup.
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from db.database import get_database_manager, initialize_database, close_database
from db.models import Base, User
from config.manager import get_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_database(force_recreate=False):
    """
    Initialize the database and create tables.
    
    Args:
        force_recreate (bool): If True, drop and recreate all tables
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        config = get_config()
        db_url = config.get_database_url()
        
        logger.info(f"Initializing database: {db_url}")
        
        # Get database manager
        db_manager = get_database_manager()
        
        if force_recreate:
            logger.warning("Force recreate enabled - dropping all tables")
            if db_manager.engine:
                Base.metadata.drop_all(db_manager.engine)
                logger.info("All tables dropped")
        
        # Initialize database
        success = initialize_database()
        
        if success:
            logger.info("Database initialization completed successfully")
            
            # Verify tables exist
            with db_manager.session_scope() as session:
                # Test table creation by counting users
                user_count = session.query(User).count()
                logger.info(f"Database verification successful - {user_count} users found")
            
            return True
        else:
            logger.error("Database initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False
    finally:
        close_database()


def check_database_status():
    """
    Check database status and connection.
    
    Returns:
        dict: Database status information
    """
    try:
        config = get_config()
        db_url = config.get_database_url()
        
        logger.info(f"Checking database status: {db_url}")
        
        # Check if database file exists (for SQLite)
        if db_url.startswith('sqlite:///'):
            db_file = db_url.replace('sqlite:///', '')
            file_exists = os.path.exists(db_file)
            file_size = os.path.getsize(db_file) if file_exists else 0
            
            logger.info(f"Database file exists: {file_exists}")
            if file_exists:
                logger.info(f"Database file size: {file_size} bytes")
        
        # Test database connection
        db_manager = get_database_manager()
        success = db_manager.initialize()
        
        if success:
            health = db_manager.health_check()
            logger.info(f"Database health check: {health}")
            
            return {
                'status': 'healthy',
                'url': db_url,
                'file_exists': file_exists if db_url.startswith('sqlite:///') else None,
                'file_size': file_size if db_url.startswith('sqlite:///') else None,
                'health': health
            }
        else:
            return {
                'status': 'unhealthy',
                'url': db_url,
                'error': 'Failed to initialize database'
            }
            
    except Exception as e:
        logger.error(f"Database status check error: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        close_database()


def create_sample_data(force_recreate=False):
    """
    Create sample user data for testing.
    
    Args:
        force_recreate (bool): If True, delete existing sample users first
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from db.database import get_user_repository
        
        logger.info("Creating sample user data")
        
        # Initialize database first
        if not initialize_database():
            logger.error("Failed to initialize database for sample data")
            return False
        
        user_repo = get_user_repository()
        
        # Sample users with valid Israeli IDs
        sample_users = [
            {
                'id': '123456782',  # Valid Israeli ID with checksum
                'name': 'John Doe',
                'phone': '+972501234567',
                'address': '123 Main St, Tel Aviv, Israel'
            },
            {
                'id': '987654321',  # Valid Israeli ID with checksum
                'name': 'Jane Smith',
                'phone': '+972507654321',
                'address': '456 Oak Ave, Jerusalem, Israel'
            }
        ]
        
        created_count = 0
        for user_data in sample_users:
            try:
                # Check if user already exists
                if user_repo.user_exists(user_data['id']):
                    if force_recreate:
                        logger.info(f"Deleting existing sample user {user_data['id']} for recreation")
                        user_repo.delete_user(user_data['id'])
                    else:
                        logger.info(f"Sample user {user_data['id']} already exists, skipping")
                        continue
                
                user = user_repo.create_user(user_data)
                logger.info(f"Created sample user: {user.id} - {user.name}")
                created_count += 1
            except Exception as e:
                logger.warning(f"Failed to create sample user {user_data['id']}: {e}")
        
        if created_count > 0:
            logger.info(f"Created {created_count} new sample users")
        else:
            logger.info("No new sample users created (all already exist)")
        
        return True  # Return True if process completed successfully, regardless of whether new users were created
        
    except Exception as e:
        logger.error(f"Sample data creation error: {e}")
        return False
    finally:
        close_database()


def backup_database(backup_path=None):
    """
    Create a backup of the database (SQLite only).
    
    Args:
        backup_path (str): Path for backup file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        config = get_config()
        db_url = config.get_database_url()
        
        if not db_url.startswith('sqlite:///'):
            logger.error("Backup only supported for SQLite databases")
            return False
        
        db_file = db_url.replace('sqlite:///', '')
        
        if not os.path.exists(db_file):
            logger.error(f"Database file not found: {db_file}")
            return False
        
        if backup_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{db_file}.backup_{timestamp}"
        
        import shutil
        shutil.copy2(db_file, backup_path)
        
        logger.info(f"Database backed up to: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Database backup error: {e}")
        return False


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database initialization and management')
    parser.add_argument('--init', action='store_true', help='Initialize database')
    parser.add_argument('--force', action='store_true', help='Force recreate tables')
    parser.add_argument('--status', action='store_true', help='Check database status')
    parser.add_argument('--sample-data', action='store_true', help='Create sample data')
    parser.add_argument('--force-sample', action='store_true', help='Force recreate sample data (delete existing first)')
    parser.add_argument('--backup', type=str, nargs='?', const='', help='Backup database')
    
    args = parser.parse_args()
    
    if args.init:
        logger.info("Starting database initialization...")
        success = init_database(force_recreate=args.force)
        if success:
            logger.info("Database initialization completed successfully")
            sys.exit(0)
        else:
            logger.error("Database initialization failed")
            sys.exit(1)
    
    elif args.status:
        logger.info("Checking database status...")
        status = check_database_status()
        print(f"Database Status: {status}")
        sys.exit(0)
    
    elif args.sample_data or args.force_sample:
        logger.info("Creating sample data...")
        success = create_sample_data(force_recreate=args.force_sample)
        if success:
            logger.info("Sample data operation completed successfully")
            sys.exit(0)
        else:
            logger.error("Failed to create sample data")
            sys.exit(1)
    
    elif args.backup is not None:
        logger.info("Creating database backup...")
        backup_path = args.backup if args.backup else None
        success = backup_database(backup_path)
        if success:
            logger.info("Database backup completed successfully")
            sys.exit(0)
        else:
            logger.error("Database backup failed")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()