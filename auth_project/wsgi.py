"""
WSGI config for auth_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
import time
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_project.settings")

# Initialize Django
application = get_wsgi_application()

# Run database initialization on first load
print("=" * 70)
print("WSGI INIT: Initializing database on application startup...")
print("=" * 70)

try:
    # Wait for database to be ready
    print("\nWaiting for database connection...")
    max_retries = 30
    for attempt in range(max_retries):
        try:
            connection.ensure_connection()
            print("✓ Database connection successful!")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⏳ Attempt {attempt + 1}/{max_retries}: Waiting for database...")
                time.sleep(2)
            else:
                print(f"✗ Database failed to connect")
                raise
    
    # Run migrations
    print("\nRunning migrations...")
    call_command('migrate', verbosity=0, interactive=False)
    print("✓ Migrations completed")
    
    # Create default data
    print("Creating default data...")
    call_command('init_db', verbosity=0)
    
    print("\n" + "=" * 70)
    print("✅ Database initialization successful!")
    print("=" * 70 + "\n")
    
except Exception as e:
    print("\n" + "=" * 70)
    print(f"⚠️ Database initialization error: {str(e)}")
    print("=" * 70)
    import traceback
    traceback.print_exc()
    print("\n✓ App will continue running (may have limited functionality)\n")

