"""
Unit Tests for ConfigLoader

Tests the configuration loading and validation functionality.
"""

import pytest
import yaml
import os
import tempfile
from app.config_loader import ConfigLoader


class TestConfigLoader:
    """Test suite for ConfigLoader class"""
    
    @pytest.fixture
    def valid_config(self):
        """Fixture providing a valid configuration dictionary"""
        return {
            'environment': 'development',
            'database': {
                'host': 'localhost',
                'port': 3306,
                'name': 'bjj_school',
                'user': 'test_user',
                'password': 'test_password',
            },
            'flask': {
                'secret_key': 'test_secret_key_at_least_16_chars',
                'debug': True,
            },
            'instagram': {
                'access_token': 'test_access_token',
                'user_id': 'test_user_id',
                'refresh_interval': 3600,
            },
            'security': {
                'csrf_enabled': True,
                'session_cookie_secure': False,
                'session_cookie_httponly': True,
            }
        }
    
    @pytest.fixture
    def temp_config_file(self, valid_config):
        """Fixture that creates a temporary config file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_load_valid_configuration(self, temp_config_file, valid_config):
        """Test loading a valid YAML configuration file"""
        loader = ConfigLoader(temp_config_file)
        config = loader.load()
        
        assert config == valid_config
        assert config['environment'] == 'development'
        assert config['database']['host'] == 'localhost'
        assert config['flask']['secret_key'] == 'test_secret_key_at_least_16_chars'
    
    def test_missing_configuration_file(self):
        """Test handling of missing configuration file"""
        loader = ConfigLoader('nonexistent_config.yaml')
        
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load()
        
        assert 'Configuration file not found' in str(exc_info.value)
    
    def test_invalid_yaml_syntax(self):
        """Test handling of invalid YAML syntax"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: syntax:\n  - broken\n  indentation")
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            
            with pytest.raises(yaml.YAMLError) as exc_info:
                loader.load()
            
            assert 'Invalid YAML syntax' in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_empty_configuration_file(self):
        """Test handling of empty configuration file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            assert 'Configuration file is empty' in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_validation_missing_required_field(self, valid_config):
        """Test validation fails when required field is missing"""
        # Remove a required field
        del valid_config['database']['host']
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            assert 'Missing required configuration field' in str(exc_info.value)
            assert 'database.host' in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_validation_invalid_field_type(self, valid_config):
        """Test validation fails when field has wrong type"""
        # Change port to string instead of int
        valid_config['database']['port'] = "3306"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            assert 'invalid type' in str(exc_info.value).lower()
            assert 'database.port' in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_validation_invalid_environment(self, valid_config):
        """Test validation fails for invalid environment value"""
        valid_config['environment'] = 'staging'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            assert 'Invalid environment' in str(exc_info.value)
            assert 'development' in str(exc_info.value)
            assert 'production' in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_validation_invalid_port_range(self, valid_config):
        """Test validation fails for invalid port number"""
        valid_config['database']['port'] = 99999
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            assert 'Invalid database port' in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_validation_short_secret_key(self, valid_config):
        """Test validation fails for secret key that's too short"""
        valid_config['flask']['secret_key'] = 'short'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            assert 'secret_key must be at least 16 characters' in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_validation_low_refresh_interval(self, valid_config):
        """Test validation fails for refresh interval below minimum"""
        valid_config['instagram']['refresh_interval'] = 30
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            assert 'Invalid Instagram refresh_interval' in str(exc_info.value)
            assert 'at least 60 seconds' in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_validation_nested_dict_not_dict(self, valid_config):
        """Test validation fails when nested dict field is not a dict"""
        valid_config['database'] = 'not_a_dict'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load()
            
            assert 'database' in str(exc_info.value)
            assert 'must be a dictionary' in str(exc_info.value)
        finally:
            os.unlink(temp_path)
    
    def test_production_environment_valid(self, valid_config):
        """Test that production environment is accepted"""
        valid_config['environment'] = 'production'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            config = loader.load()
            
            assert config['environment'] == 'production'
        finally:
            os.unlink(temp_path)
