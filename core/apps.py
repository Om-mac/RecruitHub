from django.apps import AppConfig
import os


class CoreConfig(AppConfig):
    name = "core"
    
    def ready(self):
        """Create superuser on app startup if not exists"""
        try:
            from django.contrib.auth.models import User
            
            username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@vakverse.com')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
            
            if password and not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username, email, password)
                print(f'✓ Superuser "{username}" created automatically on app startup')
        except Exception as e:
            print(f'Note: Could not auto-create superuser: {str(e)}')
