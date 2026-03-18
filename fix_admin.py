#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

username = 'omtapdiya'
password = 'RZd/148*488+GZraffe-'
email = 'omtapdiya75@gmail.com'

try:
    user = User.objects.get(username=username)
    print(f"👤 User Found: {username}")
    print(f"   is_staff: {user.is_staff}")
    print(f"   is_superuser: {user.is_superuser}")
    print(f"   is_active: {user.is_active}")
    print(f"   email: {user.email}")
    
    # Ensure all flags are correct
    changed = False
    if not user.is_staff:
        user.is_staff = True
        changed = True
        print(f"\n✅ Set is_staff = True")
    
    if not user.is_superuser:
        user.is_superuser = True
        changed = True
        print(f"✅ Set is_superuser = True")
    
    if not user.is_active:
        user.is_active = True
        changed = True
        print(f"✅ Set is_active = True")
    
    # Reset password
    user.set_password(password)
    user.save()
    
    print(f"\n✅ Admin account reconfigured successfully")
    
    # Verify password works
    auth_user = authenticate(username=username, password=password)
    if auth_user:
        print(f"✅ Password verification: SUCCESS")
        print(f"\n🔐 Admin Login Details:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {email}")
        print(f"\n🔗 Admin URL: http://localhost:8000/admin/")
    else:
        print(f"❌ Password verification: FAILED")
        
except User.DoesNotExist:
    print(f"❌ User '{username}' not found! Creating now...")
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"✅ Admin user created: {username}")
    print(f"\n🔐 Admin Login Details:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Email: {email}")
    print(f"\n🔗 Admin URL: http://localhost:8000/admin/")
