"""
Gunicorn configuration and application setup for production deployment.
"""
import multiprocessing
from app import create_app

# Gunicorn configuration
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 30
keepalive = 2

# Application
app = create_app()

if __name__ == "__main__":
    from gunicorn.app.base import BaseApplication
    
    class StandaloneApplication(BaseApplication):
        """
        Standalone Gunicorn application for running Flask app.
        """
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()
        
        def load_config(self):
            """Load configuration from options dictionary."""
            for key, value in self.options.items():
                if key in self.cfg.settings and value is not None:
                    self.cfg.set(key.lower(), value)
        
        def load(self):
            """Return the application instance."""
            return self.application
    
    options = {
        'bind': bind,
        'workers': workers,
        'worker_class': worker_class,
        'timeout': timeout,
        'keepalive': keepalive,
    }
    
    StandaloneApplication(app, options).run()
