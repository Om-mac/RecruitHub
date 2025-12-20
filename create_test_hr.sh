#!/bin/bash
# Create test HR account for testing

cd "$(dirname "$0")" || exit 1
source .venv/bin/activate

python manage.py shell << END
from django.contrib.auth.models import User
from core.models import HRProfile

# Create or update test HR account
username = 'hr_admin'
email = 'hr@example.com'
password = 'hr123456'
first_name = 'HR'
last_name = 'Admin'

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'is_staff': True
    }
)

if created:
    user.set_password(password)
    user.save()
    print(f"Created new user: {username}")
else:
    user.set_password(password)
    user.save()
    print(f"Updated password for user: {username}")

# Create or update HR profile
hr_profile, created = HRProfile.objects.get_or_create(
    user=user,
    defaults={
        'company_name': 'Test Company',
        'designation': 'HR Manager',
        'department': 'Human Resources'
    }
)

if created:
    print(f"Created HR profile for: {user.username}")
else:
    print(f"HR profile already exists for: {user.username}")

print(f"\nTest HR Account Details:")
print(f"Username: {username}")
print(f"Password: {password}")
print(f"Email: {email}")
print(f"Login at: http://127.0.0.1:8000/hr/login/")
END
