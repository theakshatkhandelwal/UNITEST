#!/usr/bin/env python3
"""
Test Neon DB Connection Script
Tests the connection to your Neon PostgreSQL database
"""

import os
import sys
from sqlalchemy import create_engine, text

# Your Neon DB connection string
DATABASE_URL = 'postgresql://neondb_owner:npg_dyFJ5zZ0fWPj@ep-green-glade-a4x5w9dj-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

def test_connection():
    """Test the database connection"""
    print("Testing Neon DB Connection...")
    print(f"Database URL: {DATABASE_URL[:50]}...")
    print()
    
    try:
        # Create engine
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={
                'sslmode': 'require',
                'connect_timeout': 10
            }
        )
        
        # Test connection
        with engine.connect() as conn:
            # Execute a simple query
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"[OK] Connection successful!")
            print(f"PostgreSQL Version: {version}")
            print()
            
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"Existing tables ({len(tables)}):")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("No tables found (database is empty)")
            print()
            
            # Test write capability
            conn.execute(text("SELECT 1;"))
            print("[OK] Write test successful")
            
        return True
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {str(e)}")
        print()
        print("Common issues:")
        print("1. Check if your Neon project is active (not paused)")
        print("2. Verify the connection string is correct")
        print("3. Ensure SSL is enabled (sslmode=require)")
        print("4. Check if IP restrictions are blocking your connection")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Neon DB Connection Test")
    print("=" * 60)
    print()
    
    success = test_connection()
    
    print()
    print("=" * 60)
    if success:
        print("[SUCCESS] All tests passed! Your database is ready.")
    else:
        print("[ERROR] Connection test failed. Please check the errors above.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

