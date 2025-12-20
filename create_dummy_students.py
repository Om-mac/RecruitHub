#!/usr/bin/env python
"""
Script to create dummy student data
Usage: python manage.py shell < create_dummy_students.py
Or: python create_dummy_students.py (if run as standalone)
"""

import os
import django
from django.contrib.auth.models import User
from faker import Faker
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

from core.models import UserProfile

fake = Faker()

# Student data configuration
BRANCHES = {
    'CS': 'Computer Science',
    'IF': 'Information Technology',
    'EE': 'Electrical Engineering',
    'CE': 'Civil Engineering',
    'ME': 'Mechanical Engineering'
}

SKILLS_POOL = [
    'Python', 'Java', 'C++', 'JavaScript', 'React', 'Django',
    'Flask', 'SQL', 'Docker', 'Git', 'Linux', 'AWS',
    'HTML', 'CSS', 'MongoDB', 'Node.js', 'REST APIs',
    'Machine Learning', 'Data Science', 'Web Development'
]

COMPANIES = ['Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Adobe']

def generate_student_data():
    """Generate dummy student data"""
    admission_year = 2022
    students = []
    
    for branch_code, branch_name in BRANCHES.items():
        for sequence in range(1, 6):  # 5 students per branch
            sequence_str = f"{sequence:03d}"
            username = f"{admission_year}{branch_code}{sequence_str}"
            password = f"{username}{username}"  # Double the username
            
            # Generate dummy data
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{username}@college.edu"
            
            cgpa = round(random.uniform(6.5, 9.5), 2)
            backlogs = random.randint(0, 3)
            current_backlogs = random.randint(0, backlogs) if backlogs > 0 else 0
            
            # Random skills
            num_skills = random.randint(3, 7)
            skills = random.sample(SKILLS_POOL, num_skills)
            
            # GitHub username
            github_username = f"{first_name.lower()}-{last_name.lower()}-{sequence}"
            linkedin_username = f"{first_name.lower()}-{last_name.lower()}"
            hackerrank_username = f"{username.lower()}"
            
            student = {
                'username': username,
                'password': password,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'profile': {
                    'branch': branch_code,
                    'college_name': 'ABC Engineering College',
                    'degree': 'B.Tech',
                    'specialization': branch_name,
                    'cgpa': cgpa,
                    'year_of_study': '4',
                    'admission_year': admission_year,
                    'backlogs': backlogs,
                    'current_backlogs': current_backlogs,
                    'phone': fake.phone_number()[:15],
                    'city': fake.city(),
                    'state': 'Karnataka',
                    'pincode': '560001',
                    'gender': random.choice(['M', 'F', 'O']),
                    'date_of_birth': fake.date_of_birth(minimum_age=20, maximum_age=25),
                    'skills': ', '.join(skills),
                    'experience': f"Internship at {random.choice(COMPANIES)} (3 months)",
                    'bio': f"Passionate developer interested in {random.choice(skills)}",
                    'github_username': github_username,
                    'linkedin_username': linkedin_username,
                    'hackerrank_username': hackerrank_username,
                    'other_platforms': f"LeetCode: {username.lower()}, Codeforces: {username.lower()}",
                }
            }
            students.append(student)
    
    return students


def create_students():
    """Create student users and profiles"""
    students = generate_student_data()
    created_count = 0
    skipped_count = 0
    
    print("\n" + "="*60)
    print("Creating Dummy Student Data")
    print("="*60 + "\n")
    
    for student_data in students:
        try:
            # Check if user already exists
            if User.objects.filter(username=student_data['username']).exists():
                print(f"⏭️  Skipped: {student_data['username']} (already exists)")
                skipped_count += 1
                continue
            
            # Create user
            user = User.objects.create_user(
                username=student_data['username'],
                email=student_data['email'],
                password=student_data['password'],
                first_name=student_data['first_name'],
                last_name=student_data['last_name']
            )
            
            # Create or update profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Update profile with all data
            for key, value in student_data['profile'].items():
                setattr(profile, key, value)
            profile.save()
            
            print(f"✅ Created: {student_data['username']} | {student_data['first_name']} {student_data['last_name']} | CGPA: {student_data['profile']['cgpa']} | Branch: {student_data['profile']['branch']}")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Error creating {student_data['username']}: {str(e)}")
            skipped_count += 1
    
    print("\n" + "="*60)
    print(f"Summary:")
    print(f"✅ Created: {created_count} students")
    print(f"⏭️  Skipped: {skipped_count} students")
    print(f"📊 Total: {len(students)} students expected")
    print("="*60 + "\n")
    
    # Print login credentials
    print("Sample Login Credentials:")
    print("-" * 60)
    for i, student in enumerate(students[:5]):
        print(f"Username: {student['username']} | Password: {student['password']}")
    print("... and more")
    print("-" * 60 + "\n")


if __name__ == '__main__':
    create_students()
