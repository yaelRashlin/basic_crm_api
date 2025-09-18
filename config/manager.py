"""
Configuration Manager for User Management Flask Server

This module handles loading and managing configuration from YAML files
with support for environment-specific overrides.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Configuration manager class for loading and accessing configuration values.
    
    Supports loading from YAML files with environment-specific overrides
    and environment variable substitution.
    """
    
    def __init__(self, config_file: str = "config/settings.yaml", env: Optional[str] = None, verbose: bool = True):
        """
        Initialize configuration manager.
        
        Args:
            config_file (str): Path to main configuration file
            env (str, optional): Environment name (development, production, testing)
            verbose (bool): Whether to log configuration loading messages
        """
        self.config_file = config_file
        self.env = env or os.getenv('FLASK_ENV', 'development')
        self.verbose = verbose
        self.config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        messages = []
        
        try:
            # Load main configuration file
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                messages.append(f"Loaded configuration from {self.config_file}")
            else:
                messages.append(f"Configuration file {self.config_file} not found, using defaults")
                self.config = self._get_default_config()
            
            # Load environment-specific overrides
            env_config_file = f"config/{self.env}.yaml"
            if os.path.exists(env_config_file):
                with open(env_config_file, 'r', encoding='utf-8') as f:
                    env_config = yaml.safe_load(f) or {}
                self._merge_config(self.config, env_config)
                messages.append(f"Applied {self.env} environment overrides from {env_config_file}")
            
            # Apply environment variable overrides
            env_overrides = self._apply_env_overrides()
            if env_overrides:
                messages.append(f"Applied environment variable overrides: {', '.join(env_overrides)}")
            
            # Log all messages at once if verbose
            if self.verbose and messages:
                logger.info("Configuration loading: " + " | ".join(messages))
            
        except Exception as e:
            error_msg = f"Error loading configuration: {e}"
            fallback_msg = "Using default configuration"
            
            if self.verbose:
                logger.error(f"{error_msg} | {fallback_msg}")
            
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'server': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': True,
                'threaded': True
            },
            'app': {
                'name': 'User Management Flask Server',
                'version': '1.0.0',
                'description': 'A Flask server for user management'
            },
            'database': {
                'type': 'sqlite',
                'filename': 'users.db',
                'echo': False,
                'pool_size': 5,
                'max_overflow': 10,
                'connect_args': {
                    'check_same_thread': False
                }
            },
            'validation': {
                'israeli_id': {
                    'length': 9,
                    'checksum_enabled': True
                },
                'phone': {
                    'min_length': 8,
                    'max_length': 16,
                    'require_plus': True
                },
                'name': {
                    'max_length': 100,
                    'allow_empty': False
                },
                'address': {
                    'max_length': 200,
                    'allow_empty': False
                }
            },
            'logging': {
                'level': 'INFO',
                'enable_request_logging': True
            }
        }
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]):
        """
        Recursively merge configuration dictionaries.
        
        Args:
            base (dict): Base configuration
            override (dict): Override configuration
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        applied_overrides = []
        
        # Server configuration from environment variables
        if os.getenv('SERVER_HOST'):
            self.config.setdefault('server', {})['host'] = os.getenv('SERVER_HOST')
            applied_overrides.append('SERVER_HOST')
        
        if os.getenv('SERVER_PORT'):
            try:
                self.config.setdefault('server', {})['port'] = int(os.getenv('SERVER_PORT'))
                applied_overrides.append('SERVER_PORT')
            except ValueError:
                if self.verbose:
                    logger.warning(f"Invalid SERVER_PORT value: {os.getenv('SERVER_PORT')}")
        
        if os.getenv('DEBUG'):
            debug_value = os.getenv('DEBUG').lower() in ('true', '1', 'yes', 'on')
            self.config.setdefault('server', {})['debug'] = debug_value
            applied_overrides.append('DEBUG')
        
        # App configuration from environment variables
        if os.getenv('APP_NAME'):
            self.config.setdefault('app', {})['name'] = os.getenv('APP_NAME')
            applied_overrides.append('APP_NAME')
        
        if os.getenv('APP_VERSION'):
            self.config.setdefault('app', {})['version'] = os.getenv('APP_VERSION')
            applied_overrides.append('APP_VERSION')
        
        # Database configuration from environment variables
        if os.getenv('DATABASE_URL'):
            # Parse DATABASE_URL for different database types
            db_url = os.getenv('DATABASE_URL')
            if db_url.startswith('sqlite:///'):
                filename = db_url.replace('sqlite:///', '')
                self.config.setdefault('database', {})['filename'] = filename
                applied_overrides.append('DATABASE_URL')
        
        if os.getenv('DATABASE_FILENAME'):
            self.config.setdefault('database', {})['filename'] = os.getenv('DATABASE_FILENAME')
            applied_overrides.append('DATABASE_FILENAME')
        
        if os.getenv('DATABASE_ECHO'):
            echo_value = os.getenv('DATABASE_ECHO').lower() in ('true', '1', 'yes', 'on')
            self.config.setdefault('database', {})['echo'] = echo_value
            applied_overrides.append('DATABASE_ECHO')
        
        return applied_overrides
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path (str): Dot-separated key path (e.g., 'server.host')
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value or default
            
        Examples:
            >>> config.get('server.host')
            '0.0.0.0'
            >>> config.get('server.port')
            5000
            >>> config.get('nonexistent.key', 'default')
            'default'
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_server_config(self) -> Dict[str, Any]:
        """
        Get server configuration for Flask app.run().
        
        Returns:
            dict: Server configuration parameters
        """
        return {
            'host': self.get('server.host', '0.0.0.0'),
            'port': self.get('server.port', 5000),
            'debug': self.get('server.debug', True),
            'threaded': self.get('server.threaded', True)
        }
    
    def get_app_info(self) -> Dict[str, Any]:
        """
        Get application information.
        
        Returns:
            dict: Application information
        """
        return {
            'name': self.get('app.name', 'User Management Flask Server'),
            'version': self.get('app.version', '1.0.0'),
            'description': self.get('app.description', 'A Flask server for user management'),
            'environment': self.env
        }
    
    def get_validation_config(self) -> Dict[str, Any]:
        """
        Get validation configuration.
        
        Returns:
            dict: Validation configuration
        """
        return self.get('validation', {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """
        Get database configuration.
        
        Returns:
            dict: Database configuration
        """
        return self.get('database', {})
    
    def get_database_url(self) -> str:
        """
        Get database URL for SQLAlchemy.
        
        Returns:
            str: Database URL
        """
        db_config = self.get_database_config()
        db_type = db_config.get('type', 'sqlite')
        
        if db_type == 'sqlite':
            filename = db_config.get('filename', 'users.db')
            return f"sqlite:///{filename}"
        else:
            # Future support for other databases
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def get_database_engine_config(self) -> Dict[str, Any]:
        """
        Get database engine configuration for SQLAlchemy.
        
        Returns:
            dict: Engine configuration parameters
        """
        db_config = self.get_database_config()
        return {
            'echo': db_config.get('echo', False),
            'pool_size': db_config.get('pool_size', 5),
            'max_overflow': db_config.get('max_overflow', 10),
            'connect_args': db_config.get('connect_args', {})
        }
    
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get('server.debug', True)
    
    def should_show_endpoints(self) -> bool:
        """Check if endpoints should be shown on startup."""
        return self.get('development.show_endpoints_on_start', True)
    
    def reload_config(self):
        """Reload configuration from files."""
        self._load_config()
        if self.verbose:
            logger.info("Configuration reloaded")
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"ConfigManager(env={self.env}, file={self.config_file})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ConfigManager(env='{self.env}', config_file='{self.config_file}', loaded_keys={list(self.config.keys())})"


# Global configuration instance
config = ConfigManager(verbose=True)


def get_config() -> ConfigManager:
    """
    Get the global configuration instance.
    
    Returns:
        ConfigManager: Global configuration manager
    """
    return config


def reload_config():
    """Reload the global configuration."""
    global config
    config.reload_config()


# Convenience functions for common configuration values
def get_server_host() -> str:
    """Get server host from configuration."""
    return config.get('server.host', '0.0.0.0')


def get_server_port() -> int:
    """Get server port from configuration."""
    return config.get('server.port', 5000)


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return config.get('server.debug', True)


def get_app_version() -> str:
    """Get application version."""
    return config.get('app.version', '1.0.0')


def get_app_name() -> str:
    """Get application name."""
    return config.get('app.name', 'User Management Flask Server')


def get_database_url() -> str:
    """Get database URL from configuration."""
    return config.get_database_url()


def get_database_config() -> Dict[str, Any]:
    """Get database configuration."""
    return config.get_database_config()