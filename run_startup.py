#!/usr/bin/env python
"""
Startup script that ensures database is initialized before app starts
"""
import os
import sys
import time
import django
from django.core.management import call_command
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

print("=" * 70)
print("STARTUP: Initializing application...")
print("=" * 70)

# Check database configuration
db_engine = connection.settings_dict.get('ENGINE', 'unknown')
db_name = connection.settings_dict.get('NAME', 'unknown')
print(f"\nDatabase Engine: {db_engine}")
print(f"Database Name: {db_name}")
print(f"DATABASE_URL set: {'DATABASE_URL' in os.environ}")

# Wait for database to be ready (with retries for PostgreSQL startup)
print("\nWaiting for database to be ready...")
max_retries = 30
for attempt in range(max_retries):
    try:
        connection.ensure_connection()
        print("✓ Database connection successful!")
        break
    except Exception as e:
        if attempt < max_retries - 1:
            wait_time = 2
            print(f"⏳ Attempt {attempt + 1}/{max_retries}: Database not ready, waiting {wait_time}s...")
            time.sleep(wait_time)
        else:
            print(f"✗ Database failed to connect after {max_retries} attempts")
            print(f"Error: {str(e)}")
            sys.exit(1)

# Run migrations and initialize data
print("\n" + "=" * 70)
print("STARTUP: Running database initialization...")
print("=" * 70)

try:
    # Step 1: Run migrations
    print("\n[1/3] Running migrations...")
    call_command('migrate', verbosity=2)
    print("✓ Migrations completed")
    
    # Step 2: Create default data
    print("\n[2/3] Creating default data...")
    call_command('init_db', verbosity=2)
    
    # Step 3: Create superuser from environment variables (one-time setup)
    print("\n[3/3] Setting up superuser from environment variables...")
    django_username = os.getenv('DJANGO_SUPERUSER_USERNAME')
    django_password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
    django_email = os.getenv('DJANGO_SUPERUSER_EMAIL')
    
    if django_username and django_password and django_email:
        try:
            call_command('create_superuser_from_env', verbosity=2)
            print("✓ Superuser setup completed")
        except Exception as e:
            print(f"⚠️ Superuser setup error: {str(e)}")
            # Continue anyway - superuser might already exist
    else:
        print("⚠️ Superuser environment variables not set")
        print("   (DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_EMAIL)")
        print("   Skipping superuser creation. Set them later with: python manage.py create_superuser_from_env")
    
    print("\n" + "=" * 70)
    print("✅ Database initialization successful!")
    print("=" * 70 + "\n")
    
except Exception as e:
    print("\n" + "=" * 70)
    print(f"⚠️ Database initialization error: {str(e)}")
    print("=" * 70 + "\n")
    import traceback
    traceback.print_exc()
    # Continue anyway - app might work with partial setup
    sys.exit(1)
