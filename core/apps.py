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
            
            username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@vakverse.com')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
            
            if password:
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
                else:
                    # Update password if user exists
                    if user.password != password:
                        user.set_password(password)
                        user.save()
        except Exception as e:
            pass
