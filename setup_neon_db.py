#!/usr/bin/env python3
"""
Initialize Neon DB Tables
Creates all required tables for Unitest application
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

# Your Neon DB connection string
DATABASE_URL = 'postgresql://neondb_owner:npg_dyFJ5zZ0fWPj@ep-green-glade-a4x5w9dj-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

def initialize_database():
    """Initialize all database tables"""
    print("Initializing Neon Database...")
    print()
    
    # Set the database URL
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    
    try:
        with app.app_context():
            # Create all tables
            print("Creating tables...")
            db.create_all()
            print("[OK] Tables created successfully!")
            print()
            
            # Verify tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"Created tables ({len(tables)}):")
            for table in sorted(tables):
                print(f"   [OK] {table}")
            
            print()
            print("[OK] Database initialization complete!")
            return True
            
    except Exception as e:
        print(f"[ERROR] Error initializing database: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Neon DB Initialization")
    print("=" * 60)
    print()
    
    success = initialize_database()
    
    print()
    print("=" * 60)
    if success:
        print("[SUCCESS] Database is ready for use!")
    else:
        print("[ERROR] Initialization failed. Please check the errors above.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

