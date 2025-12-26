from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os
import sys

class Command(BaseCommand):
    help = 'Create a superuser from environment variables'

    def handle(self, *args, **options):
        try:
            username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
            
            # Security: Don't log credential details
            if not username or not email:
                self.stdout.write(
                    self.style.WARNING('DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_EMAIL not set. Skipping.')
                )
                return
            
            if not password:
                self.stdout.write(
                    self.style.WARNING('DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser creation.')
                )
                return
            
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'Superuser "{username}" already exists. Skipping.')
                )
                return
            
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Successfully created superuser "{username}"')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating superuser: {str(e)}')
            )
            sys.exit(1)
