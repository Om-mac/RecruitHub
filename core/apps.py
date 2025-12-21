from django.apps import AppConfig
import os


class CoreConfig(AppConfig):
    name = "core"
    
    def ready(self):
        """Create superuser on app startup if not exists"""
        # Skip in production or during migrations to avoid RuntimeWarning
        import sys
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
        
        try:
            from django.contrib.auth.models import User
            from django.db import connection
            
            # Only run if database is ready
            if connection.connection is not None:
                username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
                email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@vakverse.com')
                password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
                
                if password and not User.objects.filter(username=username).exists():
                    User.objects.create_superuser(username, email, password)
                    print(f'✓ Superuser "{username}" created automatically on app startup')
        except Exception as e:
            # Silently ignore - database might not be ready yet
            pass
