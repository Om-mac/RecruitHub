from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile
from datetime import datetime
import random

try:
    from faker import Faker
except ImportError:
    Faker = None


class Command(BaseCommand):
    help = 'Create 50 fake users with realistic data'

    def handle(self, *args, **kwargs):
        if Faker is None:
            self.stdout.write(
                self.style.ERROR(
                    'faker library is not installed. Run: pip install faker'
                )
            )
            return

        fake = Faker()
        created_count = 0

        # Define branches
        branches = ['CSE', 'ECE', 'Mechanical', 'Civil', 'EEE', 'IT', 'Production']
        years = ['1', '2', '3', '4']
        genders = ['M', 'F', 'O']
        skills_list = [
            'Python, Java, JavaScript',
            'Python, Django, React',
            'Java, Spring Boot, MySQL',
            'JavaScript, Node.js, MongoDB',
            'C++, Data Structures, Algorithms',
            'Python, Machine Learning, TensorFlow',
            'Full Stack: React, Django, PostgreSQL',
            'Backend: Node.js, Express, PostgreSQL',
            'Mobile: Flutter, Kotlin',
            'Web: HTML, CSS, JavaScript, Bootstrap',
        ]

        self.stdout.write(self.style.WARNING('Creating 50 fake users...'))

        for i in range(1, 51):
            try:
                # Create username and password following the pattern: 22IF001, 22IF002, etc.
                username = f'22IF{i:03d}'
                password = f'{username}{username}'  # 22IF00122IF001, 22IF00222IF002, etc.
                email = f'{username}@college.edu'

                # Skip if user already exists
                if User.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User {username} already exists, skipping...')
                    )
                    continue

                # Create User
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                )

                # Update or create UserProfile
                profile = user.profile
                profile.middle_name = fake.first_name()
                profile.phone = fake.phone_number()[:15]
                profile.date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=25)
                profile.gender = random.choice(genders)
                profile.address = fake.address()
                profile.city = fake.city()
                profile.state = fake.state()
                profile.pincode = fake.postcode()[:10]

                # Education details
                profile.college_name = 'XYZ College of Engineering'
                profile.branch = random.choice(branches)
                profile.degree = 'B.Tech'
                profile.specialization = profile.branch
                profile.cgpa = round(random.uniform(6.5, 9.2), 2)
                profile.year_of_study = random.choice(years)
                profile.admission_year = random.randint(2020, 2023)
                profile.backlogs = random.randint(0, 3)
                profile.current_backlogs = random.randint(0, 2)

                # Professional details
                profile.skills = random.choice(skills_list)
                profile.github_username = fake.user_name()
                profile.linkedin_username = fake.user_name()
                profile.hackerrank_username = fake.user_name()
                profile.experience = f'{random.randint(0, 3)} years of experience in software development'
                profile.bio = fake.text(max_nb_chars=200)

                profile.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created user {i}: {username}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creating user {i}: {str(e)}')
                )
                continue

        self.stdout.write(
            self.style.SUCCESS(f'\n Successfully created {created_count} fake users!')
        )
