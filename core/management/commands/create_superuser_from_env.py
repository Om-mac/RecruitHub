"""
Management command to create superuser from environment variables (one-time setup)
Usage: python manage.py createsuperuser --noinput

This uses Django's official environment variables:
- DJANGO_SUPERUSER_USERNAME
- DJANGO_SUPERUSER_PASSWORD
- DJANGO_SUPERUSER_EMAIL

After creation, Django uses normal database authentication - no env vars needed.
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create or update Django superuser from environment variables (one-time setup)'

    def handle(self, *args, **options):
        """Create superuser from Django's official environment variables"""
        
        # Read from environment variables (Django's official variables)
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        
        # Validate environment variables
        if not username:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️ DJANGO_SUPERUSER_USERNAME environment variable not set'
                )
            )
            return
        
        if not password:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️ DJANGO_SUPERUSER_PASSWORD environment variable not set'
                )
            )
            return
        
        if not email:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️ DJANGO_SUPERUSER_EMAIL environment variable not set'
                )
            )
            return
        
        # Check if superuser already exists
        try:
            user = User.objects.get(username=username)
            # Update existing user
            user.email = email
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Updated superuser: {username}'
                )
            )
        except User.DoesNotExist:
            # Create new superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Created superuser: {username}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n' + '='*60
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '✅ Superuser setup complete!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '   From now on, Django will authenticate using the database.'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '   Environment variables are NOT used for login anymore.'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '='*60
            )
        )
