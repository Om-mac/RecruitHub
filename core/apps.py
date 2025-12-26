from django.apps import AppConfig
import os


class CoreConfig(AppConfig):
    name = "core"
    
    def ready(self):
        """Create superuser on app startup if not exists"""
        import sys
        
        # Skip during migrations
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
        
        try:
            from django.db import connection
            from django.contrib.auth.models import User
            
            # Check if database is accessible
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # Security: Require explicit env vars (no hardcoded fallbacks)
            username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
            
            # Only create if ALL env vars are set
            if username and email and password:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'is_staff': True,
                        'is_superuser': True,
                        'is_active': True
                    }
                )
                if created:
                    user.set_password(password)
                    user.save()
                    print(f'✓ Superuser "{username}" created on startup')
                # Security: Don't update password on existing users
        except Exception:
            # Silently fail - app will continue running
            pass
