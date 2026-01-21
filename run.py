"""
Application Entry Point

This script runs the Flask development server.
For production, use gunicorn_setup.py instead.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
