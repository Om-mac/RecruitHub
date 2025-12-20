from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User
from core.models import HRProfile

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
            self.stdout.write(self.style.ERROR(f'✗ Migration failed: {str(e)}'))
            import traceback
            traceback.print_exc()
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
        
        # Step 3: Create HR user if doesn't exist
        try:
            if not User.objects.filter(username='hr').exists():
                user = User.objects.create_user(
                    username='hr',
                    email='hr@example.com',
                    password='HRPassword123!',
                    first_name='HR',
                    last_name='Admin'
                )
                
                HRProfile.objects.create(
                    user=user,
                    company_name='RecruitHub',
                    designation='HR Manager',
                    department='Human Resources'
                )
                
                self.stdout.write(self.style.SUCCESS('✓ Created HR user: hr@example.com'))
            else:
                self.stdout.write(self.style.SUCCESS('✓ HR user already exists'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to create HR user: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS('\n✅ Database initialization complete!'))
