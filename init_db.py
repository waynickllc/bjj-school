"""
Database Initialization Script

This script initializes the database schema for the BJJ School Website.
It creates the necessary tables for ContactSubmission and TrialBooking models.

Usage:
    python init_db.py

Requirements:
    - MySQL server must be running
    - Database specified in config.yaml must exist
    - User specified in config.yaml must have appropriate permissions
"""

import sys
from app import create_app, db
from app.models import ContactSubmission, TrialBooking


def init_database():
    """
    Initialize the database schema.
    
    Creates all tables defined in the SQLAlchemy models.
    """
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("✓ Database tables created successfully!")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\nCreated tables: {', '.join(tables)}")
            
            # Display table information
            print("\n" + "="*60)
            print("Table: contact_submissions")
            print("="*60)
            for column in inspector.get_columns('contact_submissions'):
                print(f"  - {column['name']}: {column['type']}")
            
            print("\n" + "="*60)
            print("Table: trial_bookings")
            print("="*60)
            for column in inspector.get_columns('trial_bookings'):
                print(f"  - {column['name']}: {column['type']}")
            
            print("\n✓ Database initialization complete!")
            
        except Exception as e:
            print(f"✗ Error initializing database: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    init_database()
