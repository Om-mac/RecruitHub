from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Initialize database - run migrations and create default data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database initialization...'))
        
        # Step 1: Run migrations with explicit output
        try:
            self.stdout.write(self.style.WARNING('>>> Running migrations...'))
            call_command('migrate', verbosity=2, interactive=False)
            self.stdout.write(self.style.SUCCESS('✓ Migrations completed successfully'))
        except Exception as e:
            # Security: Don't print full traceback (leaks internal paths)
            self.stdout.write(self.style.ERROR(f'✗ Migration failed: {type(e).__name__}'))
            return
        
        # Step 2: Check if tables exist (for both PostgreSQL and SQLite)
        try:
            db_engine = connection.settings_dict['ENGINE']
            tables_exist = False
            
            if 'postgresql' in db_engine:
                # PostgreSQL check
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'auth_user'
                        )
                    """)
                    tables_exist = cursor.fetchone()[0]
            else:
                # SQLite check
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='auth_user'
                    """)
                    tables_exist = cursor.fetchone() is not None
            
            if not tables_exist:
                self.stdout.write(self.style.WARNING('⚠ Tables still missing - retrying migrations'))
                call_command('migrate', verbosity=1)
                self.stdout.write(self.style.SUCCESS('✓ Migrations completed on retry'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠ Could not verify tables: {str(e)}'))
        
        # Step 3: Create superuser from environment variables
        try:
            import os
            username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
            
            if username and email and password:
                if not User.objects.filter(username=username).exists():
                    User.objects.create_superuser(username, email, password)
                    self.stdout.write(self.style.SUCCESS(f'✓ Created superuser: {username}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'✓ Superuser already exists: {username}'))
            else:
                self.stdout.write(self.style.WARNING('⚠ Superuser environment variables not set'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to create superuser: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Database initialization complete!'))
