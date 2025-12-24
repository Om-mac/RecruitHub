#!/usr/bin/env python
"""
Cleanup script to remove UserProfiles from admin/staff/superuser accounts
Run this once to clean up existing stale profiles
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile

# Find and delete UserProfiles for staff/superuser accounts
admin_users = User.objects.filter(is_staff=True) | User.objects.filter(is_superuser=True)
deleted_count = 0

for user in admin_users:
    if hasattr(user, 'profile'):
        print(f"❌ Deleting UserProfile for admin user: {user.username}")
        user.profile.delete()
        deleted_count += 1

print(f"\n✅ Cleanup complete! Deleted {deleted_count} stale profiles.")
