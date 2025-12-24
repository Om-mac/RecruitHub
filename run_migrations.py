#!/usr/bin/env python
"""
Run Django migrations on startup
This script is called by Procfile to ensure migrations are applied before the app starts
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

# Run migrations
from django.core.management import call_command

print("=" * 70)
print("Running Django migrations...")
print("=" * 70)

try:
    call_command('migrate', verbosity=2)
    print("=" * 70)
    print("✅ Migrations completed successfully!")
    print("=" * 70)
except Exception as e:
    print("=" * 70)
    print(f"❌ Migration failed: {e}")
    print("=" * 70)
    sys.exit(1)
