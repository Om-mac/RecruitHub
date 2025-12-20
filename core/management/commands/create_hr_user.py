from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import HRProfile

class Command(BaseCommand):
    help = 'Create default HR user for testing'

    def handle(self, *args, **options):
        # Create HR user if doesn't exist
        if not User.objects.filter(username='hr').exists():
            user = User.objects.create_user(
                username='hr',
                email='hr@example.com',
                password='HRPassword123!',
                first_name='HR',
                last_name='Admin'
            )
            
            # Create HR Profile
            HRProfile.objects.create(
                user=user,
                company_name='RecruitHub',
                designation='HR Manager',
                department='Human Resources'
            )
            
            self.stdout.write(
                self.style.SUCCESS('Successfully created HR user: hr@example.com')
            )
        else:
            self.stdout.write(
                self.style.WARNING('HR user already exists')
            )
