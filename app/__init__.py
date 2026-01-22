"""
BJJ School Website Application Factory

This module implements the Flask application factory pattern,
initializing all extensions and registering blueprints.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_login import LoginManager
import yaml
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Initialize extensions
db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_path='config.yaml'):
    """
    Application factory function.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        Flask application instance
        
    Raises:
        SystemExit: If configuration is invalid or missing
    """
    # Load configuration
    from app.config_loader import ConfigLoader
    
    try:
        config_loader = ConfigLoader(config_path)
        config = config_loader.load()
    except (FileNotFoundError, ValueError, yaml.YAMLError) as e:
        print(f"FATAL: Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Configure Flask from loaded config
    app.config['SECRET_KEY'] = config['flask']['secret_key']
    app.config['DEBUG'] = config['flask'].get('debug', False)
    
    # Configure SQLAlchemy
    db_config = config['database']
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['name']}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure session security
    security_config = config['security']
    if config['environment'] == 'production':
        app.config['SESSION_COOKIE_SECURE'] = security_config.get('session_cookie_secure', True)
    app.config['SESSION_COOKIE_HTTPONLY'] = security_config.get('session_cookie_httponly', True)
    
    # Configure CSRF protection
    app.config['WTF_CSRF_ENABLED'] = security_config.get('csrf_enabled', True)
    
    # Initialize extensions with app
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to login page if not authenticated
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Configure session timeout (30 minutes)
    from datetime import timedelta
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    
    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """
        Load user by ID for Flask-Login.
        
        Args:
            user_id: User ID from session
            
        Returns:
            User object or None if not found
        """
        from app.models import User
        return User.query.get(int(user_id))
    
    # Store Instagram config for later use
    app.config['INSTAGRAM_ACCESS_TOKEN'] = config['instagram']['access_token']
    app.config['INSTAGRAM_USER_ID'] = config['instagram']['user_id']
    app.config['INSTAGRAM_REFRESH_INTERVAL'] = config['instagram'].get('refresh_interval', 3600)
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.contact import contact_bp
    from app.routes.booking import booking_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    # Register error handlers
    from app.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Register context processors
    register_context_processors(app)
    
    return app


def register_context_processors(app):
    """
    Register context processors to make variables available to all templates.
    
    Args:
        app: Flask application instance
    """
    @app.context_processor
    def inject_site_settings():
        """
        Inject site settings into all templates.
        
        Returns:
            Dictionary with site settings (banner_url, logo_url, site_name)
        """
        from flask import url_for
        from app.models import SiteSettings
        
        site_settings = {
            'banner_url': None,
            'logo_url': None,
            'site_name': 'BJJ SCHOOL'
        }
        
        # Query SiteSettings model from database
        settings = SiteSettings.query.get(1)
        if settings:
            if settings.banner_image_path:
                site_settings['banner_url'] = url_for('static', filename=settings.banner_image_path)
            if settings.logo_image_path:
                site_settings['logo_url'] = url_for('static', filename=settings.logo_image_path)
        
        return site_settings


def configure_logging(app):
    """
    Configure application logging.
    
    Args:
        app: Flask application instance
    """
    # Set log level based on environment
    if app.config['DEBUG']:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Configure file handler with rotation
    file_handler = RotatingFileHandler(
        'logs/bjj_school.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    
    # Set log format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Add handler to app logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    
    # Also configure root logger for error_handlers module
    logging.basicConfig(
        level=log_level,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        handlers=[file_handler]
    )
    
    app.logger.info('BJJ School Website startup')
