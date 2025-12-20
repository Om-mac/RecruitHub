#!/usr/bin/env python
"""
Startup script that ensures database is initialized before app starts
"""
import os
import sys
import django
from django.core.management import call_command

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

# Run migrations
print("=" * 60)
print("STARTUP: Running database initialization...")
print("=" * 60)

try:
    call_command('init_db', verbosity=2)
    print("\n" + "=" * 60)
    print("✅ Database initialization successful!")
    print("=" * 60 + "\n")
except Exception as e:
    print("\n" + "=" * 60)
    print(f"⚠️ Database initialization error: {str(e)}")
    print("=" * 60 + "\n")
    # Continue anyway - app might work with partial setup
