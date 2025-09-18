"""
Database Migration System for User Management Flask Server

This module provides a simple migration system for database schema changes.
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any

# Add the parent directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from db.database import get_database_manager, get_user_repository
from db.models import Base, User
from sqlalchemy import text

logger = logging.getLogger(__name__)


class Migration:
    """
    Base class for database migrations.
    """
    
    def __init__(self, version: str, description: str):
        """
        Initialize migration.
        
        Args:
            version (str): Migration version (e.g., '001', '002')
            description (str): Migration description
        """
        self.version = version
        self.description = description
        self.timestamp = datetime.now()
    
    def up(self, db_manager):
        """
        Apply the migration.
        
        Args:
            db_manager: Database manager instance
        """
        raise NotImplementedError("Migration must implement up() method")
    
    def down(self, db_manager):
        """
        Rollback the migration.
        
        Args:
            db_manager: Database manager instance
        """
        raise NotImplementedError("Migration must implement down() method")
    
    def __str__(self):
        return f"Migration {self.version}: {self.description}"


class InitialMigration(Migration):
    """
    Initial migration to create all tables.
    """
    
    def __init__(self):
        super().__init__('001', 'Create initial tables')
    
    def up(self, db_manager):
        """Create all tables."""
        logger.info("Creating initial database tables")
        Base.metadata.create_all(db_manager.engine)
        logger.info("Initial tables created successfully")
    
    def down(self, db_manager):
        """Drop all tables."""
        logger.info("Dropping all database tables")
        Base.metadata.drop_all(db_manager.engine)
        logger.info("All tables dropped successfully")


class AddIndexesMigration(Migration):
    """
    Migration to add additional indexes for performance.
    """
    
    def __init__(self):
        super().__init__('002', 'Add performance indexes')
    
    def up(self, db_manager):
        """Add additional indexes."""
        logger.info("Adding performance indexes")
        
        with db_manager.session_scope() as session:
            # Add index on phone number for faster lookups
            session.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)"
            ))
            
            # Add composite index for name and created_at
            session.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_users_name_created ON users(name, created_at)"
            ))
        
        logger.info("Performance indexes added successfully")
    
    def down(self, db_manager):
        """Remove additional indexes."""
        logger.info("Removing performance indexes")
        
        with db_manager.session_scope() as session:
            session.execute(text("DROP INDEX IF EXISTS idx_users_phone"))
            session.execute(text("DROP INDEX IF EXISTS idx_users_name_created"))
        
        logger.info("Performance indexes removed successfully")


class MigrationManager:
    """
    Manages database migrations.
    """
    
    def __init__(self):
        """Initialize migration manager."""
        self.migrations = [
            InitialMigration(),
            AddIndexesMigration(),
        ]
        self.db_manager = get_database_manager()
    
    def _create_migration_table(self):
        """Create migration tracking table if it doesn't exist."""
        with self.db_manager.session_scope() as session:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS migrations (
                    version VARCHAR(10) PRIMARY KEY,
                    description TEXT NOT NULL,
                    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """))
    
    def _get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        try:
            with self.db_manager.session_scope() as session:
                result = session.execute(text("SELECT version FROM migrations ORDER BY version"))
                return [row[0] for row in result.fetchall()]
        except Exception:
            # Migration table doesn't exist yet
            return []
    
    def _mark_migration_applied(self, migration: Migration):
        """Mark migration as applied."""
        with self.db_manager.session_scope() as session:
            session.execute(text(
                "INSERT INTO migrations (version, description) VALUES (:version, :description)"
            ), {
                'version': migration.version,
                'description': migration.description
            })
    
    def _mark_migration_reverted(self, migration: Migration):
        """Mark migration as reverted."""
        with self.db_manager.session_scope() as session:
            session.execute(text(
                "DELETE FROM migrations WHERE version = :version"
            ), {'version': migration.version})
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations."""
        if not self.db_manager.initialize():
            raise Exception("Failed to initialize database")
        
        self._create_migration_table()
        applied = self._get_applied_migrations()
        
        return [m for m in self.migrations if m.version not in applied]
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        if not self.db_manager.initialize():
            raise Exception("Failed to initialize database")
        
        self._create_migration_table()
        return self._get_applied_migrations()
    
    def migrate(self, target_version: str = None) -> bool:
        """
        Apply migrations up to target version.
        
        Args:
            target_version (str): Target migration version (None for latest)
            
        Returns:
            bool: True if successful
        """
        try:
            pending = self.get_pending_migrations()
            
            if not pending:
                logger.info("No pending migrations")
                return True
            
            # Filter migrations up to target version
            if target_version:
                pending = [m for m in pending if m.version <= target_version]
            
            logger.info(f"Applying {len(pending)} migrations")
            
            for migration in pending:
                logger.info(f"Applying {migration}")
                migration.up(self.db_manager)
                self._mark_migration_applied(migration)
                logger.info(f"Applied {migration}")
            
            logger.info("All migrations applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def rollback(self, target_version: str = None) -> bool:
        """
        Rollback migrations to target version.
        
        Args:
            target_version (str): Target migration version (None for all)
            
        Returns:
            bool: True if successful
        """
        try:
            applied = self.get_applied_migrations()
            
            if not applied:
                logger.info("No migrations to rollback")
                return True
            
            # Get migrations to rollback (in reverse order)
            to_rollback = []
            for migration in reversed(self.migrations):
                if migration.version in applied:
                    to_rollback.append(migration)
                    if target_version and migration.version == target_version:
                        break
            
            logger.info(f"Rolling back {len(to_rollback)} migrations")
            
            for migration in to_rollback:
                logger.info(f"Rolling back {migration}")
                migration.down(self.db_manager)
                self._mark_migration_reverted(migration)
                logger.info(f"Rolled back {migration}")
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def status(self) -> Dict[str, Any]:
        """
        Get migration status.
        
        Returns:
            dict: Migration status information
        """
        try:
            applied = self.get_applied_migrations()
            pending = self.get_pending_migrations()
            
            return {
                'total_migrations': len(self.migrations),
                'applied_count': len(applied),
                'pending_count': len(pending),
                'applied_versions': applied,
                'pending_versions': [m.version for m in pending],
                'latest_version': self.migrations[-1].version if self.migrations else None,
                'current_version': applied[-1] if applied else None
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }


def main():
    """Main function for command-line migration management."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration management')
    parser.add_argument('--migrate', action='store_true', help='Apply pending migrations')
    parser.add_argument('--rollback', type=str, nargs='?', const='', help='Rollback migrations')
    parser.add_argument('--status', action='store_true', help='Show migration status')
    parser.add_argument('--target', type=str, help='Target migration version')
    
    args = parser.parse_args()
    
    migration_manager = MigrationManager()
    
    if args.migrate:
        logger.info("Starting database migration...")
        success = migration_manager.migrate(args.target)
        if success:
            logger.info("Migration completed successfully")
        else:
            logger.error("Migration failed")
            exit(1)
    
    elif args.rollback is not None:
        target = args.rollback if args.rollback else args.target
        logger.info(f"Starting database rollback to version: {target or 'initial'}")
        success = migration_manager.rollback(target)
        if success:
            logger.info("Rollback completed successfully")
        else:
            logger.error("Rollback failed")
            exit(1)
    
    elif args.status:
        status = migration_manager.status()
        print("Migration Status:")
        print(f"  Total migrations: {status.get('total_migrations', 0)}")
        print(f"  Applied: {status.get('applied_count', 0)}")
        print(f"  Pending: {status.get('pending_count', 0)}")
        print(f"  Current version: {status.get('current_version', 'None')}")
        print(f"  Latest version: {status.get('latest_version', 'None')}")
        
        if status.get('applied_versions'):
            print(f"  Applied versions: {', '.join(status['applied_versions'])}")
        
        if status.get('pending_versions'):
            print(f"  Pending versions: {', '.join(status['pending_versions'])}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()