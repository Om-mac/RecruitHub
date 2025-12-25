"""
Management command to create superuser from environment variables (one-time setup)
Usage: python manage.py create_superuser_from_env

This command:
1. Reads ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL from environment variables
2. Creates or updates the superuser in the database
3. After this, Django uses normal database authentication - no env vars needed
"""

import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create or update Django superuser from environment variables (one-time setup)'

    def handle(self, *args, **options):
        """Create superuser from environment variables"""
        
        # Read from environment variables
        username = os.getenv('ADMIN_USERNAME')
        password = os.getenv('ADMIN_PASSWORD')
        email = os.getenv('ADMIN_EMAIL')
        
        # Validate environment variables
        if not username:
            raise CommandError('❌ ADMIN_USERNAME environment variable not set')
        if not password:
            raise CommandError('❌ ADMIN_PASSWORD environment variable not set')
        if not email:
            raise CommandError('❌ ADMIN_EMAIL environment variable not set')
        
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
