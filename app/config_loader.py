"""
Configuration Loader Module

This module provides the ConfigLoader class for loading and validating
YAML configuration files.
"""

import yaml
import os
from typing import Dict, Any


class ConfigLoader:
    """
    Loads and validates YAML configuration files.
    
    Attributes:
        config_path: Path to the YAML configuration file
    """
    
    REQUIRED_FIELDS = {
        'environment': str,
        'database': {
            'host': str,
            'port': int,
            'name': str,
            'user': str,
            'password': str,
        },
        'flask': {
            'secret_key': str,
            'debug': bool,
        },
        'instagram': {
            'access_token': str,
            'user_id': str,
            'refresh_interval': int,
        },
        'security': {
            'csrf_enabled': bool,
            'session_cookie_secure': bool,
            'session_cookie_httponly': bool,
        }
    }
    
    def __init__(self, config_path: str):
        """
        Initialize ConfigLoader with path to configuration file.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
    
    def load(self) -> Dict[str, Any]:
        """
        Load and parse YAML configuration file.
        
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file has invalid YAML syntax
            ValueError: If required fields are missing or invalid
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML syntax in {self.config_path}: {e}")
        
        if config is None:
            raise ValueError(f"Configuration file is empty: {self.config_path}")
        
        # Validate configuration
        self.validate(config)
        
        return config
    
    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validate required configuration fields.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If required fields are missing or have invalid types
        """
        self._validate_fields(config, self.REQUIRED_FIELDS, path='')
        
        # Additional validation rules
        if config['environment'] not in ['development', 'production']:
            raise ValueError(
                f"Invalid environment: {config['environment']}. "
                "Must be 'development' or 'production'"
            )
        
        if config['database']['port'] < 1 or config['database']['port'] > 65535:
            raise ValueError(
                f"Invalid database port: {config['database']['port']}. "
                "Must be between 1 and 65535"
            )
        
        if config['instagram']['refresh_interval'] < 60:
            raise ValueError(
                f"Invalid Instagram refresh_interval: {config['instagram']['refresh_interval']}. "
                "Must be at least 60 seconds"
            )
        
        if len(config['flask']['secret_key']) < 16:
            raise ValueError(
                "Flask secret_key must be at least 16 characters long"
            )
        
        return True
    
    def _validate_fields(self, config: Dict[str, Any], required: Dict[str, Any], path: str):
        """
        Recursively validate configuration fields.
        
        Args:
            config: Configuration dictionary to validate
            required: Required fields specification
            path: Current path in configuration (for error messages)
            
        Raises:
            ValueError: If required fields are missing or have invalid types
        """
        for key, expected_type in required.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check if field exists
            if key not in config:
                raise ValueError(f"Missing required configuration field: {current_path}")
            
            value = config[key]
            
            # If expected_type is a dict, recursively validate nested fields
            if isinstance(expected_type, dict):
                if not isinstance(value, dict):
                    raise ValueError(
                        f"Configuration field {current_path} must be a dictionary"
                    )
                self._validate_fields(value, expected_type, current_path)
            else:
                # Validate type
                if not isinstance(value, expected_type):
                    raise ValueError(
                        f"Configuration field {current_path} has invalid type. "
                        f"Expected {expected_type.__name__}, got {type(value).__name__}"
                    )
